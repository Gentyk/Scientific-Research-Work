"""
Здесь находятся дополнительные функции, которые могут быть использованы
"""
import itertools
import os
import time

from analyse.models import Teams, VectorsOneVersion1, Collections, Patterns, ML, AnomalyML
from base.constants import classification_algorithms, regression_algorithms, patterns, V
from ML.create_vectors_in_two_files import CreateVectorsDB
from ML.ML import classification, regression
from ML.new_ML import Classification
from ML.anomaly import Anomaly


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
                thousands = [i[0] for i in Teams.objects.filter(team=team).values_list('thousand')]
                vectors_number = round(sum(thousands) / len(thousands) / n_click * 1000)
                names = [name[0] for name in Teams.objects.filter(team=team).values_list('username')]

                key = {'team': team,
                       'number_parts_per_day': day_part,
                       'clicks': n_click,
                       'num_vectors': vectors_number,
                       'users_quantity': len(names)}
                if Collections.objects.filter(**key):
                    col = Collections.objects.get(**key)
                    VectorsOneVersion1.objects.filter(collection=col).delete()
                else:
                    col = Collections.objects.create(**key)
                    col.save()

                if not col in array_coll:
                    array_coll.append(col)

                data = (round(sum(thousands) / len(thousands)), int(sum(thousands) / len(thousands)/0.7))
                CreateVectorsDB(data, names, col)
    msg = "Завершено. Время выполнения: %s seconds ---" % (time.time() - start_time)
    print(msg)
    #train(array_coll, ['5 best patterns set'], ['rf'])



def train(collections, list_permission, algorithms, ):
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
                classification(collection, list_permission, algorithms, 1)
            if any([True if i in regression_algorithms else False for i in algorithms]):
                regression(collection, list_permission, algorithms)
    msg = "Завершено. Время выполнения: %s seconds ---" % (time.time() - start_time)
    print(msg)
    #messagebox.showerror("Выполнено", msg)


def get_better_patterns(num_vectors_model, collection, num_group):#collections):
    col = Collections.objects.get(pk=collection)
    patterns_array = [
        ['days', 'day_parts', 'activity_time'],
        ['middle_pause', 'middle_pause2', 'middle_pause3'],
        ['quantity_middle_pause', 'quantity_middle_pause2', 'quantity_middle_pause3'],
        ['start_comp_pause'],
        ['url_freq_pause', 'dom_freq_pause'],
        ['url_bi', 'url_bi_pauses', 'dom_bi', 'dom_bi_pauses'],
        ['url_tri', 'url_tri_pauses', 'dom_tri', 'dom_tri_pauses'],
    ]
    for patterns1 in patterns_array:
        pats = [i[0] for i in Patterns.objects.filter(num_group=num_group).values_list('patterns')]
        for pat in pats:
            for l in range(1, len(patterns1)+1):
                for j in itertools.combinations(patterns1, l):
                    patterns_list = list(set(list(j) + pat))
                    print(patterns_list)
                    names = [name[0] for name in Teams.objects.filter(team=col.team).values_list('username')]
                    algorithms = 'rf'
                    print(names)
                    Classification(num_vectors_model, collection, patterns_list, algorithms, 10000)

        mass = [i[0] for i in ML.objects.filter(num_group=num_group).values_list('accuracy')]
        mass.sort()
        print(mass[-1])
        n = (len(mass)-10 if len(mass)>10 else 1)
        ML.objects.filter(num_group=num_group,accuracy__lt=mass[n]).delete()
        Patterns.objects.filter(num_group=num_group).delete()
        for pat in ML.objects.filter(num_group=num_group).values_list('patterns'):
            p = Patterns.objects.create(num_group=num_group, patterns=pat[0])
            p.save()
    print('завершено')

def anomaly_get_better_patterns(num_vectors_model, collection, num_group):
    names = ['ys', 'bv', 'mk', 'ro']
    col = Collections.objects.get(pk=collection)
    patterns_array = [
        ['urls', 'domains'],
        ['days', 'day_parts', 'activity_time'],
        ['middle_pause', 'middle_pause2', 'middle_pause3'],
        ['quantity_middle_pause', 'quantity_middle_pause2', 'quantity_middle_pause3'],
        ['start_comp_pause'],
        ['url_freq_pause', 'dom_freq_pause'],
        ['url_bi', 'url_bi_pauses', 'dom_bi', 'dom_bi_pauses'],
        ['url_tri', 'url_tri_pauses', 'dom_tri', 'dom_tri_pauses'],
        ['domain_type', 'domain_category'],
    ]
    for patterns1 in patterns_array:
        pats = [i[0] for i in Patterns.objects.filter(num_group=num_group).values_list('patterns')]
        for pat in pats:
            for l in range(1, len(patterns1)+1):
                for j in itertools.combinations(patterns1, l):
                    patterns_list = list(set(list(j) + pat))
                    if patterns_list == []:
                        continue
                    print(patterns_list)
                    Anomaly(num_vectors_model, collection, patterns_list, names)
        if pats == []:
            for l in range(1, len(patterns1) + 1):
                for j in itertools.combinations(patterns1, l):
                    patterns_list = list(j)
                    if patterns_list == []:
                        continue
                    print(patterns_list)
                    Anomaly(num_vectors_model, collection, patterns_list, names)

        mass = [i[0] for i in AnomalyML.objects.filter(num_group=num_group).values_list('accuracy')]
        mass.sort()
        print(mass[-1])
        if len(mass) > 9:
            n = (len(mass)-10 if len(mass)>10 else 1)
            AnomalyML.objects.filter(num_group=num_group,accuracy__lt=mass[n]).delete()
        Patterns.objects.filter(num_group=num_group).delete()
        for pat in AnomalyML.objects.filter(num_group=num_group).values_list('patterns'):
            p = Patterns.objects.create(num_group=num_group, patterns=pat[0])
            p.save()
    print('завершено')