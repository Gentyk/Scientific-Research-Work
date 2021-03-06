# заполняет БД данными из папки logs
from datetime import datetime as dd
from os import listdir
from os.path import isfile, join
import time
import re

from pytz import timezone

from analyse.models import Bigrams, Log, Trigrams, Domains, URLs, Clicks

def filling():
    start_time = time.time()
    Clicks.objects.all().delete()
    Bigrams.objects.all().delete()
    Log.objects.all().delete()
    Trigrams.objects.all().delete()
    log_names = [f.split('.')[0] for f in listdir('logs') if isfile(join('logs', f))]
    for name in log_names:
        Filling(name)
    msg = "В базу данных внесены данные пользователей за время: %s seconds ---" % (
    time.time() - start_time)
    print(msg)

class Filling(object):
    def __init__(self, name):
        self.name = name
        self.start_time = None

        self.filling_bd()
        #self.filling_categories()
        self.filling_bigram_table()

    def check_obj(self, model, obj_type, obj_name):
        d = {obj_type: obj_name}
        try:
            obj = model.objects.get(**d)
        except:
            obj = model.objects.create(**d)
            obj.save()
        return obj

    def filling_bd(self):

        with open('.\\logs\\'+self.name+'.txt') as file:
            data = [line for line in file]
        last_active_time = None
        seance = -1
        thousand = 0
        num_in_thousand = 0
        for line_d in data:
            try:
                line = line_d.split('\n')[0]
                line = line.split('\t')
                day = dd.strptime(line[0], '%d.%m.%Y')
                day = day.replace(tzinfo=timezone('UTC'))
                time1 = dd.strptime(line[0] + " " + line[1], '%d.%m.%Y %H:%M:%S')
                time1 = time1.replace(tzinfo=timezone('UTC'))
                local_time = dd.strptime(line[1], '%H:%M:%S')
                local_time = local_time.replace(tzinfo=timezone('UTC'))
                # фиксируем начало работы системы
                if line[3] == 'start':
                    seance += 1
                    click = Clicks.objects.create(
                        time=time1,
                        url=Domains.objects.all()[0],
                        domain=URLs.objects.all()[0],
                    )
                    click.save()
                    p = Log(day=day, click=click, local_time=local_time, username=self.name, seance=seance, start_computer=True)
                    p.save()
                    last_active_time = time1
                    continue
                # и обычные url
                window_coordinates = (line[3][1:-1]).split(';')
                x1_w = int(window_coordinates[0][1:])
                x2_w = int(window_coordinates[2][1:])
                y1_w = int(window_coordinates[1][:-1])
                y2_w = int(window_coordinates[3][:-1])
                cursor_coordinates = (line[2][1:-1]).split(';')
                x_cur = int(cursor_coordinates[0])
                y_cur = int(cursor_coordinates[1])
                if len(line) == 4:
                    url = ""
                else:
                    url = line[4]
                if url == "":
                    domain = ""
                elif re.match(r'(http|https|ftp):\/\/', url) and len(url.split('/')) > 2:
                    domain = url.split('/')[2]
                elif len(url.split('/')) == 1:
                    domain = url[:90]
                else:
                    domain = url.split('/')[0]
                if seance == -1 or last_active_time and (time1 - last_active_time).seconds > 1800:
                    seance += 1
                if len(url) > 2700:
                    url = url[:1000]
                if len(domain) > 95:
                    domain = domain[:90]
                num_in_thousand += 1
                if num_in_thousand >= 1000:
                    num_in_thousand = 0
                    thousand += 1

                domain_obj = self.check_obj(Domains, 'domain', domain)
                url_obj = self.check_obj(URLs, 'url', url)
                click = Clicks.objects.create(
                    time=time1,
                    url=url_obj,
                    domain=domain_obj,
                )
                click.save()

                p = Log(
                    day=day,
                    local_time=local_time,
                    click=click,

                    x_cursor_coordinates=x_cur,
                    y_cursor_coordinates=y_cur,
                    x1_window_coordinates=x1_w,
                    y1_window_coordinates=y1_w,
                    x2_window_coordinates=x2_w,
                    y2_window_coordinates=y2_w,

                    seance=seance,
                    thousand=thousand,
                    username=self.name,
                )
                p.save()
                last_active_time = time1
            except ValueError:              # непонятная ошибка границы месяца
                pass
            except Exception as e:
                raise e


    # def filling_categories(self):
    #     urls = Log.objects.values('url').distinct()
    #     diffbot = DiffbotClient()
    #     token = '18aa09158e10b70ac108c941f060c99a'
    #     for i, url in urls.items():
    #         try:
    #             u = URLs.objects.get(url=url)
    #         except:
    #             api = "product"
    #             response = diffbot.request(url, token, api)
    #             try:
    #                 category = response['objects'][0]['category']
    #             except:
    #                 category = ""
    #
    #             api = "analyze"
    #             response = diffbot.request(url, token, api)
    #             type = response['type']
    #             URLs.objects.create(
    #                 url=url,
    #                 type=type,
    #                 category=category,
    #             )

    def filling_bigram_table(self):
        log = Log.objects.filter(username=self.name).filter(start_computer=False)
        start = log.earliest('seance').seance
        end = log.latest('seance').seance
        for i in range(start, end+1):
            values = log.filter(seance=i).order_by('id')
            n = len(values)
            if n > 1:
                for j in range(n-3):
                    Bigrams.objects.create(
                        seance=i,
                        username=self.name,
                        click1=values[j].click,
                        click2=values[j + 1].click,
                        )
                    if values[j].click.url != values[j + 1].click.url or values[j + 2].click.url != values[j + 1].click.url:
                        Trigrams.objects.create(
                            seance=i,
                            username=self.name,
                            click1=values[j].click,
                            click2=values[j + 1].click,
                            click3=values[j + 2].click,
                        )
                Bigrams.objects.create(
                    seance=i,
                    username=self.name,
                    click1=values[n - 2].click,
                    click2=values[n - 1].click,
                )