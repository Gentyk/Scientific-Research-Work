from datetime import datetime as dd
from pytz import timezone
from django.db.models import Avg, Max, Min, Sum
import numpy as np

NAME = "valli"
TIMES_OF_DAY = 8  # на сколько поделим день для анализа активности за день
TOTAL_SECONDS = 10  # анализ пауз между включением компа и браузера -  шаг(диапазо)
TOTAL_SECONDS_IN_MIN = 3  # аналогично, но в течение минуты
NUMBER_FREQUENT_URL = 30
NUMBER_FREQUENT_DOMAINS = 20
WIDTH = 20
HEIGHT = 16


class Analyst():
    def start_treatment(self, U_log):
        # самая общая информация о логе, которая могла вас интересовать
        result = {}
        result['всего записей'] = U_log.count()
        result['начало записи лога'] = U_log.aggregate(Min('time'))['time__min']
        result['конец записи лога'] = U_log.aggregate(Max('time'))['time__max']
        time = result['конец записи лога'] - result['начало записи лога']
        result['длительность снятия данных'] = str(time)
        result['количество сессий'] = U_log.get(time=result['конец записи лога']).seance
        return result

    def frequent_objects(self, U_log, obj_list, obj_type, numbers):
        # возвращает массив частых объектов в виде:
        # [
        #   ( количество объектов, относительная частота, список объектов с такой частотой),
        #    ...
        # ]
        n_objects = len(obj_list)
        mass = []
        objects = {}
        for object in obj_list:
            if obj_type == 'domain':
                n = U_log.filter(domain=object).count()
            else:
                n = U_log.filter(url=object).count()
            if n in mass:
                pass
            else:
                mass.append(n)
            if n in objects:
                objects[n].append(object)
            else:
                objects[n] = [object]
        mass.sort()
        mass = mass[::-1]
        mass = mass[:numbers]
        frequent_objects = []
        for n in mass:
            frequent_objects.append((n, n / n_objects, objects[n]))
        return frequent_objects

    def activity_analyse(self, U_log):
        result = {}
        # распределение активности по дням недели
        week = {}
        num_clicks = U_log.count()
        days = set([i[0] for i in U_log.values_list('day')])
        for day in days:
            if day.weekday() in week:
                week[day.weekday()] += U_log.filter(day=day).count()
            else:
                week[day.weekday()] = U_log.filter(day=day).count()

        for weekday in week:
            week[weekday] = week[weekday] / num_clicks
        result['распределение по дням недели'] = week

        # распределение активности по времени суток
        d_time = {}
        periods = {}
        hour_s = 0
        hour = int(24 / TIMES_OF_DAY)
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
        for k in periods:
            d_time[k] = U_log.filter(local_time__gte=periods[k][0]).filter(
                local_time__lt=periods[k][1]).count() / num_clicks
        result['распределение по времени суток'] = d_time

        # время запуска chrome после входа в систему
        start_brows = {}
        start_brows_min = {}
        starts = U_log.filter(start_computer=True)
        starts_n = starts.count()
        starts = starts.values_list('id', 'time')
        starts_min = 0
        for id, time in starts:
            time2 = U_log.get(pk=(id + 1)).time
            pause = time2 - time
            pause_key = pause.seconds // TOTAL_SECONDS
            if pause_key in start_brows:
                start_brows[pause_key] += 1
            else:
                start_brows[pause_key] = 1
            if pause.seconds <= 60:
                starts_min += 1
                pause_key = pause.seconds // TOTAL_SECONDS_IN_MIN
                if pause_key in start_brows_min:
                    start_brows_min[pause_key] += 1
                else:
                    start_brows_min[pause_key] = 1
        result['количество пауз между запуском компа и браузера'] = start_brows
        result['количество пауз между запуском компа и браузера(минута)(в количестве)'] = start_brows_min
        t = start_brows.copy()
        t2 = start_brows_min.copy()
        for pause in t:
            t[pause] = t[pause] / starts_n
        for pause_key in t2:
            t2[pause_key] = t2[pause_key] / starts_min
        result['распределение пауз между запуском компа и браузера'] = t
        result['распределение пауз между запуском компа и браузера(минута)'] = t2

        # наиболее частые урлы
        # наиб частые домены
        all_urls = set([url[0] for url in U_log.values_list('url')])
        frequent_urls = self.frequent_objects(U_log,all_urls,'url',NUMBER_FREQUENT_URL)
        result['частые url'] = frequent_urls

        all_domains = set([domain[0] for domain in U_log.values_list('domain')])
        frequent_domains = self.frequent_objects(U_log, all_domains, 'domain', NUMBER_FREQUENT_DOMAINS)
        result['частые домены'] = frequent_domains

        # выделим точки
        url_matrices = []
        for data in frequent_urls:
            for url in data[2]:
                mass_coordinates = U_log.filter(url=url).values_list(
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
                        y_point = (c[1] - c[4]) // ((c[5] - c[4]) // HEIGHT)
                        if y_point == HEIGHT:
                            y_point = HEIGHT - 1
                        x_point = (c[0] - c[2]) // ((c[3] - c[2]) // HEIGHT)
                        if x_point == WIDTH:
                            x_point = WIDTH - 1
                        matrix[y_point, x_point] += 1
                    except:
                        pass
                url_matrices.append((url, matrix))
        return result
