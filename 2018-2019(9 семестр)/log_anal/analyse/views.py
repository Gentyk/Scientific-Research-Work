from datetime import datetime, timedelta
from pytz import timezone
from os import listdir
from os.path import isfile, join
import time
import re

from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse

from analyse.models import Bigrams, Log, Trigrams, URLs

# Create your views here.
class LogView(View):
    """
    Отвечает за заполнение базы данных из файла лога
    """
    def post(self, request, *args, **kwargs):
        Log.objects.all().delete()
        names = [f.split('.')[0] for f in listdir('logs') if isfile(join('logs', f))]
        for name in names:
            start_time = time.time()
            with open('.\\logs\\' + name + '.txt') as file:
                data = [line for line in file]
            last_active_time = None
            seance = -1
            thousand = 0
            num_in_thousand = 0
            for line_d in data:
                try:
                    line = line_d[:len(line_d) - 2]
                    line = line.split('\t')
                    day = datetime.strptime(line[0], '%d.%m.%Y')
                    day = day.replace(tzinfo=timezone('UTC'))
                    time1 = datetime.strptime(line[0] + " " + line[1], '%d.%m.%Y %H:%M:%S')
                    time1 = time1.replace(tzinfo=timezone('UTC'))
                    local_time = datetime.strptime(line[1], '%H:%M:%S')
                    local_time = local_time.replace(tzinfo=timezone('UTC'))
                    # фиксируем начало работы системы
                    if line[3] == 'start':
                        seance += 1
                        p = Log(day=day, time=time1, local_time=local_time, username=name, seance=seance,
                                start_computer=True)
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
                    p = Log(
                        day=day,
                        time=time1,
                        local_time=local_time,
                        username=name,
                        x_cursor_coordinates=x_cur,
                        y_cursor_coordinates=y_cur,
                        x1_window_coordinates=x1_w,
                        y1_window_coordinates=y1_w,
                        x2_window_coordinates=x2_w,
                        y2_window_coordinates=y2_w,
                        url=url,
                        domain=domain,
                        seance=seance,
                        thousand=thousand
                    )
                    p.save()
                    last_active_time = time1
                except ValueError:  # непонятная ошибка границы месяца
                    pass
                except Exception as e:
                    print(e)
                    print(line)
            print("Log--[OK]--- %s seconds ---" % (time.time() - start_time))
        return {"status": "ok"}


class UserView(View):
    """
    Находит частные штучкки пользователей и заносит их в базу данных. По требованию достает инфу о каждом доступном
    пользователе.
    """

    def get(self, request, *args, **kwargs):
        with open(".\\vova", "w") as f:
            f.write("ddd")
        return HttpResponse("Hello, world. You're at the polls index.")
