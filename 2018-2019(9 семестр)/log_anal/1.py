from datetime import datetime as dd
from os import listdir
from os.path import isfile, join
from pytz import timezone

from analyse.models import Log


def filling_bd(NAME):
    with open('.\\users\\'+NAME+'.txt') as file:
        data = [line for line in file]
    last_active_time = None
    seance = -1
    for line_d in data:
        try:
            line = line_d.split('\t')
            day = dd.strptime(line[0], '%d.%m.%Y')
            day = day.replace(tzinfo=timezone('UTC'))
            time = dd.strptime(line[0] + " " + line[1], '%d.%m.%Y %H:%M:%S')
            time = time.replace(tzinfo=timezone('UTC'))
            local_time = dd.strptime(line[1], '%H:%M:%S')
            local_time = local_time.replace(tzinfo=timezone('UTC'))
            # фиксируем начало работы системы
            if line[3] == 'start\n':
                seance += 1
                p = Log(day=day, time=time, local_time=local_time, username=NAME, seance=seance, start_computer=True)
                p.save()
                last_active_time = time
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
            url = line[4]
            if url == "":
                domain = ""
            elif len(url.split('/')) > 2:
                domain = url.split('/')[2]
            else:
                domain = url.split('/')[1]
            if seance == -1 or last_active_time != None and (time - last_active_time).seconds > 1800:
                seance += 1
            p = Log(
                day=day,
                time=time,
                local_time=local_time,
                username=NAME,
                x_cursor_coordinates=x_cur,
                y_cursor_coordinates=y_cur,
                x1_window_coordinates=x1_w,
                y1_window_coordinates=y1_w,
                x2_window_coordinates=x2_w,
                y2_window_coordinates=y2_w,
                url=url,
                domain=domain,
                seance=seance)
            p.save()
            last_active_time = time
        except:
            pass

#if __name__ == '__main__':
names = [f.split('.')[0] for f in listdir('users') if isfile(join('users', f))]
for name in names:
    filling_bd(name)