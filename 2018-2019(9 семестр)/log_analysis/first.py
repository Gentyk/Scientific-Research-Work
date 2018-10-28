from datetime import datetime, timedelta
import json
import numpy as np

TIMES_OF_DAY = 8    # на сколько поделим день для анализа активности за день
TOTAL_SECONDS = 10  # анализ пауз между включением компа и браузера -  шаг(диапазо)
TOTAL_SECONDS_IN_MIN = 3    # аналогично, но в течение минуты
NUMBER_FREQUENT_URL = 30
NUMBER_FREQUENT_DOMAINS = 20
WIDTH = 20
HEIGHT = 10


class LogCheck:
    def __init__(self, data):
        self.simple_log = data
        self.good_log = []
        self.start = None
        self.end = None
        self.num_clicks = None
        self.days = {}              # чистые данные по дням
        self.sessions = []          # просто массив сессий в виде (начало, конец, [запросы])
        self.result = {}            # формирование результирующего ответа
        self.frequent_urls = []
        self.frequent_domains = []

    def _days(self):
        # после данной функции мы получаем даные без мусора в формате:
        # { день: [(полное время, [информация о клике]), ...],
        #   день2: [...],
        #   ...
        # }
        day = None
        for line in self.simple_log:
            try:
                lock_day = datetime.strptime(line[0], '%d.%m.%Y')
                time = datetime.strptime(line[0]+" "+line[1], '%d.%m.%Y %H:%M:%S')
                if day == lock_day:
                    self.days[day].append((time, line[2:]))
                else:
                    day = lock_day
                    self.days[day] = [(time, line[2:])]
                self.good_log.append((time, line[2:]))
            except:
                if line[0] != "\n":
                    del self.days[day][-1]

        time = self.simple_log[0][0] +" "+self.simple_log[0][1]
        self.start = datetime.strptime(time, '%d.%m.%Y %H:%M:%S')
        time2 = self.simple_log[-1][0] + " " + self.simple_log[-1][1]
        self.end = datetime.strptime(time2, '%d.%m.%Y %H:%M:%S')

    def _sessions(self):
        session = []
        start = None
        time = None
        for day in self.days:
            for line in self.days[day]:
                # начало сессии
                if time == None or line[0]-time >= timedelta(seconds=1800):
                    if session:
                        self.sessions.append((start, time, session))
                    start = line[0]
                    session = [line]
                    time = line[0]
                else:
                    session.append(line)
                    time = line[0]

    def starting_treatment(self):
        # самая общая информация о логе, которая могла вас интересовать
        self.num_clicks = len(self.good_log)
        self.result['всего записей'] = self.num_clicks
        self.result['начало записи лога'] = str(self.start)
        self.result['конец записи лога'] = str(self.end)
        time = self.end - self.start
        self.result['длительность снятия данных'] = str(time)
        self.result['количество сессий'] = len(self.sessions)
        print(json.dumps(self.result, ensure_ascii=False))

    def activity_analyse(self):
        # распределение активности по дням недели
        week = {}
        for day in self.days:
            if day.weekday() in week:
                week[day.weekday()] += len(self.days[day])
            else:
                week[day.weekday()] = len(self.days[day])
        for weekday in week:
            week[weekday] = week[weekday]/self.num_clicks
        self.result['распределение по дням недели'] = week

        # распределение активности по времени суток
        d_time = {}
        for line in self.good_log:
            time = line[0].hour//int(24/TIMES_OF_DAY)
            if time in d_time:
                d_time[time] += 1
            else:
                d_time[time] = 1
        for time in d_time:
            d_time[time] = d_time[time]/self.num_clicks
        self.result['распределение по времени суток'] = d_time

        # время запуска chrome после входа в систему
        start_brows = {}
        start_brows_min = {}
        starts = 0
        starts_min = 0
        time = None
        for line in self.good_log:
            if line[1][1] == "start\n":
                starts += 1
                time = line[0]
                continue
            if time:
                pause = line[0]-time
                pause_key = pause.seconds//TOTAL_SECONDS
                if pause_key in start_brows:
                    start_brows[pause_key] += 1
                else:
                    start_brows[pause_key] = 1
                if pause.seconds <= 60:
                    starts_min += 1
                    pause_key = pause.seconds//TOTAL_SECONDS_IN_MIN
                    if pause_key in start_brows_min:
                        start_brows_min[pause_key] += 1
                    else:
                        start_brows_min[pause_key] = 1
                time = None
        self.result['количество пауз между запуском компа и браузера'] = start_brows
        self.result['количество пауз между запуском компа и браузера(минута)(в количестве)'] = start_brows_min
        for pause in start_brows:
            start_brows[pause] = start_brows[pause]/starts
        for pause_key in start_brows_min:
            start_brows_min[pause_key] = start_brows_min[pause_key]/starts_min
        self.result['распределение пауз между запуском компа и браузера'] = start_brows
        self.result['распределение пауз между запуском компа и браузера(минута)'] = start_brows_min

        # наиболее частые урлы
        # наиб частые домены
        urls = {}
        domains = {}
        n_urls = 0  # количство разных урлов

        for line in self.good_log:
            if len(line[1]) == 3:
                url = line[1][2][:-1]
                n_urls += 1
                if url in urls:
                    urls[url] += 1
                else:
                    urls[url] = 1
                domain = url.split("/")
                if len(domain) >= 3 and domain[2]:
                    if domain[2] in domains:
                        domains[domain[2]] += 1
                    else:
                        domains[domain[2]] = 1

        n_urls = {}
        mass = []
        for url in urls:
            if urls[url] in n_urls:
                n_urls[urls[url]].append(url)
            else:
                n_urls[urls[url]] = [url]
                mass.append(urls[url])
        mass.sort()
        mass = mass[::-1]
        mass = mass[:NUMBER_FREQUENT_URL]
        urls = {}
        for n in mass:
            urls[n] = n_urls[n]
            self.frequent_urls.extend(n_urls[n])
        self.result['частые url'] = start_brows_min

        n_domains = {}
        mass = []
        for domain in domains:
            if domains[domain] in n_domains:
                n_domains[domains[domain]].append(domain)
            else:
                n_domains[domains[domain]] = [domain]
                mass.append(domains[domain])
        mass.sort()
        mass = mass[::-1]
        mass = mass[:NUMBER_FREQUENT_DOMAINS]
        domains = {}
        for n in mass:
            domains[n] = n_domains[n]
            self.frequent_domains.extend(n_domains[n])
        self.result['частые домены'] = start_brows_min

    # def click_analyse(self):
    #     matrix_d = {}
    #     for line in self.good_log:
    #
    #         for domain in self.frequent_domains:
    #             matrix = np.zeros((HEIGHT, WIDTH))

    def check(self):
        self._days()
        self._sessions()
        self.starting_treatment()
        self.activity_analyse()
        #self.click_analyse()

if __name__ == "__main__":
    with open('log.txt') as file:
            data = [line.split('\t') for line in file]
    f = LogCheck(data)
    f.check()