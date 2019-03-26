import csv
import numpy as np
import pandas as pd
import time

from sklearn.preprocessing import StandardScaler

from analyse.models import ML, VectorsOneVersion
from base.constants import classification_algorithms, regression_algorithms


def regression(path, names, pattern_list, algorithms, info):
    # данные для обучения
    patterns = pattern_list
    patterns.append('username')
    fil = info.copy()
    fil['type'] = 1
    X, Y = get_arrays_re(fil, patterns, names, 'bv')
    n = len(Y)
    print('Длина вектора' + str(len(X[0])))

    # нормализация
    scaler = StandardScaler()
    scaler.fit(X)
    X = scaler.transform(X)

    # данные для тестирования
    fil = info.copy()
    fil['type'] = 2
    test_X, test_Y = get_arrays_re(fil, patterns, names)

    n_test = len(test_Y)
    test_X = scaler.transform(test_X)

    # данные для определения FAR и FRR
    n_login_attempt = {names.index(name): 0 for name in names}  # сколько раз легитимный пользователь пытался войти
    for name in test_Y:
        n_login_attempt[name] += 1

    print(n_login_attempt)

    # несколько алгоритмов МО
    ml = {}
    for key, value in regression_algorithms.items():
        if key in algorithms:
            ml[key] = value

    with open(".\\otch123.txt", 'w') as f:
        f.write(str(names) + " " + str(n) + ' ' + str(ml))
        # обучение, тестирование, вывод на экран
        for name_alg, algorithm in ml.items():
            f.write('\n' + name_alg)
            print('\n' + name_alg)
            a = algorithm
            print(len(X))
            print(len(Y))
            a.fit(X, Y)
            result = a.predict(test_X)
            print(result)

            # проверка результатов
            FAR = {name: 0 for name in names}  # ложное положительное решение
            FRR = {name: 0 for name in names}  # случайно заблокировали владельца

            good = 0
            max_g=0
            min_g=0
            aver_g = []
            max_b=0
            min_b=0
            aver_b = []
            fuck_boy = names.index('bv')
            print(fuck_boy)
            for i in range(n_test):
                gg = [l / len(test_X[i]) for l in test_X[i]]
                y = sum(gg)
                difference = abs(result[i] - y)
                if test_Y[i] == fuck_boy:
                    aver_g.append(difference)
                    if difference > max_g:
                        max_g = difference
                    if difference < min_g:
                        min_g = difference
                if test_Y[i] != fuck_boy:
                    aver_b.append(difference)
                    if result[i] > max_b:
                        max_b = difference
                    if result[i] < min_b:
                        min_b = difference

            aver_g = sum(aver_g)/len(aver_g)
            aver_b = sum(aver_b) / len(aver_b)


            f.write('good aver=' + str(aver_g)+"\n min:" + str(min_g)+"\n max:" + str(max_g))
            f.write('\nbad aver=' + str(aver_b)+"\n min:" + str(min_b)+"\n max:" + str(max_b))




def classification(names, pattern_list, algorithms, info):
    # данные для обучения
    patterns = pattern_list
    patterns.append('username')
    fil = info.copy()
    fil['type'] = 1
    X, Y = get_arrays(fil, patterns)
    n = len(Y)
    print('Длина вектора' + str(len(X[0])))

    # нормализация
    scaler = StandardScaler()
    scaler.fit(X)
    X = scaler.transform(X)

    # данные для тестирования
    fil = info.copy()
    fil['type'] = 2
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

    #with open(path + "\\otch.txt", 'w') as f:
    #f.write(str(names) + " " + str(n))
    # обучение, тестирование, вывод на экран
    for name_alg, algorithm in ml.items():
        #f.write('\n' + name_alg)
        #print('\n' + name_alg)
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
        #f.write('\n' +'точность:' + str(accuracy))
        print('\n' +'точность:' + str(good / n_test))
        summ_FAR = 0
        summ_FRR = 0
        for name in names:
            #f.write('\n' + name + " FAR:" + str(FAR[name] / n_test))
            #f.write('\n' + name + " FRR:" + str(FRR[name] / n_login_attempt[name]))
            summ_FAR += FAR[name] / n_test
            summ_FRR += FRR[name] / n_login_attempt[name]
        middleFAR = summ_FAR / len(names)
        middleFRR = summ_FRR / len(names)
        #print("\nсредний FAR:" + str(middleFAR))
        #print("\nсредний FRR:" + str(middleFRR))
        #f.write("\nсредний FAR:" + str(middleFAR))
        #f.write("\nсредний FRR:" + str(middleFRR))

        ML.objects.create(
            collection = info['collection'],
            patterns = pattern_list,
            middleFAR = middleFAR,
            middleFRR = middleFRR,
            accuracy = accuracy,
            algorithm=name_alg,
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
    print(len(l_X))

    X = np.array(X)
    Y = np.array(Y)
    return X, Y


def reg_f(X):
    Y = []
    for i in X:
        gg = [l / len(i) for l in i]
        Y.append(sum(gg))
    return Y


def get_arrays_re(criterion, patterns, names, name=None):
    if name:
        mass = VectorsOneVersion.objects.filter(username=name).filter(**criterion).values_list(*patterns)
    else:
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
    print(len(l_X))

    if name:
        Y = reg_f(X)
    else:
        Y = [names.index(i) for i in Y]
    X = np.array(X)
    Y = np.array(Y)
    return X, Y