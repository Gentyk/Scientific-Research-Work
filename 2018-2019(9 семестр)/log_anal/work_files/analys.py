import calendar
from datetime import datetime as dd, timedelta
from django.db.models import Avg, Max, Min, Sum
from django.db.models import F
import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
from pytz import timezone

from analyse.models import Bigrams, Log, Trigrams

PERIOD = 25 # период времени в днях из которого 70% будут использоваться для обучения, а 30% для тетстирования
TIMES_OF_DAY = 8  # на сколько поделим день для анализа активности за день
TOTAL_SECONDS = 10  # анализ пауз между включением компа и браузера -  шаг(диапазо)
TOTAL_SECONDS_IN_MIN = 3  # аналогично, но в течение минуты
NUMBER_FREQUENT_URL = 20
NUMBER_FREQUENT_DOMAINS = 20
WIDTH = 32*5
HEIGHT = 18*5


class Main:
    def __init__(self):
        """
        Просмотр всех пользователей в логах и запуск анализа для каждого из них. В результате будут созданы файлы с
        данными о каждом.
        """
        names = Log.objects.values_list('username').distinct()
        print(names)
        names = [name[0] for name in names]
        for name in names:
            print("0")
            log = Log.objects.filter(username=name)
            print(name)
            finish_time = log.earliest('time').time + timedelta(days=PERIOD)

            u_log = log.filter(time__lt=finish_time)
            bi_log = Bigrams.objects.filter(username=name).filter(time1__lt=finish_time).filter(time2__lt=finish_time)
            tri_log = Trigrams.objects.filter(username=name).filter(time2__lt=finish_time).filter(time3__lt=finish_time)

            print("1")
            a = Analyst(u_log, bi_log, tri_log, name, finish_time)
            print("2")
            a.activity_analyse()
            print("3")
            path = './users/' + name + '_otch.npy'
            np.save(path, a.result)
            print("4")
            # path = './users/' + name + '_otch.txt'
            # with open(path, 'w') as f:
            #     for k in a.result:
            #         s = k + ": " + str(a.result[k]) + "\n"
            #         f.writelines(s)


