"""
Здесь находятся дополнительные функции, которые могут быть использованы
"""
import itertools
import os
import time

from analyse.models import Teams, VectorsOneVersion, Collections
from base.constants import classification_algorithms, regression_algorithms, patterns
from ML.create_vectors_in_two_files import CreateVectorsDB
from ML.ML import classification, regression


def create_dirname(path):
    # проверяем наличие папки для результатов и возвращаем путь
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            i = 0
            while True:
                try:
                    i += 1
                    path = path[:path.rfind("\\")+2] + path[len(path)-150:] + str(i)
                    os.makedirs(path)
                    break
                except:
                    print(i)

    #return path
    return ""

def create_vectors(clicks, day_parts, teams):
    """
    В зависимости от режима запускает или формирование выборок, или запускает МО.
    """
    start_time = time.time()
    for team in teams:
        for day_part in day_parts:
            for n_click in clicks:
                thousand = Teams.objects.filter(team=team).values_list('thousand')[0][0]
                names = [name[0] for name in Teams.objects.filter(team=team).values_list('username')]
                key = {'team': team, 'number_parts_per_day': day_part, 'clicks': n_click, 'thousand': thousand,
                       'users_quantity': len(names)}
                if Collections.objects.filter(**key):
                    collection = Collections.objects.get(**key)
                    VectorsOneVersion.objects.filter(collection=collection).delete()
                else:
                    col = Collections.objects.create(**key)
                    col.save()

                data = (thousand, int(thousand/0.7))
                CreateVectorsDB(data, names, col)
    msg = "Завершено. Время выполнения: %s seconds ---" % (time.time() - start_time)
    print(msg)

def train(collections, list_permission, algorithms):
    """
    В зависимости от режима запускает или формирование выборок, или запускает МО.
    """
    start_time = time.time()
    for collection in collections:
        team = collection[0]
        thousand = collection[1]
        day_part = collection[2]
        n_click = collection[3]

        # сюда буду сохранять более подробные отчеты
        #path = create_dirname(str(".\\dataset2\\") + str(team) + " perm " + str(list_permission) + " " + \
          #                    str(day_part) + "t " + str(n_click) + "cl " + str(thousand))
        names = [name[0] for name in VectorsOneVersion.objects.filter(team=team, thousand=thousand, number_parts_per_day=day_part, clicks=n_click).
            distinct('username').values_list('username')]
        print("!!!!")
        info = {'team': team, 'clicks': n_click, 'number_parts_per_day': day_part, 'thousand': thousand}
        if any([True if i in classification_algorithms else False for i in algorithms]):
            classification(names, list_permission, algorithms, info)
        if any([True if i in regression_algorithms else False for i in algorithms]):
            regression(names, list_permission, algorithms, info)
    msg = "Завершено. Время выполнения: %s seconds ---" % (time.time() - start_time)
    print(msg)
    #messagebox.showerror("Выполнено", msg)


def get_better_patterns(collections):
    for i in collections:
        col = Collections.objects.get(pk=i[0])

        for l in range(1, len(patterns)+1):
            for j in itertools.combinations(patterns, l):
                patterns_list = list(j)
                print(patterns_list)
                names = [name[0] for name in Teams.objects.filter(team=col.team).values_list('username')]
                algorithms = ['rf']
                info = {'collection': col}
                classification(names, patterns_list, algorithms, info)




