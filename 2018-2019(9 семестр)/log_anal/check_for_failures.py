from os import listdir
from os.path import isfile, join
from datetime import datetime as dd
from pytz import timezone

names = [f.split('.')[0] for f in listdir('logs') if isfile(join('logs', f))]
for name in names:
    print("Start check %s data"%name)
    with open('.\\logs\\' + name + '.txt') as file:
        data = [line for line in file]
    last_active_time = None
    seance = -1
    old_time = None
    for line_d in data:
        try:
            line = line_d.split('\t')
            s = "sds"
            time = dd.strptime(line[0], '%d.%m.%Y')
            if old_time and time<old_time:
                print(old_time)
                print(time)
                cc = input()
            else:
                old_time = time
        except ValueError:
             pass



    print("Successful check %s data" % name)