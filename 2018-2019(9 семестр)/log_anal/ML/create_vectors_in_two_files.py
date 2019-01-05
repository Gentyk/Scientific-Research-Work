import csv
from datetime import datetime, timedelta
import numpy as np
import xlsxwriter

from analyse.models import Log
from ML import ML
from work_files.analys import WIDTH, HEIGHT

PERIOD = 30
CLICKS = 5
COEFFICIENT = 1 / CLICKS
TRAINING = int(PERIOD*0.7)


class CreateVectorsApart(object):
    """
    Просто вектор для классификации. Вклюает следующие столбцы:
    - имя
    - день недели
    - время клика (день разделен на 8 частей)
    - частые url всех пользователей
    - частые домены всех пользователей
    - частые биграммы всех пользователей
    - частые триграммы всех пользователей
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
        self.dom_trigrams_user = {}

    def run(self):
        X_train = []
        Y_train = []
        X_test = []
        Y_test = []

        mass = ['ys', 'bv']#[name[0] for name in Log.objects.only('username').distinct('username').values_list('username')]
        for name in mass:
            self.up_data(name)

        # print(len(self.urls))
        # print(len(self.domains))
        # print(len(self.url_maps))
        # print(len(self.domain_maps))
        #
        # print(len(self.url_bigrams))
        # print(len(self.dom_bigrams))
        # print(len(self.url_trigrams))
        # print(len(self.dom_trigrams))

        # выкачиваем карты кликов всех пользователей, которые соответствуют урлам и доменам владельца
        # for i in mass:
        #     map1, map2 = self.get_maps(i)
        #     self.url_maps[i] = map1.copy()
        #     self.domain_maps[i] = map2.copy()

        # обучающая выбока
        path = "TRAINING.csv"
        for i in mass:
            print('user ' + i + ' start writing training data')
            train_vectors = self.create_vectors(i, training_period=TRAINING, num_file=1)
            print('user ' + i + ' success writing training data')
            X_train += train_vectors[:]
            Y_train += [i for j in range(len(train_vectors))]

        # выборка для тестирования
        path = "TESTING.csv"
        for i in mass:
            print('user ' + i + ' start writing testing data')
            test_vectors = self.create_vectors(i, training_period=TRAINING, num_file=2)
            print('user ' + i + ' success writing testing data')
            X_test += test_vectors[:]
            Y_test += [i for j in range(len(test_vectors))]

        ML.ml(X_train, Y_train, X_test, Y_test, mass)

    def up_data(self, name):
        """
        Достаем данные специфичные для пользоваетля-владельца
        """
        r_dict = np.load('.\\users\\' + name + '_otch.npy').item()

        # частые объекты всех пользователей без повторений
        self.urls = list(set(self.urls + r_dict['частые url']))
        self.domains = list(set(self.domains + r_dict['частые домены']))

        self.url_bigrams = list(set(self.url_bigrams + [tuple(k.split(', ')) for k in r_dict['url биграммы']]))
        self.dom_bigrams = list(set(self.dom_bigrams + [tuple(k.split(', ')) for k in r_dict['domain биграммы']]))
        # self.url_trigrams = list(set(self.url_trigrams + [tuple(k.split(', ')) for k in r_dict['url триграммы']]))
        # self.dom_trigrams = list(set(self.dom_trigrams + [tuple(k.split(', ')) for k in r_dict['domain триграммы']]))
        # self.dom_trigrams_user[name] = [tuple(k.split(', ')) for k in r_dict['domain триграммы']]

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

    def create_vectors(self, name, training_period=None, num_file=None):
        result = []
        log = Log.objects.filter(username=name)
        if num_file == 1:
            # обучение
            current_time = log.earliest('time').time
            self.finish_time = current_time + timedelta(days=training_period)
        elif num_file == 2:
            # тестирование
            current_time = log.earliest('time').time + timedelta(days=training_period)
            self.finish_time = log.earliest('time').time + timedelta(days=PERIOD)

        all_values = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).order_by('id').values()
        size = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).count()

        old_day = current_time.day
        for ind in range(0, size - CLICKS, CLICKS):
            res = {'username': name}
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
            urls = [0 for i in range(len(self.urls))]
            domains = [0 for i in range(len(self.domains))]
            user_urls = [(i['id'], i['url']) for i in values]
            for i in user_urls:
                if i[1] in self.urls:
                    urls[self.urls.index(i[1])] += 1#COEFFICIENT
            for i in range(len(urls)):
                res['u' + str(i)] = urls[i]
            user_domains = [(i['id'], i['domain']) for i in values]
            for i in user_domains:
                if i[1] in self.domains:
                    domains[self.domains.index(i[1])] += 1#COEFFICIENT
            for i in range(len(domains)):
                res['d' + str(i)] = domains[i]

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
            dom_bi = [0 for i in range(len(self.dom_bigrams))]
            # url_tri = [0 for i in range(len(self.url_trigrams))]
            # dom_tri = [0 for i in range(len(self.dom_trigrams))]

            url_and_dom = [(i['url'], i['domain']) for i in values]
            n = len(url_and_dom) - 1
            for i in range(n):
                u = (url_and_dom[i][0], url_and_dom[i + 1][0])
                if u in self.url_bigrams:
                    url_bi[self.url_bigrams.index(u)] += 1

                d = (url_and_dom[i][1], url_and_dom[i + 1][1])
                if d in self.dom_bigrams:
                    dom_bi[self.dom_bigrams.index(d)] += 1

                # if i + 2 <= n:
                #     u = (url_and_dom[i][0], url_and_dom[i + 1][0], url_and_dom[i + 2][0])
                #     if u in self.url_trigrams:
                #         url_tri[self.url_trigrams.index(u)] += 1
                #
                #     d = (url_and_dom[i][1], url_and_dom[i + 1][1], url_and_dom[i + 2][1])
                #     if d in self.dom_trigrams:
                #         dom_tri[self.dom_trigrams.index(d)] += 1
                #     if d in self.dom_trigrams_user[name]:
                #         fuck[self.dom_trigrams_user[name].index(d)] = True



            for i in range(len(dom_bi)):
                res['d_bi' + str(i)] = dom_bi[i]
            # for i in range(len(dom_tri)):
            #     res['d_tri' + str(i)] = dom_tri[i]
            result.append(res)
        # if not all(fuck):
        #     print(name)
        #     for i in self.dom_trigrams_user[name]:
        #         print(i)
        #     print(fuck)
        #     bb = input()
        return result


    def write_in_csv(self, path, vectors):
        """
        Записывает в csv вектора пользователя
        """
        fieldnames = list(vectors[0].keys())
        with open(path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for vector in vectors:
                writer.writerow(vector)

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




