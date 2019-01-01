import numpy as np
from datetime import datetime as timedelta

from analyse.models import Log, Vectors

PERIOD = 30
CLICKS = 20

class CreateVectors(object):
    def __init__(self, name, ):
        self.user = name
        self.finish_time = Log.objects.filter(username=self.user).earliest('time').time + timedelta(days=PERIOD)
        self.urls = []
        self.domains = []

    def up_data(self):
        """
        достаем данные для определения полей
        """
        r_dict = np.load(self.user+'_otch.npy').item()
        self.urls = r_dict['частые url']
        self.domains = r_dict['частые домены']

        self.url_bigrams = [k.split(', ') for k in r_dict['url биграммы']]
        self.dom_bigrams = [k.split(', ') for k in r_dict['domain биграммы']]
        self.url_trigrams = [k.split(', ') for k in r_dict['url триграммы']]
        self.dom_trigrams = [k.split(', ') for k in r_dict['domain триграммы']]

    def start(self, name):
        log = Log.objects.filter(username=name)
        current_time = log.earliest('time').time
        while current_time < self.finish_time:
            values = log.filter(time__gte=current_time)[:20].values()
            current_time = log.filter(time__gte=current_time)[20].time

            # день и время берем по медиане
            vector_times = [i['time'] for i in values]
            vector_times.sort()
            vector_time = vector_times[9]
            v_day = vector_time.date().weekday()
            v_time = vector_time.hour // 8

            # счиатаем, сколько раз был на частых урлах и доменах
            urls = {i : 0 for i in range(20)}
            domains = {i : 0 for i in range(20)}
            user_urls = [i['url'] for i in values]
            for i in user_urls:
                if i in self.urls:
                    urls[self.urls.index(i)] += 1
            user_domains = [i['domain'] for i in values]
            for i in user_domains:
                if i in self.domains:
                    domains[self.domains.index(i)] += 1

            # если был факт старта компа
            start = 0
            starts = [i['start_computer'] for i in values]
            if any(starts):
                times = starts = [i['time'] for i in values]
                for i in range(CLICKS):
                    if starts[i]:
                        start += 1
                        deviation = 1 - 1/(times[i+1] - times[i]).seconds

            # проверяем наличие биграмм и триграмм
            url_bi = {i: 0 for i in range(len(self.url_bigrams))}
            dom_bi = {i: 0 for i in range(len(self.dom_bigrams))}
            url_tri = {i: 0 for i in range(len(self.url_bigrams))}
            dom_tri = {i: 0 for i in range(len(self.dom_bigrams))}
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
                    if d in self.dom_bigrams:
                        dom_tri[self.dom_bigrams.index(d)] += 1

            Vectors.objects.create(
                username=name,
                WeekDay=v_day,
                Time=v_time,
                url0 = urls[0],
                url1 = urls[1],
                url2 = urls[2],
                url3 = urls[3],
                url4 = urls[4],
                url5 = urls[5],
                url6 = urls[6],
                url7 = urls[7],
                url8 = urls[8],
                url9 = urls[9],
                url10 = urls[10],
                url11 = urls[11],
                url12 = urls[12],
                url13 = urls[13],
                url14 = urls[14],
                url15 = urls[15],
                url16 = urls[16],
                url17 = urls[17],
                url18 = urls[18],
                url19 = urls[19],
                dom0 = domains[0],
                dom1 = domains[1],
                dom2 = domains[2],
                dom3 = domains[3],
                dom4 = domains[4],
                dom5 = domains[5],
                dom6 = domains[6],
                dom7 = domains[7],
                dom8 = domains[8],
                dom9 = domains[9],
                dom10 = domains[10],
                dom11 = domains[11],
                dom12 = domains[12],
                dom13 = domains[13],
                dom14 = domains[14],
                dom15 = domains[15],
                dom16 = domains[16],
                dom17 = domains[17],
                dom18 = domains[18],
                dom19 = domains[19],
                start = start,
                deviation = deviation,

                bi0 = dom_bi[0],
                bi1 = dom_bi[1],
                bi2 = dom_bi[2],
                bi3 = dom_bi[3],
                bi4 = dom_bi[4],
                bi5 = dom_bi[5],
                bi6 = dom_bi[6],
                bi7 = dom_bi[7],
                bi8 = dom_bi[8],
                bi9 = dom_bi[9],
                bi10 = dom_bi[10],
                bi11 = dom_bi[11],
                bi12 = dom_bi[12],
                bi13 = dom_bi[13],
                bi14 = dom_bi[14],

                # триграммы
                tri0 = dom_tri[0],
                tri1 = dom_tri[0],
                tri2 = dom_tri[0],
                tri3 = dom_tri[0],
                tri4 = dom_tri[0],
                tri5 = dom_tri[0],
                tri6 = dom_tri[0],
                tri7 = dom_tri[0],
                tri8 = dom_tri[0],
                tri9 = dom_tri[0]
            )






















