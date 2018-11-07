from datetime import datetime as dd, timedelta
from pytz import timezone
from django.test import TestCase
from django.db.models import Avg, Max, Min, Sum

from analyse.models import Log

NAME = "IAM"
TIMES_OF_DAY = 8    # на сколько поделим день для анализа активности за день
TOTAL_SECONDS = 10  # анализ пауз между включением компа и браузера -  шаг(диапазо)
TOTAL_SECONDS_IN_MIN = 3    # аналогично, но в течение минуты
NUMBER_FREQUENT_URL = 30
NUMBER_FREQUENT_DOMAINS = 20
WIDTH = 20
HEIGHT = 10

class Test1(TestCase):

    def start_treatment(self):
        # самая общая информация о логе, которая могла вас интересовать
        result = {}
        result['всего записей'] = Log.objects.count()
        result['начало записи лога'] = Log.objects.all().aggregate(Min('time'))['time__min']
        result['конец записи лога'] = Log.objects.all().aggregate(Max('time'))['time__max']
        time = result['конец записи лога'] - result['начало записи лога']
        result['длительность снятия данных'] = str(time)
        result['количество сессий'] = Log.objects.get(time=result['конец записи лога']).seance
        return result

    def activity_analyse(self):
        result = {}
        # распределение активности по дням недели
        week = {}
        num_clicks = Log.objects.count()
        days = set([i[0] for i in Log.objects.all().values_list('day')])
        for day in days:
            if day.weekday() in week:
                week[day.weekday()] += Log.objects.filter(day=day).count()
            else:
                week[day.weekday()] = Log.objects.filter(day=day).count()

        for weekday in week:
            week[weekday] = week[weekday]/num_clicks
        result['распределение по дням недели'] = week

        # распределение активности по времени суток
        d_time = {}
        periods = {}
        hour_s = 0
        hour = int(24/TIMES_OF_DAY)
        for i in range(TIMES_OF_DAY):
            time = dd.strptime(str(hour_s)+":0:0", '%H:%M:%S')
            start = time.replace(tzinfo=timezone('UTC'))
            h = hour*(i+1)
            if h == 24:
                time = dd.strptime("23:59:59", '%H:%M:%S')
            else:
                time = dd.strptime(str(h)+":0:0", '%H:%M:%S')
            end = time.replace(tzinfo=timezone('UTC'))
            periods[i] = [
                start.replace(tzinfo=timezone('UTC')),
                end.replace(tzinfo=timezone('UTC'))
            ]
            hour_s = hour*(i+1)
        for k in periods:
            d_time[k] = Log.objects.filter(local_time__gte=periods[k][0]).filter(local_time__lt=periods[k][1]).count()/num_clicks
        result['распределение по времени суток'] = d_time

        # время запуска chrome после входа в систему
        start_brows = {}
        start_brows_min = {}
        starts = Log.objects.filter(start_computer=True)
        starts_n = starts.count()
        starts = starts.values_list('id', 'time')
        starts_min = 0
        for id, time in starts:
            time2 = Log.objects.get(pk=(id+1)).time
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
            t[pause] = t[pause]/starts_n
        for pause_key in t2:
            t2[pause_key] = t2[pause_key]/starts_min
        result['распределение пауз между запуском компа и браузера'] = t
        result['распределение пауз между запуском компа и браузера(минута)'] = t2

        # наиболее частые урлы
        # наиб частые домены
        all_urls = set([url[0] for url in Log.objects.values_list('url')])
        n_urls = len(all_urls)
        mass = []
        urls = {}
        for url in all_urls:
            n = Log.objects.filter(url=url).count()
            if n not in mass:
                mass.append(n)
            if n in urls:
                urls[n].append(url)
            else:
                urls[n] = [url]
        mass.sort()
        mass = mass[::-1]
        mass = mass[:NUMBER_FREQUENT_URL]
        frequent_urls = []
        for n in mass:
            frequent_urls.append((n, n/n_urls, urls[n]))
        result['частые url'] = frequent_urls

        all_domains = set([domain[0] for domain in Log.objects.values_list('domain')])
        n_domains = len(all_domains)
        mass = []
        domains = {}
        for domain in all_domains:
            n = Log.objects.filter(domain=domain).count()
            if n in mass:
                pass
            else:
                mass.append(n)
            if n in domains:
                domains[n].append(domain)
            else:
                domains[n] = [domain]
        mass.sort()
        mass = mass[::-1]
        mass = mass[:NUMBER_FREQUENT_DOMAINS]
        frequent_domains = []
        for n in mass:
            frequent_domains.append((n, n / n_domains, domains[n]))
        result['частые домены'] = frequent_domains




        return result

    def test1(self):
        result = self.start_treatment()
        result.update(self.activity_analyse())
        for k in result:
            s = k+": "+str(result[k])
            print(s)


