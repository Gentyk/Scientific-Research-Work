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

    def run(self):
        Vectors.objects.all().delete()
        self.up_data()
        bad_user = 'bv'
        print('user1 start')
        self.start(self.user)
        print('user2 start')
        self.start(bad_user)

    def up_data(self):
        """
        достаем данные для определения полей
        """
        r_dict = np.load('.\\users\\'+self.user+'_otch.npy').item()
        self.urls = r_dict['частые url']
        self.domains = r_dict['частые домены']

        self.url_bigrams = [k.split(', ') for k in r_dict['url биграммы']]
        self.dom_bigrams = [k.split(', ') for k in r_dict['domain биграммы']]
        self.url_trigrams = [k.split(', ') for k in r_dict['url триграммы']]
        self.dom_trigrams = [k.split(', ') for k in r_dict['domain триграммы']]

        # подробнее
        # print(len(self.urls))
        # print(len(self.domains))
        # print(len(self.url_bigrams))
        # print(len(self.dom_bigrams))
        # print(len(self.url_trigrams))
        # print(len(self.dom_trigrams))

    def start(self, name):
        """
        Записывает в таблицу данные пользователя name за период PERIOD
        :param name:
        :return:
        """
        log = Log.objects.filter(username=name)
        self.finish_time = log.earliest('time').time + timedelta(days=PERIOD)
        current_time = log.earliest('time').time
        print(current_time)
        print(self.finish_time)
        all_values = log.filter(time__lte=self.finish_time).filter(time__gte=current_time).order_by('id').values()
        size = log.filter(time__lte=self.finish_time).filter(time__gte=current_time).count()
        old_day = current_time.day
        for ind in range(0, size - CLICKS, CLICKS):
            values = all_values[ind: ind+CLICKS]
            current_time = values[0]['time']

            if old_day != current_time.day:
                print("!"+str(current_time))
                old_day = current_time.day

            # день и время берем по медиане
            vector_times = [i['time'] for i in values]
            vector_times.sort()
            vector_time = vector_times[9]
            v_day = vector_time.weekday()
            v_time = vector_time.hour // 8

            # счиатаем, сколько раз был на частых урлах и доменах
            urls = [0 for i in range(len(self.urls))]
            domains = [0 for i in range(len(self.domains))]
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
            deviation = 0
            starts = [i['start_computer'] for i in values]
            if any(starts):
                times = [(i['time'], i['url']) for i in values]
                for i in range(CLICKS):
                    if starts[i] and i+1<CLICKS and times[i+1][1]:
                        start += 1
                        deviation = (times[i+1][0] - times[i][0]).seconds

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

            try:
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
                tri1 = dom_tri[1],
                tri2 = dom_tri[2],
                tri3 = dom_tri[3],
                tri4 = dom_tri[4],
                tri5 = dom_tri[5],
                tri6 = dom_tri[6],
                tri7 = dom_tri[7],
                tri8 = dom_tri[8],
                tri9 = dom_tri[9],
                )
            except:
                print(len(domains))
                print(len(urls))
                print(len(dom_bi))
                print(len(dom_tri))
                raise

    def f_write(self):
        items = Vectors.objects.all()
        with open('.\\users\\vnames.csv', 'w', newline='') as csvfile:


        #response['Content-Disposition'] = 'attachment; filename="vectors.csv"'
            #writer = csv.writer('attachment', '.\\users\\fuck.csv', delimiter=',')
            fieldnames = [
                             'username', 'weekday', 'daytime',
                             'u0', 'u1', 'u2', 'u3', 'u4',
                             'u5', 'u6', 'u7', 'u8', 'u9',
                             'u10', 'u11', 'u12', 'u13', 'u14',
                             'u15', 'u16', 'u17', 'u18', 'u19',
                             'd0', 'd1', 'd2', 'd3', 'd4',
                             'd5', 'd6', 'd7', 'd8', 'd9',
                             'd10', 'd11', 'd12', 'd13', 'd14',
                             'd15', 'd16', 'd17', 'd18', 'd19',
                             'start', 'dev',

                             'bi0', 'bi1', 'bi2', 'bi3', 'bi4',
                             'bi5', 'bi6', 'bi7', 'bi8', 'bi9',
                             'bi10', 'bi11', 'bi12', 'bi13', 'bi14',

                             'tri0', 'tri1', 'tri2', 'tri3', 'tri4',
                             'tri5', 'tri6', 'tri7', 'tri8', 'tri9']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for obj in items:
                writer.writerow({
                    'username':obj.username,
                    'weekday':obj.WeekDay,
                    'daytime':obj.Time,
                    'u0':obj.url0,
                    'u1':obj.url1,
                    'u2':obj.url2,
                    'u3':obj.url3,
                    'u4':obj.url4,
                    'u5':obj.url5,
                    'u6':obj.url6,
                    'u7':obj.url7,
                    'u8':obj.url8,
                    'u9':obj.url9,
                    'u10':obj.url10,
                    'u11':obj.url11,
                    'u12':obj.url12,
                    'u13':obj.url13,
                    'u14':obj.url14,
                    'u15':obj.url15,
                    'u16':obj.url16,
                    'u17':obj.url17,
                    'u18':obj.url18,
                    'u19':obj.url19,

                    'd0':obj.dom0,
                    'd1':obj.dom1,
                    'd2':obj.dom2,
                    'd3':obj.dom3,
                    'd4':obj.dom4,
                    'd5':obj.dom5,
                    'd6':obj.dom6,
                    'd7':obj.dom7,
                    'd8':obj.dom8,
                    'd9':obj.dom9,
                    'd10':obj.dom10,
                    'd11':obj.dom11,
                    'd12':obj.dom12,
                    'd13':obj.dom13,
                    'd14':obj.dom14,
                    'd15':obj.dom15,
                    'd16':obj.dom16,
                    'd17':obj.dom17,
                    'd18':obj.dom18,
                    'd19':obj.dom19,

                    'start':obj.start,
                    'dev':obj.deviation,

                    'bi0':obj.bi0,
                    'bi1':obj.bi1,
                    'bi2':obj.bi2,
                    'bi3':obj.bi3,
                    'bi4':obj.bi4,
                    'bi5':obj.bi5,
                    'bi6':obj.bi6,
                    'bi7':obj.bi7,
                    'bi8':obj.bi8,
                    'bi9':obj.bi9,
                    'bi10':obj.bi10,
                    'bi11':obj.bi11,
                    'bi12':obj.bi12,
                    'bi13':obj.bi13,
                    'bi14':obj.bi14,

                    'tri0':obj.tri0,
                    'tri1':obj.tri1,
                    'tri2':obj.tri2,
                    'tri3':obj.tri3,
                    'tri4':obj.tri4,
                    'tri5':obj.tri5,
                    'tri6':obj.tri6,
                    'tri7':obj.tri7,
                    'tri8':obj.tri8,
                    'tri9':obj.tri9
                })




















