import csv
import numpy as np
import pandas as pd
import time

from sklearn.preprocessing import StandardScaler

from analyse.models import ML, VectorsOneVersion
from base.constants import classification_algorithms

def classification(path, names, pattern_list, algorithms, info):

    # данные для обучения
    patterns = pattern_list
    patterns.append('username')
    fil = info.copy()
    fil['type'] = 1
    X, Y = get_arrays(fil, patterns)
    n = len(Y)

    # нормализация
    scaler = StandardScaler()
    scaler.fit(X)
    X = scaler.transform(X)

    # данные для тестирования
    fil = info.copy()
    fil['type'] = 2
    mass = VectorsOneVersion.objects.filter(**fil).values_list(*patterns)
    test_X, test_Y = get_arrays(fil, patterns)

    n_test = len(test_Y)
    test_X = scaler.transform(test_X)

    # данные для определения FAR и FRR
    n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
    for name in test_Y:
        n_login_attempt[name] += 1

    print(n_login_attempt)

    # несколько алгоритмов МО
    ml = {}
    for key, value in classification_algorithms.items():
        if key in algorithms:
            ml[key] = value

    with open(path + "\\otch.txt", 'w') as f:
        f.write(str(names) + " " + str(n))
        # обучение, тестирование, вывод на экран
        for name_alg, algorithm in ml.items():
            f.write('\n' + name_alg)
            a = algorithm
            a.fit(X, Y)
            result = a.predict(test_X)

            # проверка результатов
            FAR = {name: 0 for name in names}  # ложное положительное решение
            FRR = {name: 0 for name in names}  # случайно заблокировали владельца

            good = 0
            for i in range(n_test):
                if result[i] == test_Y[i]:
                    good += 1
                for name in names:
                    if result[i] == name and test_Y[i] != name:
                        FAR[name] += 1
                    if result[i] != name and test_Y[i] == name:
                        FRR[name] += 1
            accuracy = good / n_test
            f.write('\n' +'точность:' + str(accuracy))
            #print('\n' +'точность:' + str(good / n_test))
            summ_FAR = 0
            summ_FRR = 0
            for name in names:
                f.write('\n' + name + " FAR:" + str(FAR[name] / n_test))
                f.write('\n' + name + " FRR:" + str(FRR[name] / n_login_attempt[name]))
                summ_FAR += FAR[name] / n_test
                summ_FRR += FRR[name] / n_login_attempt[name]
            middleFAR = summ_FAR / len(names)
            middleFRR = summ_FRR / len(names)
            f.write("\nсредний FAR:" + str(middleFAR))
            f.write("\nсредний FRR:" + str(middleFRR))

            ML.objects.create(
                team = info['team'],
                clicks = info['clicks'],
                num_users = len(names),
                patterns = pattern_list,
                middleFAR = middleFAR,
                middleFRR = middleFRR,
                accuracy = accuracy,
            )

def get_arrays(criterion, patterns):
    mass = VectorsOneVersion.objects.filter(**criterion).values_list(*patterns)
    X = []
    Y = []
    for line in mass:
        l_X = []
        for obj in line[:len(line)-1]:
            if isinstance(obj, list):
                # для карты кликов
                if isinstance(obj[0], list):
                    for j in obj:
                        l_X.extend(j)
                else:
                    l_X.extend(obj)
            else:
                l_X.append(obj)
        Y.append(line[-1])
        X.append(l_X.copy())
    X = np.array(X)
    Y = np.array(Y)
    return X, Y