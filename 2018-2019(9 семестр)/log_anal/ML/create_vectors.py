import csv
import numpy as np
from datetime import datetime, timedelta

from analyse.models import Log
from work_files.analys import WIDTH, HEIGHT

from ML import ML

PERIOD = 30
TRAINING = int(PERIOD*0.7)
CLICKS = 20
COEFFICIENT = 1 / CLICKS

class CreateVectors(object):
    """
    Создадим вектор для классификации.
    Один клик - один вестор
    Составные части:
    - имя
    - день недели
    - часть дня
    - область клика по Х
    - область клика по У
    - домен
    - урл
    - добавили список частых урлов и доменов
    """
    def __init__(self):
        self.finish_time = None
        self.urls = []
        self.domains = []
        self.fr_urls = []
        self.fr_domains = []


    def run(self):
        train_vectors = []
        test_vectors = []
        mass = ['ys', 'bv']#[name[0] for name in Log.objects.only('username').distinct('username').values_list('username')]
        for name in mass:
            self.up_data(name)

        # обучающая выбока
        path = "siTRAINING.csv"
        for i in mass:
            print('user ' + i + ' start writing training data')
            train_vectors += self.create_vectors(i, training_period=TRAINING, num_file=1)
            print('user ' + i + ' success writing training data')
        self.write_in_csv(path, train_vectors)

        # выборка для тестирования
        path = "siTESTING.csv"
        for i in mass:
            print('user ' + i + ' start writing testing data')
            test_vectors += self.create_vectors(i, training_period=TRAINING, num_file=2)
            print('user ' + i + ' success writing testing data')
        self.write_in_csv(path, test_vectors)
        ML.ml(mass, 'si')

    def up_data(self, name):
        """
        Достаем данные специфичные для пользоваетля-владельца
        """
        r_dict = np.load('.\\users\\'+ name +'_otch.npy').item()
        # частые объекты всех пользователей без повторений
        self.fr_urls = list(set(self.fr_urls + r_dict['частые url']))
        self.fr_domains = list(set(self.fr_domains + r_dict['частые домены']))

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

    def create_vectors(self, name, training_period=None, num_file=None):
        log = Log.objects.filter(username=name)
        if num_file == 1:
            # обучение отдельно
            current_time = log.earliest('time').time
            self.finish_time = current_time + timedelta(days=training_period)
        elif num_file == 2:
            # тестирование отдельно
            current_time = log.earliest('time').time + timedelta(days=training_period)
            self.finish_time = log.earliest('time').time + timedelta(days=PERIOD)

        all_values = log.filter(time__lt=self.finish_time).filter(time__gte=current_time).order_by('id').values()
        result = []
        old_day = current_time.day
        for value in all_values:
            res = {'username': name}
            current_time = value['time']

            # просто для удобства отслеживания записи дней
            if old_day != current_time.day:
                #print("!" + str(current_time))
                old_day = current_time.day

            # день и время берем по медиане
            vector_time = value['time']
            res['weekday'] = vector_time.weekday()
            res['daytime'] = vector_time.hour // 8
            if not (value['domain'] in self.domains):
                self.domains.append(value['domain'])
            res['d'] = self.domains.index(value['domain'])
            if not (value['url'] in self.urls):
                self.urls.append(value['url'])

            res['f_d'] = (1 if value['domain'] in self.fr_domains else 0)
            res['f_u'] = (1 if value['url'] in self.fr_urls else 0)
            res['start_computer'] = value['start_computer']
            result.append(res)
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


