class Analyst(object):
    def __init__(self, log, bi_log, tri_log, username, finish_time):
        self.log = log
        self.bi = bi_log
        self.tri = tri_log
        self.username = username
        self.finish_time = finish_time
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
        #self.start_treatment()
        #self.distribution_in_time()
        self.frequent_objects()
        self.n_gramms()
        #self.pause()
        #self.graphic_res()

    # Пункт 0: самые общие данные о логе
    def start_treatment(self):
        # самая общая информация о логе, которая могла вас интересовать
        self.result['всего записей'] = self.n_clicks
        start = self.log.earliest('time').time
        end = self.log.latest('time').time
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
        start_brows = []
        start_brows_3min = []
        starts = self.log.filter(start_computer=True).values_list('id', 'time')
        for id, time in starts:
            if self.log.get(pk=(id + 1)).url:
                time2 = self.log.get(pk=(id + 1)).time
                pause = (abs(time - time2)).seconds
                if pause >= 180:
                    start_brows.append(pause)
                else:
                    start_brows_3min.append(pause)
        self.result['средняя пауза между запуском компа и браузера(>3min)'] = (sum(start_brows) / len(start_brows)
                                                                               if len(start_brows) > 0 else 0)
        self.result['средняя пауза между запуском компа и браузера(<3min)'] = (sum(start_brows_3min) / len(start_brows_3min)
                                                                               if len(start_brows_3min) > 0 else 0)

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

        # Пункт 2.2: среднее время между кликами при просмтривании частого ресурса
        url_time = self._duration_of_viewing_frequent_objects(frequent_urls, 'url')
        domain_time = self._duration_of_viewing_frequent_objects(frequent_domains, 'domain')
        self.result['распределение пауз между кликами на частых url(когда не переключаемся на другой)'] = url_time
        self.result['распределение пауз между кликами на частых доменах(когда не переключаемся на другой)'] = domain_time

        # Пункт 2.3: карта кликов
        # self._click_map(frequent_urls, 'url')
        # self._click_map(frequent_domains, 'domain')

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
        r1 = []
        for n in mass:
            for object in objects[n]:
                if obj_type == 'domain':
                    query = self.log.filter(domain=object)
                else:
                    query = self.log.filter(url=object)
                n_seance = query.values_list('seance').distinct().count()
                frequent_objects.append((object, n, n / self.n_clicks, n_seance / self.seance))
                r1.append(object)
                if len(r1)>=20:
                    r1 = r1[:20]
                    break
            if len(r1)>=20:
                r1 = r1[:20]
                break
        #return frequent_objects
        return r1

    def _duration_of_viewing_frequent_objects(self, list_fr_obj, type_obj):
        """
        ПОлсчет средней из всех пауз, когда пользователь сидит на одном и том же частом ресурсе
        :param list_fr_obj: массив частых урлов/доменов
        :param type_obj: тип объекта 'url'/'damain'
        :return: словарь вида:
                {
                    url1 : средняя пауза(в секундах),
                    ...
                }
        """
        times = {}
        for i in list_fr_obj:
            if type_obj == 'url':
                data = self.bi.filter(url1=i).filter(url2=i).values_list('time2', 'time1')
            if type_obj == 'domain':
                data = self.bi.filter(domain1=i).filter(domain2=i).values_list('time2', 'time1')
            mass = [(abs(d[0] - d[1])).seconds for d in data]
            times[i] = sum(mass)/len(mass)
        return times

    def _click_map(self, frequent_objects, type_obj):
        # создание карты кликов для списка объектов
        i = 0
        path = str("./users/")+self.username
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.makedirs(path)
        for data in frequent_objects:
            obj = data#[0]
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
            i += 1
            np.save(path+"\\"+type_obj+" "+self.username+str(i), matrix)

            # изображаем карту кликов
            # px = []
            # py = []
            # a = []
            # cm = plt.cm.get_cmap('jet')
            # for y in range(HEIGHT):
            #     for x in range(WIDTH):
            #         px.append(x)
            #         py.append(HEIGHT-y)
            #         a.append(int(matrix[y, x]) if int(matrix[y, x]) > 0 else None)
            #
            # plt.scatter(px, py, c=a, cmap=cm)
            # plt.xlabel("x")
            # plt.ylabel("y")
            # plt.title(str(obj))
            # cbar = plt.colorbar()
            # cbar.set_label("elevation (m)", labelpad=+1)
            # #plt.show()
            # i+=1
            # plt.savefig(path+"\\"+type_obj+" "+self.username+" "+str(i)+".png")
            # plt.clf()

    # Пункт 3: частые n-граммы
    def n_gramms(self):
        """
        Функция, которая получает информацию о биграммах и триграммах пользователя и записывает их в словарь
        """
        urls_bigrams, domains_bigrams = self._bigramm()
        print(len(urls_bigrams))
        print(len(domains_bigrams))
        self.result['url биграммы'] = urls_bigrams
        self.result['domain биграммы'] = domains_bigrams

        urls_trigrams, domains_trigrams = self._trigramm()
        print(len(urls_trigrams))
        print(len(domains_trigrams))
        self.result['url триграммы'] = urls_trigrams
        self.result['domain триграммы'] = domains_trigrams

    def _bigramm(self):
        print('биграммы начало')
        bi_gramms = {}
        a = self.bi.only('url1', 'url2').exclude(url1=F('url2')).distinct('url1', 'url2').values_list('url1', 'url2')
        mass = []
        for data in a:
            n = self.bi.only('url1', 'url2').filter(url1=data[0]).filter(url2=data[1]).count()
            if n in bi_gramms:
                bi_gramms[n].append((data[0], data[1]))
            else:
                bi_gramms[n] = [(data[0], data[1])]
            if n not in mass:
                mass.append(n)
        mass.sort(reverse=True)
        mass = mass[:15]
        result_bi_gramms = {}
        for n in mass:
            for urls in bi_gramms[n]:
                times = self.bi.filter(url1=urls[0]).filter(url2=urls[1]).values_list('time1', 'time2')
                mass_t = [(abs(t[1] - t[0])).seconds for t in times]
                v = 0
                if mass_t:
                    v = sum(mass_t) / len(mass_t)
                result_bi_gramms[tuple(urls[0], urls[1])] = v#(max(t), v, t)
                if len(result_bi_gramms) >= 15:
                    break
            if len(result_bi_gramms) >= 15:
                break


        bi_gramms = {}
        a = self.bi.only('domain1', 'domain2').exclude(domain1=F('domain2')).distinct('domain1', 'domain2').values_list(
            'domain1', 'domain2')
        mass = []
        for data in a:
            n = self.bi.only('domain1', 'domain2').filter(domain1=data[0]).filter(domain2=data[1]).count()
            if n in bi_gramms:
                bi_gramms[n].append((data[0], data[1]))
            else:
                bi_gramms[n] = [(data[0], data[1])]
            if n not in mass:
                mass.append(n)
        mass.sort(reverse=True)
        mass = mass[:15]
        result_bid_gramms = {}
        for n in mass:
            for domains in bi_gramms[n]:
                times = self.bi.filter(domain1=domains[0]).filter(domain2=domains[1]).values_list('time1', 'time2')
                mass_t = [(abs(t[1] - t[0])).seconds for t in times]
                v = 0
                if mass_t:
                    v = sum(mass_t)/len(mass_t)
                result_bid_gramms[tuple(domains[0], domains[1])] = v  # (max(t), v, t)
                if len(result_bid_gramms) >= 15:
                    break
            if len(result_bid_gramms) >= 15:
                break
        print('биграммы конец')
        return result_bi_gramms, result_bid_gramms

    def _trigramm(self):
        print('триграммы начало')
        th_gramms = {}
        a = self.tri.only('url1', 'url2', 'url3').distinct('url1', 'url2', 'url3').values_list('url1', 'url2', 'url3')
        mass = []
        for data in a:
            n =  self.tri.only('url1', 'url2', 'url3').filter(url1=data[0]).filter(url2=data[1]).filter(url3=data[2]).count()
            if n in th_gramms:
                th_gramms[n].append((data[0], data[1], data[2]))
            else:
                th_gramms[n] = [(data[0], data[1], data[2])]
            if n not in mass:
                mass.append(n)
        mass.sort(reverse=True)
        mass = mass[:10]
        result_gramms = {}
        for n in mass:
            for data in th_gramms[n]:
                times = self.tri.filter(url1=data[0]).filter(url2=data[1]).filter(url3=data[2]).values_list('time1', 'time2', 'time3')
                v = 0
                v2 = 0
                mass_t = [(abs(t[1] - t[0])).seconds for t in times]
                mass_t2 = [(abs(t[2] - t[1])).seconds for t in times]
                if mass_t:
                    v = sum(mass_t) / len(mass_t)
                if mass_t2:
                    v2 = sum(mass_t2) / len(mass_t2)
                result_gramms[tuple(data[0], data[1], data[2])] = (v, v2)# = (max(t), v, t, max(t2), v2, t2)
                if len(result_gramms) >= 10:
                    break
            if len(result_gramms) >= 10:
                break

        th_gramms = {}
        a = self.tri.only('domain1', 'domain2', 'domain3').exclude(domain1=F('domain2')).exclude(domain2=F('domain3')).distinct('domain1', 'domain2', 'domain3').values_list('domain1', 'domain2', 'domain3')
        mass = []
        for data in a:
            n = self.tri.only('domain1', 'domain2', 'domain3').filter(domain1=data[0]).filter(domain2=data[1]).filter(
                domain3=data[2]).count()
            if n in th_gramms:
                th_gramms[n].append((data[0], data[1], data[2]))
            else:
                th_gramms[n] = [(data[0], data[1], data[2])]
            if n not in mass:
                mass.append(n)
        mass.sort(reverse=True)
        mass = mass[:10]
        resultb_gramms = {}
        for n in mass:
            for data in th_gramms[n]:
                times = self.tri.filter(url1=data[0]).filter(url2=data[1]).filter(url3=data[2]).\
                    values_list('time1', 'time2', 'time3')
                v = 0
                v2 = 0
                mass_t = [(abs(t[1] - t[0])).seconds for t in times]
                mass_t2 = [(abs(t[2] - t[1])).seconds for t in times]
                if mass_t:
                    v = sum(mass_t) / len(mass_t)
                if mass_t2:
                    v2 = sum(mass_t2) / len(mass_t2)
                resultb_gramms[tuple(data[0], data[1], data[2])] = (v, v2)  # = (max(t), v, t, max(t2), v2, t2)
                if len(resultb_gramms) >= 10:
                    break
            if len(resultb_gramms) >= 10:
                break
        print('триграммы конец')
        return result_gramms, resultb_gramms

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