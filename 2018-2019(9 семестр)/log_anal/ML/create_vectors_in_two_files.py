import csv
from datetime import datetime, timedelta
import numpy as np
import xlsxwriter

from analyse.models import Log
from ML import ML
from work_files import analys

PERIOD = 60
CLICKS = 5
COEFFICIENT = 1 / CLICKS
TRAINING = 45
WIDTH = 7
HEIGHT = 5


class CreateVectorsApart(object):
    """
    Создаем вектора для классификации. Каждый вектор содечжит n=CLICKS кликов. Вектор содержит следующие столбцы:
    - имя (str)
    - день недели (int [0,6])
    - время клика (день разделен на 8 частей) (int [0,7])
    - средняя пауза в секундах ()
    - частые url всех пользователей (int [0, CLICKS])
    - частые домены всех пользователей (int [0, CLICKS])
    -! для каждого частого url и домена есть WIDTH * HEIGHT столбцов, которые показывают сколько кликов в эту область (int [0, CLICKS])
    - частые биграммы всех пользователей (int [0, CLICKS-1])
    -! для каждой частой биграммы считаем паузу. Если несколько, то среднюю среди пауз.
    - частые триграммы всех пользователей (int [0, CLICKS-2])
    -! для каждой частой триграммы считаем паузу. Если несколько, то среднюю среди пауз.
    """
    def __init__(self):
        self.finish_time = None
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

    def run(self, mode = 'normal'):
        mass = ['bv', 'ro', 'ys', 'mk', 'dy']#[name[0] for name in Log.objects.only('username').distinct('username').values_list('username')]

        # иногда надо проверить обучающую выборку
        if mode == 'analysis':
            for name in mass:
                self.up_data(name, mode)
            for i in mass:
                print('user ' + i + ' start writing training data')
                train_vectors = self.create_vectors_analyse(i)
                print('user ' + i + ' success writing training data')

        # обычный режим
        else:
            X_train = []
            Y_train = []
            X_test = []
            Y_test = []

            # обучающая выбока
            for i in mass:
                print('user ' + i + ' start writing training data')
                train_vectors = self.create_vectors(i, num_file=1)
                print('user ' + i + ' success writing training data')
                X_train += train_vectors[:]
                Y_train += [i for j in range(len(train_vectors))]

            # выборка для тестирования
            for i in mass:
                print('user ' + i + ' start writing testing data')
                test_vectors = self.create_vectors(i, num_file=2)
                print(test_vectors[0])
                print('user ' + i + ' success writing testing data')
                X_test += test_vectors[:]
                Y_test += [i for j in range(len(test_vectors))]

            # запускаем МО
            ML.ml(X_train, Y_train, X_test, Y_test, mass)

    def up_data(self, name, mode=None):
        """
        Достаем данные специфичные для пользоваетля-владельца
        """
        r_dict = np.load('.\\users\\' + name + '_otch.npy').item()

        # частые объекты всех пользователей без повторений
        self.urls = list(set(self.urls + r_dict['частые url']))
        self.domains = list(set(self.domains + r_dict['частые домены']))

        self.url_bigrams = list(set(self.url_bigrams + [tuple(k.split(', ')) for k in r_dict['url биграммы']]))
        self.dom_bigrams = list(set(self.dom_bigrams + [tuple(k.split(', ')) for k in r_dict['domain биграммы']]))
        self.url_trigrams = list(set(self.url_trigrams + [tuple(k.split(', ')) for k in r_dict['url триграммы']]))
        self.dom_trigrams = list(set(self.dom_trigrams + [tuple(k.split(', ')) for k in r_dict['domain триграммы']]))

        if mode:
            self.url_bigrams_user[name] = [tuple(k.split(', ')) for k in r_dict['url биграммы']]
            self.dom_bigrams_user[name] = [tuple(k.split(', ')) for k in r_dict['domain биграммы']]
            self.url_trigrams_user[name] = [tuple(k.split(', ')) for k in r_dict['url триграммы']]
            self.dom_trigrams_user[name] = [tuple(k.split(', ')) for k in r_dict['domain триграммы']]

    def get_maps(self, name):
        """
        Получаем карты кликов доменов и урлов в виде словарей. Например:
            {
                url1 : <карты кликов, соответсвующая url1>:;
                ...
            }

        """
        # урлы
        url_matrix = {}
        type_obj = 'url'
        objects = [i[0] for i in
                   Log.objects.filter(username=name).only(type_obj).distinct(type_obj).values_list(type_obj)]
        names = [url for url in objects if url in self.urls]
        for url in names:
            outfile = ".\\users\\" + name + "\\" + type_obj + " " + name + str(self.urls.index(url) + 1) + ".npy"
            url_matrix[url] = np.load(outfile)

        # домены
        domain_matrix = {}
        type_obj = 'domain'
        objects = [i[0] for i in
                   Log.objects.filter(username=name).only(type_obj).distinct(type_obj).values_list(type_obj)]
        names = [domain for domain in objects if domain in self.domains]
        for domain in names:
            outfile = ".\\users\\" + name + "\\" + type_obj + " " + name + str(self.domains.index(domain) + 1) + ".npy"
            domain_matrix[domain] = np.load(outfile)
        return url_matrix, domain_matrix

    def create_vectors(self, name, num_file=None):
        result = []
        log = Log.objects.filter(username=name)
        if num_file == 1:
            # обучение
            current_time = log.earliest('time').time
            self.finish_time = current_time + timedelta(days=TRAINING)
        elif num_file == 2:
            # тестирование
            current_time = log.earliest('time').time + timedelta(days=TRAINING)
            self.finish_time = log.earliest('time').time + timedelta(days=PERIOD)
            print(current_time)
            print(self.finish_time)

        all_values = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).order_by('id').values()
        size = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).count()
        print(size)
        old_day = current_time.day
        for ind in range(0, size - CLICKS, CLICKS):
            res = {}
            values = all_values[ind: ind + CLICKS]
            current_time = values[0]['time']

            # просто для удобства отслеживания записи дней
            if old_day != current_time.day:
                print("!" + str(current_time))
                old_day = current_time.day

            # день и время берем по медиане
            vector_times = [i['time'] for i in values]
            vector_times.sort()
            vector_time = vector_times[len(values) // 2]
            res['weekday'] = vector_time.weekday()
            res['daytime'] = vector_time.hour // 8

            # счиатаем, сколько раз был на частых урлах и доменах
            # заполняем для них карту кликов
            urls = [0 for i in range(len(self.urls))]
            urls_map = [[0 for i in range(WIDTH * HEIGHT)] for j in range(len(self.urls))]
            domains = [0 for i in range(len(self.domains))]
            domains_map = [[0 for i in range(WIDTH * HEIGHT)] for j in range(len(self.domains))]
            for i in values:
                if i['url'] in self.urls:
                    urls[self.urls.index(i['url'])] += 1#COEFFICIENT
                    x, y = self.point(i)
                    if x and y:
                            urls_map[self.urls.index(i['url'])][y * WIDTH + x] += 1
            for i in range(len(urls)):
                res['u' + str(i)] = urls[i]
            i = 0
            for map in urls_map:
                for j in map:
                    res['u_map' + str(i)] = j
                    i += 1

            for i in values:
                if i['domain'] in self.domains:
                    domains[self.domains.index(i['domain'])] += 1#COEFFICIENT
                    x, y = self.point(i)
                    if x and y:
                        domains_map[self.domains.index(i['domain'])][y * WIDTH + x] += 1
            for i in range(len(domains)):
                res['d' + str(i)] = domains[i]
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

            # если был факт старта компа
            start = 0
            deviation = 0
            starts = [i['start_computer'] for i in values]
            if any(starts):
                times = [(i['time'], i['url']) for i in values]
                for i in range(CLICKS):
                    if starts[i] and i + 1 < CLICKS and times[i + 1][1]:
                        start += 1
                        deviation = (times[i + 1][0] - times[i][0]).seconds
            res['start'] = start
            res['dev'] = deviation

            # проверяем наличие биграмм и триграмм
            url_bi = [0 for i in range(len(self.url_bigrams))]
            url_bi_pauses = [[] for i in range(len(self.url_bigrams))]
            dom_bi = [0 for i in range(len(self.dom_bigrams))]
            dom_bi_pauses = [[] for i in range(len(self.dom_bigrams))]
            url_tri = [0 for i in range(len(self.url_trigrams))]
            dom_tri = [0 for i in range(len(self.dom_trigrams))]

            n = len(values) - 1
            for i in range(n):
                u = (values[i]['url'], values[i + 1]['url'])
                if u in self.url_bigrams:
                    url_bi[self.url_bigrams.index(u)] += 1

                    pause = abs(values[i + 1]['time'] - values[i]['time']).seconds
                    if pause < 29 * 60:
                        url_bi_pauses[self.url_bigrams.index(u)].append(pause)

                d = (values[i]['domain'], values[i + 1]['domain'])
                if d in self.dom_bigrams:
                    dom_bi[self.dom_bigrams.index(d)] += 1

                if i + 2 <= n:
                    u = (values[i]['url'], values[i + 1]['url'], values[i + 2]['url'])
                    if u in self.url_trigrams:
                        url_tri[self.url_trigrams.index(u)] += 1

                    d = (values[i]['domain'], values[i + 1]['domain'], values[i + 1]['domain'])
                    if d in self.dom_trigrams:
                        dom_tri[self.dom_trigrams.index(d)] += 1

            for i in range(len(dom_bi)):
                res['d_bi' + str(i)] = dom_bi[i]
            for i in range(len(dom_tri)):
                res['d_tri' + str(i)] = dom_tri[i]
            result.append(list(res.values()))

        return result

    def point(self, obj):
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
            if x_point > WIDTH or x_point < 0 or y_point > HEIGHT or x_point < 0:
                return None, None
            return x_point, y_point
        except:
            return None, None


    def analysis(self):
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
        self.finish_time = current_time + timedelta(days=TRAINING)

        all_values = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).order_by('id').values()
        size = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).count()

        furl_bi = [0 for i in range(len(self.url_bigrams_user[name]))]
        fdom_bi = [0 for i in range(len(self.dom_bigrams_user[name]))]
        furl_tri = [0 for i in range(len(self.url_trigrams_user[name]))]
        fdom_tri = [0 for i in range(len(self.dom_trigrams_user[name]))]


        for ind in range(0, size - CLICKS, CLICKS):
            res = {}
            values = all_values[ind: ind + CLICKS]

            # проверяем наличие биграмм и триграмм
            url_bi = [0 for i in range(len(self.url_bigrams_user[name]))]
            dom_bi = [0 for i in range(len(self.dom_bigrams_user[name]))]
            url_tri = [0 for i in range(len(self.url_trigrams_user[name]))]
            dom_tri = [0 for i in range(len(self.dom_trigrams_user[name]))]

            url_and_dom = [(i['url'], i['domain']) for i in values]
            n = len(url_and_dom) - 1
            for i in range(n):
                u = (url_and_dom[i][0], url_and_dom[i + 1][0])
                # if u in self.url_bigrams:
                #     url_bi[self.url_bigrams.index(u)] += 1
                if u in self.url_bigrams_user[name]:
                    furl_bi[self.url_bigrams_user[name].index(u)] = True

                d = (url_and_dom[i][1], url_and_dom[i + 1][1])
                # if d in self.dom_bigrams:
                #     dom_bi[self.dom_bigrams.index(d)] += 1
                if d in self.dom_bigrams_user[name]:
                    fdom_bi[self.dom_bigrams_user[name].index(d)] = True

                if i + 2 <= n:
                    u = (url_and_dom[i][0], url_and_dom[i + 1][0], url_and_dom[i + 2][0])
                    # if u in self.url_trigrams:
                        # url_tri[self.url_trigrams.index(u)] += 1
                    if u in self.url_trigrams_user[name]:
                        furl_tri[self.url_trigrams_user[name].index(u)] = True

                    d = (url_and_dom[i][1], url_and_dom[i + 1][1], url_and_dom[i + 2][1])
                    # if d in self.dom_trigrams:
                    #     dom_tri[self.dom_trigrams.index(d)] += 1
                    if d in self.dom_trigrams_user[name]:
                        fdom_tri[self.dom_trigrams_user[name].index(d)] = True

            # for i in range(len(dom_bi)):
            #     res['d_bi' + str(i)] = dom_bi[i]
            # for i in range(len(dom_tri)):
            #     res['d_tri' + str(i)] = dom_tri[i]
            result.append(list(res.values()))
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
        return result