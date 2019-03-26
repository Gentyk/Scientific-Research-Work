import csv
from datetime import timedelta
import json
import numpy as np
import random
import requests
import xlsxwriter
import vk_api

from analyse.models import Log, Teams, VectorsOneVersion

WIDTH = 7
HEIGHT = 5

class CreateVectorsDB(object):
    def __init__(self, data, names, collection):
        """
        :param data: (кол-во кликов для обучения/кол-во кликов всего)
        :param names: массив имен всех пользователей
        :param clicks: массив кол-ва кликов в векторе (5/15/30)
        :param day_parts: на сколько частей мы делим день
        :param team_name: имя команды
        """
        self.finish_time = None
        self.collection = collection
        self.team_name =collection.team
        self.period = data[1]   # количество данных за период обучения и тестирования
        self.training = data[0] # количество данных за период обучения
        self.names = names
        self.n_click = collection.clicks
        self.time_of_day = collection.number_parts_per_day

        self.urls = []
        self.domains = []
        self.url_maps = {}
        self.domain_maps = {}

        self.url_bigrams = []
        self.dom_bigrams = []
        self.url_trigrams = []
        self.dom_trigrams = []

        self.url_bigrams_user = {}
        self.dom_bigrams_user = {}
        self.url_trigrams_user = {}
        self.dom_trigrams_user = {}
        self.user_flag = {}

        self.run()

    def run(self):
        for name in self.names:
            self.user_flag[name] = False
            self.up_data_from_db(name)

        # обучающая выбока
        for i in self.names:
            print('user ' + i + ' start writing training data')
            self.create_vectors(i, type=1)
            print('user ' + i + ' success writing training data')

        # выборка для тестирования
        for i in self.names:
            print('user ' + i + ' start writing testing data')
            self.create_vectors(i, type=2)
            print('user ' + i + ' success writing testing data')

    def up_data_from_db(self, name):
        log = Teams.objects.filter(team=self.team_name).get(username=name)

        # частые объекты всех пользователей без повторений
        self.urls = list(set(self.urls + log.frequent_urls))
        self.domains = list(set(self.domains + log.frequent_domains))

        self.url_bigrams = list(set(self.url_bigrams + [tuple(k) for k in log.frequent_bi_urls]))
        self.dom_bigrams = list(set(self.dom_bigrams + [tuple(k) for k in log.frequent_bi_domains]))
        self.url_trigrams = list(set(self.url_trigrams + [tuple(k) for k in log.frequent_tri_urls]))
        self.dom_trigrams = list(set(self.dom_trigrams + [tuple(k) for k in log.frequent_tri_domains]))

    def create_vectors(self, name, type):
        size = 0
        log = Log.objects.filter(username=name)
        if type == 1:
            # обучение
            all_v = log.filter(thousand__lt=self.training)
            size = all_v.count()
        elif type == 2:
            # тестирование
            all_v = log.filter(thousand__gte=self.training).filter(thousand__lt=self.period)
            size = all_v.count()
        all_fields = ['click__domain__domain', 'click__domain__category', 'click__domain__type', 'click__url__url',
                      'click__time', 'x1_window_coordinates', 'x2_window_coordinates', 'x_cursor_coordinates',
                      'y1_window_coordinates', 'y2_window_coordinates', 'y_cursor_coordinates', 'start_computer']
        all_values = all_v.order_by('id').values(*all_fields)
        print(size)

        num = 0
        all_types = [i[0] for i in Log.objects.distinct('click__domain__type').values_list('click__domain__type')]
        all_categories = [i[0] for i in Log.objects.distinct('click__domain__category').values_list('click__domain__category')]
        for ind in range(0, size - self.n_click, self.n_click):
            num += 1
            res = {'collection': self.collection, 'username': name, 'type': type}
            values = all_values[ind: ind + self.n_click]

            # день и время суток
            vector_times = [i['click__time'] for i in values]
            res['day_parts'] = [0 for i in range(self.time_of_day)]
            res['days'] = [0 for i in range(7)]
            for i in vector_times:
                res['days'][i.weekday()] = 1
                res['day_parts'][i.hour // self.time_of_day] = 1

            # считаем, сколько раз был на частых урлах
            # заполняем для них карту кликов
            res['urls'] = [0 for i in range(len(self.urls))]
            res['url_maps'] = [[0 for i in range(WIDTH * HEIGHT + 1)] for j in range(len(self.urls))]
            urls_repeat_pause = [[] for i in range(len(self.urls))]
            current_url = None
            current_url_time = None
            for i in values:
                if i['click__url__url'] in self.urls:
                    res['urls'][self.urls.index(i['click__url__url'])] += 1

                    # учитываем паузы, когда пользователь тыкается внутри
                    if current_url == i['click__url__url'] and current_url_time and i['click__time'] - current_url_time < timedelta(seconds=1800):
                        urls_repeat_pause[self.urls.index(i['click__url__url'])].append(i['click__time'] - current_url_time)
                        current_url_time = i['click__time']
                    else:
                        current_url = i['click__url__url']
                        current_url_time = i['click__time']

                    x, y = self.point(i)
                    if x and y:
                        res['url_maps'][self.urls.index(i['click__url__url'])][y * WIDTH + x] += 1

            res['url_freq_pause'] = []
            for i in range(len(self.urls)):
                if urls_repeat_pause[i]:
                    res['url_freq_pause'].append(sum([i.seconds for i in urls_repeat_pause[i]]) / len(urls_repeat_pause[i]))
                else:
                    res['url_freq_pause'].append(0)

            # считаем, сколько раз был на частых доменах
            # заполняем для них карту кликов
            res['domains'] = [0 for i in range(len(self.domains))]
            res['domain_maps'] = [[0 for i in range(WIDTH * HEIGHT + 1)] for j in range(len(self.domains))]

            domain_repeat_pause = [[] for i in range(len(self.domains))]
            current_domain = None
            current_domain_time = None
            for i in values:
                if i['click__domain__domain'] in self.domains:
                    res['domains'][self.domains.index(i['click__domain__domain'])] += 1

                    # учитываем паузы, когда пользователь тыкается внутри
                    if current_domain == i['click__domain__domain'] and current_domain_time and i['click__time'] - current_domain_time < timedelta(seconds=1800):
                        domain_repeat_pause[self.domains.index(i['click__domain__domain'])].append(i['click__time'] - current_domain_time)
                        current_domain_time = i['click__time']
                    else:
                        current_domain = i['click__domain__domain']
                        current_domain_time = i['click__time']

                    x, y = self.point(i)
                    if x and y:
                        res['domain_maps'][self.domains.index(i['click__domain__domain'])][y * WIDTH + x] += 1

            res['dom_freq_pause'] = []
            for i in range(len(self.domains)):
                if domain_repeat_pause[i]:
                    res['dom_freq_pause'].append(sum([i.seconds for i in domain_repeat_pause[i]]) / len(domain_repeat_pause[i]))
                else:
                    res['dom_freq_pause'].append(0)

            # паузы (средняя) - которая менее 5 мин
            times = [i['click__time'] for i in values]
            pauses = [abs(times[i+1]-times[i]).seconds for i in range(len(times)-1)
                      if abs(times[i+1]-times[i]) < timedelta(seconds=300)]
            pauses2 = [abs(times[i+1]-times[i]).seconds for i in range(len(times)-1)
                      if abs(times[i+1]-times[i]) >= timedelta(seconds=300) and abs(times[i+1]-times[i]) < timedelta(seconds=600)]
            pauses3 = [abs(times[i+1]-times[i]).seconds for i in range(len(times)-1)
                      if abs(times[i+1]-times[i]) >= timedelta(seconds=600)]
            res['middle_pause'] = sum(pauses) / len(pauses)
            res['middle_pause2'] = sum(pauses2) / len(pauses)
            res['middle_pause3'] = sum(pauses3) / len(pauses)
            res['quantity_middle_pause'] = len(pauses)
            res['quantity_middle_pause2'] = len(pauses2)
            res['quantity_middle_pause3'] = len(pauses3)

            # если был факт старта компа
            start_pause = 0
            starts = [i['start_computer'] for i in values]
            if any(starts):
                times = [(i['click__time'], i['click__url__url']) for i in values]
                for i in range(self.n_click):
                    if starts[i] and i + 1 < self.n_click and times[i + 1][1]:
                        start_pause = (times[i + 1][0] - times[i][0]).seconds
            res['start_comp_pause'] = start_pause

            # проверяем наличие биграмм и триграмм
            res['url_bi'] = [0 for i in range(len(self.url_bigrams))]
            url_bi_pauses = [[] for i in range(len(self.url_bigrams))]
            res['dom_bi'] = [0 for i in range(len(self.dom_bigrams))]
            dom_bi_pauses = [[] for i in range(len(self.dom_bigrams))]
            res['url_tri'] = [0 for i in range(len(self.url_trigrams))]
            url_tri_pauses = [[] for i in range(len(self.url_trigrams))]
            res['dom_tri'] = [0 for i in range(len(self.dom_trigrams))]
            dom_tri_pauses = [[] for i in range(len(self.dom_trigrams))]

            n = len(values) - 1
            for i in range(n):
                # биграммы url и их паузы
                u = (values[i]['click__url__url'], values[i + 1]['click__url__url'])
                if u in self.url_bigrams:
                    res['url_bi'][self.url_bigrams.index(u)] += 1
                    pause = abs(values[i + 1]['click__time'] - values[i]['click__time']).seconds
                    if pause < 29 * 60:
                        url_bi_pauses[self.url_bigrams.index(u)].append(pause)

                # биграммы домeнов и их паузы
                d = (values[i]['click__domain__domain'], values[i + 1]['click__domain__domain'])
                if d in self.dom_bigrams:
                    res['dom_bi'][self.dom_bigrams.index(d)] += 1
                    pause = abs(values[i + 1]['click__time'] - values[i]['click__time']).seconds
                    if pause < 29 * 60:
                        dom_bi_pauses[self.dom_bigrams.index(d)].append(pause)

                if i + 2 <= n:
                    # триграммы url и их паузы
                    u = (values[i]['click__url__url'], values[i + 1]['click__url__url'], values[i + 2]['click__url__url'])
                    if u in self.url_trigrams:
                        res['url_tri'][self.url_trigrams.index(u)] += 1
                        pause = abs(values[i + 2]['click__time'] - values[i]['click__time']).seconds
                        if pause < 29 * 60:
                            url_tri_pauses[self.url_trigrams.index(u)].append(pause)

                    # триграммы доменов и их паузы
                    d = (values[i]['click__domain__domain'], values[i + 1]['click__domain__domain'], values[i + 1]['click__domain__domain'])
                    if d in self.dom_trigrams:
                        res['dom_tri'][self.dom_trigrams.index(d)] += 1
                        pause = abs(values[i + 2]['click__time'] - values[i]['click__time']).seconds
                        if pause < 29 * 60:
                            dom_tri_pauses[self.dom_trigrams.index(d)].append(pause)

            res['url_bi_pauses'] = []
            res['url_tri_pauses'] = []
            res['dom_bi_pauses'] = []
            res['dom_tri_pauses'] = []
            for i in range(len(self.url_bigrams)):
                res['url_bi_pauses'].append(self.pause(url_bi_pauses[i]))
            for i in range(len(self.url_trigrams)):
                res['url_tri_pauses'].append(self.pause(url_tri_pauses[i]))
            for i in range(len(self.dom_bigrams)):
                res['dom_bi_pauses'].append(self.pause(dom_bi_pauses[i]))
            for i in range(len(self.dom_trigrams)):
                res['dom_tri_pauses'].append(self.pause(dom_tri_pauses[i]))

            res.update(self.get_info('domain_type', 'click__domain__type', all_types,values))
            res.update(self.get_info('domain_categories', 'click__domain__category', all_categories, values))

            new = VectorsOneVersion.objects.create(**res)
            new.save()
        #print(num)

    def get_info(self, field_name, type_perm, all_type_objs, values):
        res = {field_name: []}
        for i in range(len(all_type_objs)):
            res[field_name].append(0)
        for i in values:
            res[field_name][all_type_objs.index(i[type_perm])] += 1
        return res

    def point(self, obj):
        """
        Возвращаем координаты области, в которой произошел клик
        """
        xcc = obj['x_cursor_coordinates']
        ycc = obj['y_cursor_coordinates']
        x1wc = obj['x1_window_coordinates']
        x2wc = obj['x2_window_coordinates']
        y1wc = obj['y1_window_coordinates']
        y2wc = obj['y2_window_coordinates']

        try:
            y_point = int(abs(ycc - y1wc) / (abs(y2wc - y1wc) / HEIGHT))
            if y_point == HEIGHT:
                y_point = HEIGHT - 1
            x_point = int(abs(xcc - x1wc) / (abs(x2wc - x1wc) / HEIGHT))
            if x_point == WIDTH:
                x_point = WIDTH - 1
            # если клик за пределами окна, то тоже стоит запонить
            if x_point > WIDTH or x_point < 0 or y_point > HEIGHT or x_point < 0:
                return 0, HEIGHT
            return x_point, y_point
        except:
            return None, None

    def pause(self, mass):
        """
        Возвращает паузу из массива в нужном формате
        """
        if not mass:
            return 0
        elif len(mass) == 1:
            return mass[0]
        else:
            return sum(mass) / len(mass)