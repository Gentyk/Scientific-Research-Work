from analyse.models import Log
from datetime import datetime as dd
from pytz import timezone

NAME="IAM"

with open('log.txt') as file:
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
        window_coordinates = str(line[3])
        cursor_coordinates = str(line[2])
        url = line[4]
        if url == "":
            domain = ""
        elif len(url.split('/')) > 2:
            domain = url.split('/')[2]
        else:
            domain = url.split('/')[1]
        if seance == -1 or last_active_time != None and (time - last_active_time).seconds > 1800:
            seance += 1
        p = Log(day=day, time=time, local_time=local_time, username=NAME, window_coordinates=window_coordinates,
                cursor_coordinates=cursor_coordinates, url=url, domain=domain, seance=seance)
        p.save()
        last_active_time = time
    except:
        pass