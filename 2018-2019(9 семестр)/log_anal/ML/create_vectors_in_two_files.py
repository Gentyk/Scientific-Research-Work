import csv
from datetime import timedelta
import json
import numpy as np
import random
import requests
import xlsxwriter
import vk_api

from analyse.models import Log, Teams

WIDTH = 7
HEIGHT = 5


class CreateVectorsApart(object):
    """
    Создаем вектора для классификации. Каждый вектор содержит n=CLICKS кликов. Вектор содержит следующие столбцы:
    - имя (str)
    - день недели
    - время клика (день разделен на n частей)
    - средняя пауза в секундах ()
    - частые url всех пользователей (int [0, CLICKS])
    - частые домены всех пользователей (int [0, CLICKS])
    - для каждого частого url и домена есть WIDTH * HEIGHT столбцов, которые показывают сколько кликов в эту область (int [0, CLICKS])
    - частые биграммы всех пользователей (int [0, CLICKS-1])
    - для каждой частой биграммы считаем паузу. Если несколько, то среднюю среди пауз.
    - частые триграммы всех пользователей (int [0, CLICKS-2])
    - для каждой частой триграммы считаем паузу. Если несколько, то среднюю среди пауз.
    """
    def __init__(self, path, data, names, clicks, day_parts, permission, team_name, add_info_by_namedir=""):
        """
        :param data: (кол-во кликов для обучения/кол-во кликов всего)
        :param names: массив имен всех пользователей
        :param clicks: массив кол-ва кликов в векторе (5/15/30)
        :param day_parts: на сколько частей мы делим день
        :param permission: список признаков, которые мы хотим увидеть в векторе
        :param team_name: имя команды
        :param add_info_by_namedir: приписка к ф
        """
        self.finish_time = None
        self.permission = permission
        self.team_name = team_name
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

        self.period = data[1]   # количество данных за период обучения и тестирования
        self.training = data[0] # количество данных за период обучения
        self.names = names
        self.n_click = clicks
        self.time_of_day = day_parts
        self.path = path
        self.run()

    def run(self, mode = 'normal'):
        # иногда надо проверить обучающую выборку
        if mode == 'analysis':
            for name in self.names:
                self.up_data(name, mode)

            for i in self.names:
                print('user ' + i + ' start writing training data')
                self.create_vectors_analyse(i)
                print('user ' + i + ' success writing training data')

        # обычный режим
        else:
            for name in self.names:
                self.user_flag[name] = False
                self.up_data_from_db(name)

            path = self.path + "\\TRAINING.csv"
            with open(path, 'w', newline='') as csvfile:
                pass

            # обучающая выбока
            for i in self.names:
                print('user ' + i + ' start writing training data')
                self.create_vectors(i, num_file=1, path=path)
                print('user ' + i + ' success writing training data')


            path = self.path + "\\TESTING.csv"
            with open(path, 'w', newline='') as csvfile2:
                pass

            # выборка для тестирования
            for i in self.names:
                print('user ' + i + ' start writing testing data')
                self.create_vectors(i, num_file=2, path=path)
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

    def up_data_from_file(self, name, mode=None):
        """
        Достаем данные специфичные для пользоваетля-владельца
        """
        r_dict = np.load('.\\' + self.team_name[len(self.team_name)-1] + '_users\\' + name + str(self.training) + '_otch.npy').item()

        # частые объекты всех пользователей без повторений
        self.urls = list(set(self.urls + r_dict['частые url']))
        self.domains = list(set(self.domains + r_dict['частые домены']))

        self.url_bigrams = list(set(self.url_bigrams + [k for k in r_dict['url биграммы']]))
        self.dom_bigrams = list(set(self.dom_bigrams + [k for k in r_dict['domain биграммы']]))
        self.url_trigrams = list(set(self.url_trigrams + [k for k in r_dict['url триграммы']]))
        self.dom_trigrams = list(set(self.dom_trigrams + [k for k in r_dict['domain триграммы']]))

        if mode:
            self.url_bigrams_user[name] = [k for k in r_dict['url биграммы']]
            self.dom_bigrams_user[name] = [k for k in r_dict['domain биграммы']]
            self.url_trigrams_user[name] = [k for k in r_dict['url триграммы']]
            self.dom_trigrams_user[name] = [k for k in r_dict['domain триграммы']]


    def create_vectors(self, name, num_file=None, path=""):
        size = 0
        result_by_file = []
        log = Log.objects.filter(username=name).filter(start_computer=False)
        if num_file == 1:
            # обучение
            all_v = log.filter(thousand__lt=self.training)
            size = all_v.count()
            all_values = all_v.order_by('id').values()
        elif num_file == 2:
            # тестирование
            all_v = log.filter(thousand__gte=self.training).filter(thousand__lt=self.period)
            size = all_v.count()
            all_values = all_v.order_by('id').values()
        print(size)

        num = 0
        all_types = [i[0] for i in Log.objects.distinct('domain_type').values_list('domain_type')]
        all_categories = [i[0] for i in Log.objects.distinct('domain_category').values_list('domain_category')]
        for ind in range(0, size - self.n_click, self.n_click):
            num += 1
            res = {}
            res_by_file = {'username': name}
            values = all_values[ind: ind + self.n_click]

            # день и время берем по медиане
            vector_times = [i['time'] for i in values]
            days = [0 for i in range(7)]
            t = [0 for i in range(self.time_of_day)]
            for i in vector_times:
                days[i.weekday()] = 1
                t[i.hour // 8] = 1

            j = 0
            for i in days:
                res['weekday'+str(j)] = i
                j += 1

            j = 0
            for i in t:
                res['daytime' + str(j)] = i
                j += 1

            # считаем, сколько раз был на частых урлах
            # заполняем для них карту кликов
            urls = [0 for i in range(len(self.urls))]

            urls_map = [[0 for i in range(WIDTH * HEIGHT + 1)] for j in range(len(self.urls))]

            urls_repeat_pause = [[] for i in range(len(self.urls))]
            current_url = None
            current_url_time = None
            for i in values:
                if i['url'] in self.urls:
                    urls[self.urls.index(i['url'])] += 1

                    # учитываем паузы, когда пользователь тыкается внутри
                    if current_url == i['url'] and current_url_time and i['time'] - current_url_time < timedelta(seconds=1800):
                        urls_repeat_pause[self.urls.index(i['url'])].append(i['time'] - current_url_time)
                        current_url_time = i['time']
                    else:
                        current_url = i['url']
                        current_url_time = i['time']

                    x, y = self.point(i)
                    if x and y:
                            urls_map[self.urls.index(i['url'])][y * WIDTH + x] += 1
            for i in range(len(urls)):
                res['u' + str(i)] = urls[i]

            for i in range(len(urls)):
                if urls_repeat_pause[i] == []:
                    res['u_freq_pause' + str(i)] = 0
                else:
                    res['u_freq_pause' + str(i)] = sum([i.seconds for i in urls_repeat_pause[i]])/len(urls_repeat_pause[i])

            if 'url_maps' in self.permission:
                i = 0
                for map in urls_map:
                    for j in map:
                        res['u_map' + str(i)] = j
                        i += 1

            # считаем, сколько раз был на частых доменах
            # заполняем для них карту кликов
            if 'domain' in self.permission or 'domain_maps' in self.permission:
                domains = [0 for i in range(len(self.domains))]
                domains_map = [[0 for i in range(WIDTH * HEIGHT + 1)] for j in range(len(self.domains))]

                domain_repeat_pause = [[] for i in range(len(self.domains))]
                current_domain = None
                current_domain_time = None
                for i in values:
                    if i['domain'] in self.domains:
                        domains[self.domains.index(i['domain'])] += 1#COEFFICIENT

                        # учитываем паузы, когда пользователь тыкается внутри
                        if current_domain == i['domain'] and current_domain_time and i['time'] - current_domain_time < timedelta(seconds=1800):
                            domain_repeat_pause[self.domains.index(i['domain'])].append(i['time'] - current_domain_time)
                            current_domain_time = i['time']
                        else:
                            current_domain = i['domain']
                            current_domain_time = i['time']

                        x, y = self.point(i)
                        if x and y:
                            domains_map[self.domains.index(i['domain'])][y * WIDTH + x] += 1
            if 'domain' in self.permission:
                for i in range(len(domains)):
                    res['d' + str(i)] = domains[i]

                for i in range(len(domains)):
                    if domain_repeat_pause[i] == []:
                        res['dom_freq_pause' + str(i)] = 0
                    else:
                        try:
                            res['dom_freq_pause' + str(i)] = sum([i.seconds for i in domain_repeat_pause[i]])/len(domain_repeat_pause[i])
                        except:
                            res['dom_freq_pause' + str(i)] = 0
                            print(domain_repeat_pause[i])
                            cc = input()

            if 'domain_maps' in self.permission:
                i = 0
                for map in domains_map:
                    for j in map:
                        res['d_map' + str(i)] = j
                        i += 1


            # паузы (средняя) - которая менее 5 мин
            times = [i['time'] for i in values]
            pauses = [abs(times[i+1]-times[i]).seconds for i in range(len(times)-1)
                      if abs(times[i+1]-times[i]) < timedelta(seconds=300)]
            res['middle_pause'] = sum(pauses) / len(pauses)

            # # если был факт старта компа
            if 'start_comp' in self.permission:
                start = 0
                start_pause = 0
                starts = [i['start_computer'] for i in values]
                if any(starts):
                    times = [(i['time'], i['url']) for i in values]
                    for i in range(self.n_click):
                        if starts[i] and i + 1 < self.n_click and times[i + 1][1]:
                            start += 1
                            start_pause = (times[i + 1][0] - times[i][0]).seconds
                res['start'] = start
                res['start_pause'] = start_pause

            # проверяем наличие биграмм и триграмм
            url_bi = [0 for i in range(len(self.url_bigrams))]
            url_bi_pauses = [[] for i in range(len(self.url_bigrams))]
            dom_bi = [0 for i in range(len(self.dom_bigrams))]
            dom_bi_pauses = [[] for i in range(len(self.dom_bigrams))]
            url_tri = [0 for i in range(len(self.url_trigrams))]
            url_tri_pauses = [[] for i in range(len(self.url_trigrams))]
            dom_tri = [0 for i in range(len(self.dom_trigrams))]
            dom_tri_pauses = [[] for i in range(len(self.dom_trigrams))]

            n = len(values) - 1
            for i in range(n):
                # биграммы url и их паузы
                if 'url_bi' in self.permission or 'grams_pause' in self.permission:
                    u = (values[i]['url'], values[i + 1]['url'])
                    if u in self.url_bigrams:
                        url_bi[self.url_bigrams.index(u)] += 1
                        pause = abs(values[i + 1]['time'] - values[i]['time']).seconds
                        if pause < 29 * 60:
                            url_bi_pauses[self.url_bigrams.index(u)].append(pause)

                # биграммы домeнов и их паузы
                if 'dom_bi' in self.permission or 'grams_pause' in self.permission:
                    d = (values[i]['domain'], values[i + 1]['domain'])
                    if d in self.dom_bigrams:
                        dom_bi[self.dom_bigrams.index(d)] += 1
                        pause = abs(values[i + 1]['time'] - values[i]['time']).seconds
                        if pause < 29 * 60:
                            dom_bi_pauses[self.dom_bigrams.index(d)].append(pause)

                if i + 2 <= n:
                    # триграммы url и их паузы
                    if 'url_tri' in self.permission or 'grams_pause' in self.permission:
                        u = (values[i]['url'], values[i + 1]['url'], values[i + 2]['url'])
                        if u in self.url_trigrams:
                            url_tri[self.url_trigrams.index(u)] += 1
                            pause = abs(values[i + 2]['time'] - values[i]['time']).seconds
                            if pause < 29 * 60:
                                url_tri_pauses[self.url_trigrams.index(u)].append(pause)

                    # триграммы доменов и их паузы
                    if 'dom_tri' in self.permission or 'grams_pause' in self.permission:
                        d = (values[i]['domain'], values[i + 1]['domain'], values[i + 1]['domain'])
                        if d in self.dom_trigrams:
                            dom_tri[self.dom_trigrams.index(d)] += 1
                            pause = abs(values[i + 2]['time'] - values[i]['time']).seconds
                            if pause < 29 * 60:
                                dom_tri_pauses[self.dom_trigrams.index(d)].append(pause)

            if 'url_bi' in self.permission:
                for i in range(len(url_bi)):
                    res['url_bi' + str(i)] = url_bi[i]
            if 'url_tri' in self.permission:
                for i in range(len(url_tri)):
                    res['url_tri' + str(i)] = url_tri[i]
            if 'dom_bi' in self.permission:
                for i in range(len(dom_bi)):
                    res['d_bi' + str(i)] = dom_bi[i]
            if 'dom_tri' in self.permission:
                for i in range(len(dom_tri)):
                    res['d_tri' + str(i)] = dom_tri[i]
            if 'grams_pause' in self.permission:
                for i in range(len(url_bi)):
                    res['url_bi_pause' + str(i)] = self.pause(url_bi_pauses[i])
                for i in range(len(url_tri)):
                    res['url_tri_pause' + str(i)] = self.pause(url_tri_pauses[i])
                for i in range(len(dom_bi)):
                    res['dom_bi_pause' + str(i)] = self.pause(dom_bi_pauses[i])
                for i in range(len(dom_tri)):
                    res['dom_tri_pause' + str(i)] = self.pause(dom_tri_pauses[i])

            if 'domain_type' in self.permission:
                res.update(self.get_info('domain_type', all_types,values))
            if 'domain_category' in self.permission:
                res.update(self.get_info('domain_category', all_categories, values))


            res_by_file.update(res)
            result_by_file.append(res_by_file)
            if num >= 1000:
                self.write_in_csv(path, result_by_file)
                num = 0
                result_by_file = []
        if result_by_file:
            self.write_in_csv(path, result_by_file)

    def get_info(self, type_perm, all_type_objs, values):
        res = {}
        for i in range(len(all_type_objs)):
            res[type_perm + str(i)] = 0
        for i in values:
            res[type_perm + str(all_type_objs.index(i[type_perm]))] += 1
        return res

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

    def write_in_csv(self, path, vectors):
        """
        Записывает в csv вектора пользователя
        """
        fieldnames = list(vectors[0].keys())
        with open(path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for vector in vectors:
                writer.writerow(vector)

    def analysis(self):
        """
        Записывыет в таблицу эксель всех пользователь и сумму по всем полям.
        Получается очень наглядно и здорово)
        """
        mass = [name[0] for name in Log.objects.only('username').distinct('username').values_list('username')]
        r_dict = dict()
        for i in mass:
            r_dict[i] = np.load('.\\users\\' + i + '_otch.npy').item()

        result = []
        for name1 in mass:
            result += [["", name1], [""] + [k for k in r_dict[name1]]]
            for name2 in mass:
                if name1 != name2:
                    new = [name2]
                    for k, v in r_dict[name2].items():


                        if isinstance(v, list):
                            print(k)
                            print(v)
                            gg = len(set(v) & set(r_dict[name1][k])) // len(v)
                            print(gg)
                            new.append(gg)
                            #bb = input()

                        if isinstance(v, dict):
                            try:
                                print(k)
                                print(v)
                                gg = len(set(list(v.keys())) & set(list(r_dict[name1][k].keys()))) // len(
                                list(v.keys()))
                                print(gg)
                                new.append(gg)
                                #bb = input()
                            except:
                                print(k)
                                print(v)
                    result.append(new)
            result.append([""])

        workbook = xlsxwriter.Workbook('Expenses1.xlsx')
        worksheet = workbook.add_worksheet()
        row = 0
        col = 0

        # Iterate over the data and write it out row by row.
        for i in result:
            j = 0
            for ii in i:
                worksheet.write(row, col + j, ii)
                j += 1
            row += 1

        workbook.close()

    def create_vectors_analyse(self, name):
        """
        Проверка наличия биграмм и триграмм для каждого пользователя

        """
        result = []
        log = Log.objects.filter(username=name)
        # обучение
        current_time = log.earliest('time').time
        self.finish_time = current_time + timedelta(days=self.period)

        all_values = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).order_by('id').values()
        size = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).count()

        furl_bi = [0 for i in range(len(self.url_bigrams_user[name]))]
        fdom_bi = [0 for i in range(len(self.dom_bigrams_user[name]))]
        furl_tri = [0 for i in range(len(self.url_trigrams_user[name]))]
        fdom_tri = [0 for i in range(len(self.dom_trigrams_user[name]))]


        for ind in range(0, size - self.n_click):
            values = all_values[ind: ind + self.n_click]

            url_and_dom = [(i['url'], i['domain']) for i in values]
            n = len(url_and_dom) - 1
            for i in range(n):
                u = (url_and_dom[i][0], url_and_dom[i + 1][0])
                if u in self.url_bigrams_user[name]:
                    furl_bi[self.url_bigrams_user[name].index(u)] = True

                d = (url_and_dom[i][1], url_and_dom[i + 1][1])
                if d in self.dom_bigrams_user[name]:
                    fdom_bi[self.dom_bigrams_user[name].index(d)] = True

                if i + 2 <= n:
                    u = (url_and_dom[i][0], url_and_dom[i + 1][0], url_and_dom[i + 2][0])
                    if u in self.url_trigrams_user[name]:
                        furl_tri[self.url_trigrams_user[name].index(u)] = True

                    d = (url_and_dom[i][1], url_and_dom[i + 1][1], url_and_dom[i + 2][1])
                    if d in self.dom_trigrams_user[name]:
                        fdom_tri[self.dom_trigrams_user[name].index(d)] = True

        if not all(fdom_tri):
            print(name)
            print(fdom_tri)
            bb = input()
        if not all(furl_bi):
            print(name)
            print(furl_bi)
            bb = input()
        if not all(fdom_bi):
            print(name)

            print(fdom_bi)
            bb = input()
        if not all(furl_tri):
            print(name)

            print(furl_tri)
            bb = input()


    def send_vk_letter(self, text):
        session = requests.Session()
        with open('data.json', 'r') as f:
            auth = json.load(f)
        login, password = auth['phone'], auth['password']
        vk_session = vk_api.VkApi(login, password)
        try:
            vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            print(error_msg)
        vk = vk_session.get_api()
        vk.messages.send(
            user_id=auth['user_id'],
            message=text,
            random_id=random.randint(1,100)
        )
