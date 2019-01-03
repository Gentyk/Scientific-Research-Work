import csv
import numpy as np
from datetime import datetime, timedelta

from analyse.models import Log
from work_files.analys import WIDTH, HEIGHT

PERIOD = 30
CLICKS = 20
COEFFICIENT = 1 / CLICKS

class CreateVectors(object):
    def __init__(self, name):
        self.user = name
        self.finish_time = None
        self.urls = []
        self.domains = []
        self.url_maps = {}
        self.domain_maps = {}

    def run(self, bad_users):
        # выкачиваем данные характерные именно для пользователя владельца из его отчета
        path = '.\\users\\vnames.csv'
        self.up_data()

        # выкачиваем карты кликов всех пользователей, которые соответствуют урлам и доменам владельца
        mass = [self.user] + bad_users
        for i in mass:
            map1, map2 = self.get_maps(i)
            self.url_maps[i] = map1.copy()
            self.domain_maps[i] = map2.copy()

        # пишем в файл вектора владельца
        print('user ' + self.user + ' start writing')
        self.write_in_csv(self.user, path)
        print('user ' + self.user + ' success writing')

        # пишем ветора для остальных
        for i in bad_users:
            print('user ' + i + ' start writing')
            self.write_in_csv(i, path)
            print('user ' + i + ' success writing')

    def up_data(self):
        """
        Достаем данные специфичные для пользоваетля-владельца
        """
        r_dict = np.load('.\\users\\'+self.user+'_otch.npy').item()
        self.urls = r_dict['частые url']
        self.domains = r_dict['частые домены']

        self.url_bigrams = [k.split(', ') for k in r_dict['url биграммы']]
        self.dom_bigrams = [k.split(', ') for k in r_dict['domain биграммы']]
        self.url_trigrams = [k.split(', ') for k in r_dict['url триграммы']]
        self.dom_trigrams = [k.split(', ') for k in r_dict['domain триграммы']]

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
        objects = [i[0] for i in Log.objects.filter(username=name).only(type_obj).distinct(type_obj).values_list(type_obj)]
        names = [url for url in objects if url in self.urls]
        for url in names:
            outfile = ".\\users\\"+name+"\\"+type_obj+" "+name+str(self.urls.index(url) + 1) + ".npy"
            url_matrix[url] = np.load(outfile)

        # домены
        domain_matrix = {}
        type_obj = 'domain'
        objects = [i[0] for i in Log.objects.filter(username=name).only(type_obj).distinct(type_obj).values_list(type_obj)]
        names = [domain for domain in objects if domain in self.domains]
        for domain in names:
            outfile = ".\\users\\" + name + "\\" + type_obj + " " + name + str(self.domains.index(domain) + 1) + ".npy"
            domain_matrix[domain] = np.load(outfile)
        return url_matrix, domain_matrix

    def write_in_csv(self, name, path, training_period=None, num_file=None):
        """
        Записывает в csv вектора пользователя name за период PERIOD
        """
        log = Log.objects.filter(username=name)
        if training_period == None and num_file == None:
            # даные для тестирования и обучения вместе
            current_time = log.earliest('time').time
            self.finish_time = current_time + timedelta(days=PERIOD)
        elif num_file == 1:
            # обучение отдельно
            current_time = log.earliest('time').time
            self.finish_time = current_time + timedelta(days=training_period)
        elif num_file == 2:
            # тестирование отдельно
            current_time = log.earliest('time').time + timedelta(days=training_period)
            self.finish_time = log.earliest('time').time + timedelta(days=PERIOD)

        all_values = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).order_by('id').values()
        size = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).count()

        with open(path, 'a', newline='') as csvfile:
            flag = True
            old_day = current_time.day
            for ind in range(0, size - CLICKS, CLICKS):
                res = {'username': name}
                values = all_values[ind: ind+CLICKS]
                current_time = values[0]['time']

                # просто для удобства отслеживания записи дней
                if old_day != current_time.day:
                    print("!"+str(current_time))
                    old_day = current_time.day

                # день и время берем по медиане
                vector_times = [i['time'] for i in values]
                vector_times.sort()
                vector_time = vector_times[9]
                res['weekday'] = vector_time.weekday()
                res['daytime'] = vector_time.hour // 8

                # счиатаем, сколько раз был на частых урлах и доменах
                res['u'] = 0
                urls = [0.5 for i in range(len(self.urls))]
                domains = [0.5 for i in range(len(self.domains))]
                user_urls = [(i['id'], i['url']) for i in values]
                for i in user_urls:
                    if i[1] in self.urls:
                        urls[self.urls.index(i[1])] += COEFFICIENT
                        res['u'] += self.hit_ratio(i[0], 'url', i[1])
                for i in range(len(urls)):
                    res['u' + str(i)] = urls[i]
                res['d'] = 0
                user_domains = [(i['id'], i['domain']) for i in values]
                for i in user_domains:
                    if i[1] in self.domains:
                        domains[self.domains.index(i[1])] += COEFFICIENT
                        res['d'] += self.hit_ratio(i[0], 'domain', i[1])
                for i in range(len(domains)):
                    res['d' + str(i)] = domains[i]

                # если был факт старта компа
                start = 0
                deviation = 0
                starts = [i['start_computer'] for i in values]
                if any(starts):
                    times = [(i['time'], i['url']) for i in values]
                    for i in range(CLICKS):
                        if starts[i] and i+1<CLICKS and times[i+1][1]:
                            start += 1
                            deviation = (times[i+1][0] - times[i][0]).seconds
                res['start'] = start
                res['dev'] = deviation

                # проверяем наличие биграмм и триграмм
                url_bi = [0 for i in range(len(self.url_bigrams))]
                dom_bi = [0 for i in range(len(self.dom_bigrams))]
                url_tri = [0 for i in range(len(self.url_trigrams))]
                dom_tri = [0 for i in range(len(self.dom_trigrams))]
                url_and_dom = [(i['url'], i['domain']) for i in values]
                n = len(url_and_dom) - 1
                for i in range(n):
                    u = [url_and_dom[i][0], url_and_dom[i + 1][0]]
                    if u in self.url_bigrams:
                        url_bi[self.url_bigrams.index(u)] += 1

                    d = [url_and_dom[i][1], url_and_dom[i + 1][1]]
                    if d in self.dom_bigrams:
                        dom_bi[self.dom_bigrams.index(d)] += 1

                    if i+2 <= n:
                        u = [url_and_dom[i][0], url_and_dom[i + 1][0], url_and_dom[i + 2][0]]
                        if u in self.url_trigrams:
                            url_tri[self.url_trigrams.index(u)] += 1

                        d = [url_and_dom[i][1], url_and_dom[i + 1][1], url_and_dom[i + 2][1]]
                        if d in self.dom_trigrams:
                            dom_tri[self.dom_trigrams.index(d)] += 1
                for i in range(len(dom_bi)):
                    res['d_bi' + str(i)] = dom_bi[i]
                for i in range(len(dom_tri)):
                    res['d_tri' + str(i)] = dom_tri[i]

                if flag:
                    fieldnames = list(res.keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    flag = False

                writer.writerow(res)

    def hit_ratio(self, id, type_obj, obj):
        res = 0
        # находим текущию запись и регистрируем область клика
        cl = Log.objects.get(pk=id)
        if cl.start_computer:
            return 0
        c = [0 for i in range(6)]
        c[0] = cl.x_cursor_coordinates
        c[1] = cl.y_cursor_coordinates
        c[2] = cl.x1_window_coordinates
        c[4] = cl.y1_window_coordinates
        c[3] = cl.x2_window_coordinates
        c[5] = cl.y2_window_coordinates
        try:
            y_point = int((c[1] - c[4]) / ((c[5] - c[4]) / HEIGHT))
            if y_point == HEIGHT:
                y_point = HEIGHT - 1
            x_point = int((c[0] - c[2]) / ((c[3] - c[2]) / HEIGHT))
            if x_point == WIDTH:
                x_point = WIDTH - 1




            if type_obj == 'url':
                # проверяем наличие такого клика у пользователя-владельца
                matrix = self.url_maps[self.user][obj]
                n_clicks = matrix[x_point, y_point]
                if n_clicks:
                    sum = np.sum(matrix)
                    res = COEFFICIENT * 4 * n_clicks / sum
                # если нету, то смотрим у "плохих пользователей" и вычитаем значение
                else:
                    names = [i for i in self.url_maps.keys() if i != self.user]
                    mass = []
                    for name in names:
                        maps = self.url_maps[name]
                        if obj in maps:
                            matrix = maps[obj]
                            n_clicks = matrix[x_point, y_point]
                            if n_clicks:
                                sum = np.sum(matrix)
                                mass.append(-(COEFFICIENT * 4 * n_clicks / sum))
                    if mass:
                        res = min(mass)
                    # если никто до этого так не кликал, то 0
                    else:
                        res = 0

            if type_obj == 'domain':
                # проверяем наличие такого клика у пользователя-владельца
                matrix = self.domain_maps[self.user][obj]
                n_clicks = matrix[x_point, y_point]
                if n_clicks:
                    sum = np.sum(matrix)
                    res = COEFFICIENT * 4 * n_clicks / sum
                # если нету, то смотрим у "плохих пользователей" и вычитаем значение
                else:
                    names = [i for i in self.domain_maps.keys() if i != self.user]
                    mass = []
                    for name in names:
                        maps = self.domain_maps[name]
                        if obj in maps:
                            matrix = maps[obj]
                            n_clicks = matrix[x_point, y_point]
                            if n_clicks:
                                sum = np.sum(matrix)
                                mass.append(-(COEFFICIENT * 4 * n_clicks / sum))
                    if mass:
                        res = min(mass)
                    # если никто до этого так не кликал, то 0
                    else:
                        res = 0

            return res
        except Exception as e:
            print(e)
            print(cl.time)
            print(c)
            tt = input()
            return 0


















