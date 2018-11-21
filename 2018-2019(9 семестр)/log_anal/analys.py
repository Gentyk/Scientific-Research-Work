import calendar
from datetime import datetime as dd, timedelta
from django.db.models import Avg, Max, Min, Sum
import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
from pytz import timezone

from analyse.models import Log

TIMES_OF_DAY = 8  # на сколько поделим день для анализа активности за день
TOTAL_SECONDS = 10  # анализ пауз между включением компа и браузера -  шаг(диапазо)
TOTAL_SECONDS_IN_MIN = 3  # аналогично, но в течение минуты
NUMBER_FREQUENT_URL = 20
NUMBER_FREQUENT_DOMAINS = 20
WIDTH = 32*5#320
HEIGHT = 18*5#180


class Main:
    def __init__(self):
        names = Log.objects.values_list('username').distinct()
        names = [name[0] for name in names]
        for name in names:
            u_log = Log.objects.filter(username=name)
            a = Analyst(u_log, name)
            a.activity_analyse()
            path = './users/' + name + '_otch.txt'
            with open(path, 'w') as f:
                for k in a.result:
                    s = k + ": " + str(a.result[k]) + "\n"
                    f.writelines(s)
                #json.dump(a.result, f)


class Analyst:
    def __init__(self, log, username):
        self.log = log
        self.username = username
        self.seance = log.values("seance").distinct().count()
        self.n_clicks = self.log.filter(start_computer=False).count()
        self.result = {}

    # последовательный анализ лога по пуктам
    def activity_analyse(self):
        # создаем папку для результатов
        path = str("./users/")+self.username
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.makedirs(path)
        # последовательный анализ лога по пуктам
        self.start_treatment()
        self.distribution_in_time()
        self.frequent_objects()
        self.n_gramms()
        self.pause()
        self.graphic_res()

    # Пункт 0: самые общие данные о логе
    def start_treatment(self):
        # самая общая информация о логе, которая могла вас интересовать
        self.result['всего записей'] = self.n_clicks
        start = self.log.aggregate(Min('time'))['time__min']
        end = self.log.aggregate(Max('time'))['time__max']
        time = end - start
        self.result['длительность снятия данных'] = str(time)
        self.result['начало записи лога'] = str(start)
        self.result['конец записи лога'] = str(end)
        self.result['количество сеансов'] = self.seance

    # Пункт 1: распределением по дням недели и времени суток; время между запуском компа и браузера
    def distribution_in_time(self):
        # распределение активности по дням недели
        week = {}
        week_r = {}
        num_clicks = self.log.count()
        days = [i[0] for i in self.log.values_list('day').distinct()]
        for day in days:
            if day.weekday() in week:
                week[day.weekday()] += self.log.filter(day=day).count()
            else:
                week[day.weekday()] = self.log.filter(day=day).count()
        for weekday in week:
            week_r[weekday] = week[weekday] / num_clicks
        self.result['распределение по дням недели'] = week_r

        # распределение активности по времени суток
        d_time = {}
        periods = {}
        hour_s = 0
        hour = int(24 / TIMES_OF_DAY)
        # для этого 24 часа делим на промежутки и для каждого промежутка фикцируем, когда о начинается и когда заканчивается
        for i in range(TIMES_OF_DAY):
            time = dd.strptime(str(hour_s) + ":0:0", '%H:%M:%S')
            start = time.replace(tzinfo=timezone('UTC'))
            h = hour * (i + 1)
            if h == 24:
                time = dd.strptime("23:59:59", '%H:%M:%S')
            else:
                time = dd.strptime(str(h) + ":0:0", '%H:%M:%S')
            end = time.replace(tzinfo=timezone('UTC'))
            periods[i] = [
                start.replace(tzinfo=timezone('UTC')),
                end.replace(tzinfo=timezone('UTC'))
            ]
            hour_s = hour * (i + 1)
        # далее фильтруем
        for k in periods:
            d_time[k] = self.log.filter(local_time__gte=periods[k][0]).filter(
                local_time__lt=periods[k][1]).count() / num_clicks
        self.result['распределение по времени суток'] = d_time

        # распределение по дням недели и времени суток
        week_time = {}
        week_time_abs = {}
        for day in days:
            for k in periods:
                n_click = self.log.filter(day=day).\
                                   filter(local_time__gte=periods[k][0]).\
                                   filter(local_time__lt=periods[k][1]).\
                                   count()
                value = n_click / num_clicks
                value_abs = n_click / week[day.weekday()]
                if day.weekday() in week_time:
                    if k in week_time[day.weekday()]:
                        week_time[day.weekday()][k] += value
                        week_time_abs[day.weekday()][k] += value_abs
                    else:
                        week_time[day.weekday()][k] = value
                        week_time_abs[day.weekday()][k] = value_abs
                else:
                    week_time[day.weekday()] = {k: value}
                    week_time_abs[day.weekday()] = {k: value_abs}
        self.result['распределение по дням недели и времени суток1'] = week_time    # вообще
        self.result['распределение по дням недели и времени суток'] = week_time_abs # если день брать за 100%

        # время запуска chrome после входа в систему
        start_brows = {}
        start_brows_min = {}
        starts = self.log.filter(start_computer=True)
        starts_n = starts.count()
        starts = starts.values_list('id', 'time')
        starts_min = 0
        for id, time in starts:
            try:
                time2 = self.log.get(pk=(id + 1)).time
                pause = time2 - time
                pause_key = pause.seconds #// TOTAL_SECONDS
                if pause_key in start_brows:
                    start_brows[pause_key] += 1
                else:
                    start_brows[pause_key] = 1
                if pause.seconds <= 60:
                    starts_min += 1
                    pause_key = pause.seconds #// TOTAL_SECONDS_IN_MIN
                    if pause_key in start_brows_min:
                        start_brows_min[pause_key] += 1
                    else:
                        start_brows_min[pause_key] = 1
            except:
                pass
        #self.result['количество пауз между запуском компа и браузера'] = start_brows
        #self.result['количество пауз между запуском компа и браузера(минута)(в количестве)'] = start_brows_min
        t = start_brows.copy()
        t2 = start_brows_min.copy()
        for pause in t:
            t[pause] = t[pause] / starts_n
        for pause_key in t2:
            t2[pause_key] = t2[pause_key] / starts_min
        self.result['распределение пауз между запуском компа и браузера'] = t
        self.result['распределение пауз между запуском компа и браузера(минута)'] = t2

    # Пункт 2: получение частых объектов (url-ов и доменов)
    def frequent_objects(self):
        # Пункт 2.0: наиболее частые урлы и частые домены
        # Пункт 2.1: в скольки процентах сеансов мы встречаем частые объекты
        # данные возвращаются в виде:
        # [(объект, количество кликов, относительное количество кликов, пункт 2.1), ...]
        all_urls = [url[0] for url in self.log.values_list('url').distinct()]
        frequent_urls = self._get_frequent_objects_list(all_urls, 'url', NUMBER_FREQUENT_URL)
        self.result['частые url'] = frequent_urls
        all_domains = [domain[0] for domain in self.log.values_list('domain').distinct()]
        frequent_domains = self._get_frequent_objects_list(all_domains, 'domain', NUMBER_FREQUENT_DOMAINS)
        self.result['частые домены'] = frequent_domains

        # Пункт 2.2: время нахождения на одном ресурсе
        url_time, url_clicks = self._duration_of_viewing_frequent_objects(frequent_urls, 'url')
        domain_time, domain_clicks = self._duration_of_viewing_frequent_objects(frequent_domains, 'domain')
        self.result['распределение пауз между кликами на частых url(когда не переключаемся на другой)'] = url_time
        self.result['распределение количества кликов на частых url(когда не переключаемся на другой)'] = url_clicks
        self.result['распределение пауз между кликами на частых доменах(когда не переключаемся на другой)'] = domain_time
        self.result['распределение количества кликов на частых доменах(когда не переключаемся на другой)'] = domain_clicks

        # Пункт 2.3: карта кликов
        self._click_map(frequent_urls, 'url')
        self._click_map(frequent_domains, 'domain')

    def _get_frequent_objects_list(self, obj_list, obj_type, numbers):
        # возвращает массив частых объектов в виде:
        # [
        #   (object, n, n / self.n_clicks, n_seance / self.seance),
        #    ...
        # ]
        mass = []
        objects = {}
        for object in obj_list:
            if obj_type == 'domain':
                n = self.log.filter(domain=object).count()
            else:
                n = self.log.filter(url=object).count()
            if n in mass:
                pass
            else:
                mass.append(n)
            if n in objects:
                objects[n].append(object)
            else:
                objects[n] = [object]
        mass.sort(reverse=True)
        mass = mass[:numbers]
        frequent_objects = []
        for n in mass:
            for object in objects[n]:
                if obj_type == 'domain':
                    query = self.log.filter(domain=object)
                else:
                    query = self.log.filter(url=object)
                n_seance = query.values_list('seance').distinct().count()
                frequent_objects.append((object, n, n / self.n_clicks, n_seance / self.seance))
        return frequent_objects

    def _duration_of_viewing_frequent_objects(self, list_fr_obj, name_obj):
        query = "SELECT " \
                    "   p2.id as id, p2.time as time " \
                    "FROM analyse_log p1" \
                    "   JOIN analyse_log p2" \
                    "      ON p1.id+1 = p2.id" \
                    "      AND p1.obj <> %s" \
                    "      AND p2.obj = %s" \
                    "      AND p1.seance = p2.seance" \
                    "      AND p1.username = %s AND p2.username = %s " \
                    "      OR  p1.id-1 = p2.id" \
                    "      AND p1.obj <> %s" \
                    "      AND p2.obj = %s" \
                    "      AND p1.seance = p2.seance" \
                    "      AND p1.username = %s AND p2.username = %s" \
                    "      OR  p1.id+1 = p2.id" \
                    "      AND p2.obj = %s" \
                    "      AND p1.seance <> p2.seance" \
                    "      AND p1.username = %s AND p2.username = %s" \
                    "      OR  p1.id-1 = p2.id" \
                    "      AND p2.obj = %s" \
                    "      AND p1.seance <> p2.seance" \
                    "      AND p1.username = %s AND p2.username = %s"
        obj_query = query.replace('obj', name_obj)
        times = {}
        clicks = {}
        for i in list_fr_obj:
            obj = i[0]
            times[obj] = []
            clicks[obj] = []
            params = [obj, obj, self.username, self.username, obj, obj, self.username, self.username, obj, self.username, self.username, obj, self.username, self.username,]
            data = Log.objects.raw(obj_query, params)
            a = len(data)
            for i in range(a//2):
                clicks[obj].append(data[i * 2 + 1].id - data[i * 2].id)
                times[obj].append(data[i*2+1].time - data[i*2].time if data[i*2+1].time - data[i*2].time > timedelta(seconds=0) else timedelta(seconds=0))
        return times, clicks

    def _click_map(self, frequent_objects, type_obj):
        # создание карты кликов для списка объектов
        i = 0
        path = str("./users/")+self.username
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.makedirs(path)
        for data in frequent_objects:
            obj = data[0]
            if type_obj == 'domain':
                mass_coordinates = self.log.filter(domain=obj).values_list(
                    'x_cursor_coordinates',
                    'y_cursor_coordinates',
                    'x1_window_coordinates',
                    'x2_window_coordinates',
                    'y1_window_coordinates',
                    'y2_window_coordinates',
                )
            else:
                mass_coordinates = self.log.filter(url=obj).values_list(
                    'x_cursor_coordinates',
                    'y_cursor_coordinates',
                    'x1_window_coordinates',
                    'x2_window_coordinates',
                    'y1_window_coordinates',
                    'y2_window_coordinates',
                )
            matrix = np.zeros((HEIGHT, WIDTH))

            for c in mass_coordinates:
                try:
                    y_point = int((c[1] - c[4]) / ((c[5] - c[4]) / HEIGHT))
                    if y_point == HEIGHT:
                        y_point = HEIGHT - 1
                    x_point = int((c[0] - c[2]) / ((c[3] - c[2]) / HEIGHT))
                    if x_point == WIDTH:
                        x_point = WIDTH - 1
                    matrix[y_point, x_point] += 1
                except:
                    pass

            px = []
            py = []
            a = []
            cm = plt.cm.get_cmap('jet')
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    px.append(x)
                    py.append(HEIGHT-y)
                    a.append(int(matrix[y, x]) if int(matrix[y, x]) > 0 else None)

            plt.scatter(px, py, c=a, cmap=cm)
            plt.xlabel("x")
            plt.ylabel("y")
            plt.title(str(obj))
            cbar = plt.colorbar()
            cbar.set_label("elevation (m)", labelpad=+1)
            #plt.show()
            i+=1
            plt.savefig(path+"\\"+type_obj+" "+self.username+" "+str(i)+".png")
            plt.clf()

    # Пункт 3: частые n-граммы
    def n_gramms(self):
        a, b = self._get_n_gramms('url')
        self.result['время биграмм урлов'] = a
        self.result['время триграмм урлов'] = b

        c,d = self._get_n_gramms('domain')
        self.result['время биграмм доменов'] = c
        self.result['время триграмм доменов'] = d

    def _bigramm(self, query, query2, query_time, params):
        bi_gramms = {}
        a = Log.objects.raw(query, params)
        mass = []
        for data in a:
            n = len(Log.objects.raw(query2, [data.u1, data.u2]+params))
            if n in bi_gramms:
                bi_gramms[n].append((data.u1, data.u2))
            else:
                bi_gramms[n] = [(data.u1, data.u2)]
            if n not in mass:
                mass.append(n)
        mass.sort(reverse=True)
        mass = mass[:30]
        result_bi_gramms = {}
        for n in mass:
            for urls in bi_gramms[n]:
                times = Log.objects.raw(query_time, [urls[0], urls[1]] + params)
                t = [t.t2.seconds for t in times]
                v = None
                if t:
                    v = sum(t)/len(t)
                result_bi_gramms[urls[0] + ", " + urls[1]] = (max(t), v, t)
        return result_bi_gramms

    def _threegramm(self, query, query2, query_time, name):
        th_gramms = {}
        a = Log.objects.raw(query, [name, name, name])
        mass = []
        for data in a:
            n = len(Log.objects.raw(query2, [data.u1, data.u2, name, name, data.u3, name]))
            if n in th_gramms:
                th_gramms[n].append((data.u1, data.u2, data.u3))
            else:
                th_gramms[n] = [(data.u1, data.u2, data.u3)]
            if n not in mass:
                mass.append(n)
        mass.sort(reverse=True)
        mass = mass[:30]
        result_gramms = {}
        for n in mass:
            for data in th_gramms[n]:
                times = Log.objects.raw(query_time, [data[0], data[1], name, name, data[2], name])
                t = [t.t1.seconds for t in times]
                t2 = [t.t2.seconds for t in times]
                v = None
                v2 = None
                if t:
                    v = sum(t)/len(t)
                if t2:
                    v2 = sum(t2) / len(t2)
                result_gramms[data[0] + ", " + data[1] + ", " + data[2]] = (max(t), v, t, max(t2), v2, t2)
        return result_gramms

    def _get_n_gramms(self, obj_name):
        # биграммы obj1<>obj2
        # самые частые биграммы(без повторений) и основная информация о них
        bi_query = "SELECT DISTINCT ON " \
                    "   (p1.obj, p2.obj)  p1.id as id, p1.obj as u1, p2.obj as u2 " \
                    "FROM analyse_log p1" \
                    "   JOIN analyse_log p2" \
                    "      ON p1.id+1 = p2.id" \
                    "      AND p1.obj <> p2.obj"\
                    "      AND p1.start_computer = False" \
                    "      AND p2.start_computer = False" \
                    "      AND p1.seance = p2.seance" \
                    "      AND p1.username = %s AND p2.username = %s"
        # для подсчета количества каждой биграммы
        bi_query2 = "SELECT " \
                    "   p1.id " \
                    "FROM analyse_log p1" \
                    "   JOIN analyse_log p2" \
                    "      ON p1.id+1 = p2.id" \
                    "      AND p1.obj = %s" \
                    "      AND p2.obj = %s" \
                    "      AND p1.seance = p2.seance" \
                    "      AND p1.username = %s AND p2.username = %s"
        # пауза перед переходом в биграмме
        bi_query_time = "SELECT " \
                    "   p1.id, (p2.time - p1.time) as t2 " \
                    "FROM analyse_log p1" \
                    "   JOIN analyse_log p2" \
                    "      ON p1.id+1 = p2.id" \
                    "      AND p1.obj = %s" \
                    "      AND p2.obj = %s" \
                    "      AND p1.seance = p2.seance" \
                    "      AND p1.username = %s AND p2.username = %s"
        bigramm_params = [self.username, self.username]
        obj_query = bi_query.replace('obj', obj_name)
        obj_query2 = bi_query2.replace('obj', obj_name)
        obj_query_time = bi_query_time.replace('obj', obj_name)
        bigramms = self._bigramm(obj_query, obj_query2, obj_query_time, bigramm_params)

        # триграммы url1<>url2 or url2<>url3
        th_query = "WITH table111 AS (SELECT DISTINCT ON " \
                "   (p1.obj, p2.obj, p3.obj)  p1.id as id, p1.obj as u1, p2.obj as u2, p3.obj as u3 " \
                "FROM analyse_log p1" \
                "   JOIN analyse_log p2" \
                "      ON p1.id+1 = p2.id" \
                "      AND p1.start_computer = False" \
                "      AND p2.start_computer = False" \
                "      AND p1.seance = p2.seance" \
                "      AND p1.username = %s " \
                "      AND p2.username = %s"\
                "   JOIN analyse_log p3" \
                "      ON p1.id+2 = p3.id" \
                "      AND p1.start_computer = False" \
                "      AND p3.start_computer = False" \
                "      AND p1.seance = p3.seance" \
                "      AND p3.username = %s) "\
                "SELECT * " \
                "FROM table111 " \
                "WHERE table111.u1 <> table111.u2 OR table111.u2 <> table111.u3"
        th_query2 = "SELECT " \
                "   p1.id as id " \
                "FROM analyse_log p1" \
                "   JOIN analyse_log p2" \
                "      ON p1.id+1 = p2.id" \
                "      AND p1.obj = %s" \
                "      AND p2.obj = %s" \
                "      AND p1.seance = p2.seance" \
                "      AND p1.username = %s " \
                "      AND p2.username = %s"\
                "   JOIN analyse_log p3" \
                "      ON p1.id+2 = p3.id" \
                "      AND p3.obj = %s" \
                "      AND p1.seance = p3.seance" \
                "      AND p3.username = %s "
        th_query_time = "SELECT " \
                "   p1.id as id,  (p2.time - p1.time) as t1,  (p3.time - p2.time) as t2 " \
                "FROM analyse_log p1" \
                "   JOIN analyse_log p2" \
                "      ON p1.id+1 = p2.id" \
                "      AND p1.obj = %s" \
                "      AND p2.obj = %s" \
                "      AND p1.start_computer = False" \
                "      AND p2.start_computer = False" \
                "      AND p1.seance = p2.seance" \
                "      AND p1.username = %s AND p2.username = %s"\
                "   JOIN analyse_log p3" \
                "      ON p1.id+2 = p3.id" \
                "      AND p1.start_computer = False" \
                "      AND p3.start_computer = False" \
                "      AND p3.obj = %s" \
                "      AND p1.seance = p3.seance" \
                "      AND p3.username = %s "
        three_query = th_query.replace('obj', obj_name)
        three_query2 = th_query2.replace('obj', obj_name)
        three_query_time = th_query_time.replace('obj', obj_name)
        thgramms = self._threegramm(three_query, three_query2, three_query_time, self.username)

        return bigramms, thgramms

    # Пункт 4: паузы до 5 минут
    def pause(self):
        pauses = "SELECT " \
                    "   p1.id, (p2.time - p1.time) as t " \
                    "FROM analyse_log p1" \
                    "   JOIN analyse_log p2" \
                    "      ON p1.id+1 = p2.id" \
                    "      AND p1.start_computer = False" \
                    "      AND p2.start_computer = False" \
                    "      AND p1.seance = p2.seance" \
                    "      AND p1.username = %s AND p2.username = %s"
        times = Log.objects.raw(pauses, [self.username, self.username])
        pause_statistic = {}
        for t in times:
            sec = t.t.seconds
            if sec < 300 and sec > 0:
                k = sec // 10
                if k in pause_statistic:
                    pause_statistic[k] += 1
                else:
                    pause_statistic[k] = 1
        self.result['распределение пауз'] = pause_statistic

    # Пункт 5: графический отчет
    def graphic_res(self):
        weekdays = list(calendar.day_abbr)
        self._simple_diagr('распределение по дням недели', self.result['распределение по дням недели'], weekdays)
        self._simple_diagr('распределение по времени суток', self.result['распределение по времени суток'])

        title = 'распределение по дням недели и времени суток'  # если день брать за 100%
        for key in self.result[title]:
            self._simple_diagr(title, self.result[title][key], note=str(weekdays[key]))

        titles = [
            'распределение пауз между запуском компа и браузера',
            'распределение пауз между запуском компа и браузера(минута)'
        ]
        for title in titles:
            self._simple_line(title, self.result[title])

        titles = [
            'частые url',
            'частые домены'
        ]
        for title in titles:
            self._horiz_diagr(title, self.result[title])


    def _simple_diagr(self, title, data_dict, ox = None, note = ""):
        title = title + " " + note
        path = str("./users/") + self.username + "/" + title
        x=list(data_dict.keys())
        x.sort()
        y=[data_dict[k] for k in x]
        if ox:
            x = ox
        plt.bar(x, y)
        plt.title(title)
        #plt.show()
        plt.savefig(path + ".png")
        plt.clf()

    def _simple_line(self, title, data_dict):
        path = str("./users/") + self.username + "/" + title
        x = list(data_dict.keys())
        x.sort()
        #print(len(x))
        if len(x)>100:
            x = x[:100]
        y = [data_dict[i] for i in x]
        plt.plot(x, y)
        plt.title(title)
        # plt.show()
        plt.savefig(path + ".png")
        plt.clf()

    def _horiz_diagr(self, title, data):
        plt.rcdefaults()
        fig, ax = plt.subplots()
        path = str("./users/") + self.username + "/" + title
        x_f = []
        x_p = []
        frequency = {}  # количество
        probability = {} # вероятность встретить в сеансе
        for str1 in data:
            if str1[1] not in x_f:
                x_f.append(str1[1])
            if str1[3] not in x_p:
                x_p.append(str1[3])
            if str1[1] in frequency:
                frequency[str1[1]].append(str1[0])
            else:
                frequency[str1[1]] = [str1[0]]
            if str1[3] in probability:
                probability[str1[3]].append(str1[0])
            else:
                probability[str1[3]] = [str1[0]]
        x_f.sort()
        y = [str(frequency[i][0])[:20] for i in x_f]

        ax.barh(y, x_f, align='center')
        #ax.set_yticks(range(len(y)), y)
        ax.set_yticklabels(y)
        ax.set_title(title)
        plt.subplots_adjust(left=0.3)
        ax.invert_yaxis()
        plt.savefig(path + ".png")
        plt.clf()






