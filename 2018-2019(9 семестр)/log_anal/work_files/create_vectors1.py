import csv
import numpy as np
from datetime import datetime, timedelta

from analyse.models import Log, Vectors

PERIOD = 30
CLICKS = 20

class CreateVectors(object):
    def __init__(self, name):
        self.user = name
        self.finish_time = None
        self.urls = []
        self.domains = []

    def run(self, bad_users):
        self.up_data()

        print('user ' + self.user + ' start writing')
        self.write_in_csv(self.user)
        print('user ' + self.user + ' success writing')

        for i in bad_users:
            print('user ' + i + ' start writing')
            self.write_in_csv(i)
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

    def write_in_csv(self, name):
        """
        Записывает в csv вектора пользователя name за период PERIOD
        """
        log = Log.objects.filter(username=name)
        self.finish_time = log.earliest('time').time + timedelta(days=PERIOD)
        current_time = log.earliest('time').time
        all_values = log.filter(time__lte=self.finish_time).filter(time__gte=current_time).order_by('id').values()
        size = log.filter(time__lte=self.finish_time).filter(time__gte=current_time).count()

        with open('.\\users\\vnames.csv', 'a', newline='') as csvfile:

            flag = True
            old_day = current_time.day
            for ind in range(0, size - CLICKS, CLICKS):
                res = {'username': name}
                values = all_values[ind: ind+CLICKS]
                current_time = values[0]['time']

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
                urls = [0 for i in range(len(self.urls))]
                domains = [0 for i in range(len(self.domains))]
                user_urls = [i['url'] for i in values]
                for i in user_urls:
                    if i in self.urls:
                        urls[self.urls.index(i)] += 1
                for i in range(len(urls)):
                    res['u' + str(i)] = urls[i]
                user_domains = [i['domain'] for i in values]
                for i in user_domains:
                    if i in self.domains:
                        domains[self.domains.index(i)] += 1
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




















