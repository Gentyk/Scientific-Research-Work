"""
Здесь находятся дополнительные функции, которые могут быть использованы
"""
import itertools
import os
import time

from analyse.models import Teams, VectorsOneVersion1, Collections, Patterns, ML
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
    array_coll = []
    for team in teams:
        for day_part in day_parts:
            for n_click in clicks:
                thousand = Teams.objects.filter(team=team).values_list('thousand')[0][0]
                names = [name[0] for name in Teams.objects.filter(team=team).values_list('username')]
                key = {'team': team, 'number_parts_per_day': day_part, 'clicks': n_click, 'thousand': thousand,
                       'users_quantity': len(names)}
                if Collections.objects.filter(**key):
                    col = Collections.objects.get(**key)
                    VectorsOneVersion1.objects.filter(collection=col).delete()
                else:
                    col = Collections.objects.create(**key)
                    col.save()

                if not col in array_coll:
                    array_coll.append(col)

                data = (thousand, int(thousand/0.7))
                CreateVectorsDB(data, names, col)
    msg = "Завершено. Время выполнения: %s seconds ---" % (time.time() - start_time)
    print(msg)
    train(array_coll, ['5 best patterns set'], ['rf'])



def train(collections, list_permission, algorithms):
    """
    В зависимости от режима запускает или формирование выборок, или запускает МО.
    """
    print(list_permission)
    start_time = time.time()
    for collection in collections:
        print("!!!!")

        if ['5_best_patterns_set'] == list_permission:
            """к сожалению я стер лучшее, поэтому костыль ниже
            percent = [i[0] for i in ML.objects.values_list('accuracy')]
            percent.sort(reverse=True)
            percent = set(percent[:5])
            for i in percent:
                best_patterns = [i[0] for i in ML.objects.filter(accuracy=i).values_list('patterns')]
                for pat in best_patterns:
                    if any([True if i in classification_algorithms else False for i in algorithms]):
                        classification(names, pat, algorithms, info)
                    if any([True if i in regression_algorithms else False for i in algorithms]):
                        regression(names, pat, algorithms, info)
            """
            best_patterns = [i[0] for i in Patterns.objects.values_list('patterns')]
            best_patterns = best_patterns[:5]
            print(best_patterns)
            for pat in best_patterns:
                if any([True if i in classification_algorithms else False for i in algorithms]):
                    classification(collection, pat, algorithms)
                if any([True if i in regression_algorithms else False for i in algorithms]):
                    regression(collection, pat, algorithms)

        else:
            if any([True if i in classification_algorithms else False for i in algorithms]):
                classification(collection, list_permission, algorithms)
            if any([True if i in regression_algorithms else False for i in algorithms]):
                regression(collection, list_permission, algorithms)
    msg = "Завершено. Время выполнения: %s seconds ---" % (time.time() - start_time)
    print(msg)
    #messagebox.showerror("Выполнено", msg)


def get_better_patterns(collections):
    for i in collections:
        col = Collections.objects.get(pk=i[0])

        pats = [i[0] for i in Patterns.objects.all().values_list('patterns')]
        patterns_array = [
            ['url_bi', 'url_bi_pauses', 'dom_bi', 'dom_bi_pauses'],
            ['url_tri', 'url_tri_pauses', 'dom_tri', 'dom_tri_pauses'],
            ['middle_pause2', 'middle_pause3', 'quantity_middle_pause', 'quantity_middle_pause2', 'quantity_middle_pause3']
        ]
        for patterns1 in patterns_array:
            for pat in pats:
                for l in range(1, len(patterns1)+1):
                    for j in itertools.combinations(patterns1, l):
                        patterns_list = list(set(list(j) + pat))
                        print(patterns_list)
                        names = [name[0] for name in Teams.objects.filter(team=col.team).values_list('username')]
                        algorithms = ['rf']
                        info = {'collection': col}
                        print(names)
                        classification(names, patterns_list, algorithms, info)

            mass = [i[0] for i in ML.objects.all().values_list('accuracy')]
            mass.sort()
            ML.objects.filter(accuracy__lt=mass[len(mass)-100]).delete()
            Patterns.objects.all().delete()
            for pat in ML.objects.all().values_list('patterns'):
                p = Patterns.objects.create(patterns=pat[0])
                p.save()
    print('завершено')




