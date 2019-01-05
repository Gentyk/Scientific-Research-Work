import csv
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

def ml(X, Y, test_X, test_Y, names=None):
    # имена юнитов
    if not names:
        names = ['mk', 'ro', 'ys', 'dy', 'bv']

    # находим количество столбцов
    n=len(X[0])
    n_test = len(test_Y)

    # данные для определения FAR и FRR
    n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
    for name in test_Y:
        n_login_attempt[name] += 1
    print(n_login_attempt)

    # несколько алгоритмов МО
    ml = {'rf': RandomForestClassifier(),
          'knn': KNeighborsClassifier(n_neighbors=5, weights='uniform', p=1, algorithm='brute'),
          'SVC': SVC()}

    # обучение, тестирование, вывод на экран
    for name_alg, algorithm in ml.items():
        print('\n'+name_alg)
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
        print('ошибается вообще:' + str(good / n_test))
        for name in names:
            print(name + " FAR:" + str(FAR[name] / n_test))
            print(name + " FRR:" + str(FRR[name] / n_login_attempt[name]))
