import csv
import numpy as np
import pandas as pd
import time

from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler

from analyse.models import ML, VectorsOneVersion1, Collections
from base.constants import classification_algorithms, regression_algorithms

class Classification(object):
    def __init__(self, collection, pattern_list, algorithm, forgivable_mistakes=0, filename=None, exclude = []):
        self.collection = collection
        self.pattern_list = pattern_list
        self.algorithm = algorithm
        self.forgivable_mistakes = forgivable_mistakes
        self.filename = filename
        self.exclude = exclude

    def train(self):
        # данные для обучения
        patterns = self.pattern_list.copy()
        patterns.append('username')
        print(patterns)
        #exclude = ['ys', 'mk']
        fil = {'collection': self.collection, 'type': 1}
        X, Y = self.get_arrays_norma(fil, patterns, self.exclude, 1600)
        print('Длина вектора' + str(len(X[0])))
        print('Количество векторов' + str(len(X)))
        #n = len(X[0])
        #exit()
        # for i in range(len(X)):
        #     try:
        #         if len(X[i]) != n:
        #             print(Y[i])
        #             print(str(n)+ ' ' + str(len(X[i])))
        #     except:
        #         print(Y[i])
        #         print(X[i])

        scaler = StandardScaler()
        scaler.fit(X)
        X = scaler.transform(X)
        print('начало обучения')
        a = classification_algorithms[self.algorithm]
        a.fit(X, Y)
        if self.filename:
            joblib.dump(a, self.filename)
            print('машина сохранена')

        # данные для тестирования
        fil = {'collection': self.collection, 'type': 2}
        test_X, test_Y = self.get_arrays_order(fil, patterns, self.exclude)
        n_test = len(test_Y)
        test_X = scaler.transform(test_X)
        names = [i[0]  for i in VectorsOneVersion1.objects.filter(collection=self.collection).distinct('username').values_list('username') if not i[0] in self.exclude]
        n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
        for name in test_Y:
            n_login_attempt[name] += 1
        active_users = [test_Y[i] for i in range(self.forgivable_mistakes)]
        result = a.predict(test_X)

        # проверка результатов
        FAR = {name: 0 for name in names}  # ложное положительное решение
        FRR = {name: 0 for name in names}  # случайно заблокировали владельца
        good = 0
        for i in range(n_test):
            if result[i] != test_Y[i]:
                if test_Y[i] in active_users:
                    active_users = active_users[1:] + [result[i]]
                    result[i] = test_Y[i]

            if result[i] == test_Y[i]:
                good += 1
            for name in names:
                if result[i] == name and test_Y[i] != name:
                    FAR[name] += 1
                if result[i] != name and test_Y[i] == name:
                    FRR[name] += 1
        accuracy = good / n_test
        print('\n' +'точность:' + str(good / n_test))
        summ_FAR = 0
        summ_FRR = 0
        for name in names:
            print('\n' + name + " FAR:" + str(FAR[name] / n_test))
            print('\n' + name + " FRR:" + str(FRR[name] / n_login_attempt[name]))
            summ_FAR += FAR[name] / n_test
            summ_FRR += FRR[name] / n_login_attempt[name]
        middleFAR = summ_FAR / len(names)
        middleFRR = summ_FRR / len(names)
        print("\nсредний FAR:" + str(middleFAR))
        print("\nсредний FRR:" + str(middleFRR))
        print(self.pattern_list)
        collection = Collections.objects.get(pk=self.collection)
        ML.objects.create(
            collection = collection,
            patterns = self.pattern_list,
            middleFAR = middleFAR,
            middleFRR = middleFRR,
            accuracy = accuracy,
            algorithm=self.algorithm,
        )

    def test(self, scaler=None, alg=None, file=None):
        if file:
            scaler = joblib.load(file + 'scaler.pkl')
            alg = joblib.load(file + '.pkl')
        patterns = self.pattern_list.copy()
        patterns.append('username')

        # данные для тестирования
        fil = {'collection': self.collection, 'type': 2}
        test_X, test_Y = self.get_arrays_order(fil, patterns, self.exclude)
        n_test = len(test_Y)
        test_X = scaler.transform(test_X)
        names = [i[0] for i in
                 VectorsOneVersion1.objects.filter(collection=self.collection).distinct('username').values_list(
                     'username') if not i[0] in self.exclude]
        n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
        for name in test_Y:
            n_login_attempt[name] += 1
        active_users = [test_Y[i] for i in range(self.forgivable_mistakes)]
        result = alg.predict(test_X)

        # проверка результатов
        FAR = {name: 0 for name in names}  # ложное положительное решение
        FRR = {name: 0 for name in names}  # случайно заблокировали владельца
        good = 0
        for i in range(n_test):
            if result[i] != test_Y[i]:
                if test_Y[i] in active_users:
                    active_users = active_users[1:] + [result[i]]
                    result[i] = test_Y[i]

            if result[i] == test_Y[i]:
                good += 1
            for name in names:
                if result[i] == name and test_Y[i] != name:
                    FAR[name] += 1
                if result[i] != name and test_Y[i] == name:
                    FRR[name] += 1
        accuracy = good / n_test
        print('\n' + 'точность:' + str(good / n_test))
        summ_FAR = 0
        summ_FRR = 0
        for name in names:
            print('\n' + name + " FAR:" + str(FAR[name] / n_test))
            print('\n' + name + " FRR:" + str(FRR[name] / n_login_attempt[name]))
            summ_FAR += FAR[name] / n_test
            summ_FRR += FRR[name] / n_login_attempt[name]
        middleFAR = summ_FAR / len(names)
        middleFRR = summ_FRR / len(names)
        print("\nсредний FAR:" + str(middleFAR))
        print("\nсредний FRR:" + str(middleFRR))
        print(self.pattern_list)
        collection = Collections.objects.get(pk=self.collection)
        ML.objects.create(
            collection=collection,
            patterns=self.pattern_list,
            middleFAR=middleFAR,
            middleFRR=middleFRR,
            accuracy=accuracy,
            algorithm=self.algorithm,
        )

    def get_arrays(self, criterion, patterns, exclude=[]):
        mass = VectorsOneVersion1.objects.filter(**criterion).values_list(*patterns)
        X = []
        Y = []
        for line in mass:
            if not line[-1] in exclude:
                l_X = []
                for obj in line[:len(line) - 2]:
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
        X = np.array(X)#, dtype=object)
        Y = np.array(Y)#, dtype=object)
        return X, Y

    def get_arrays_norma(self, criterion, patterns, exclude=[], Norma=None):
        mass = VectorsOneVersion1.objects.filter(**criterion).values_list(*patterns)
        users = [name[0] for name in
                 VectorsOneVersion1.objects.filter(**criterion).distinct('username').values_list('username') if
                 not name[0] in exclude]
        users_X = {name: [] for name in users}
        X = []
        Y = []
        for line in mass:
            if not line[-1] in exclude:
                l_X = []
                for obj in line[:len(line) - 1]:
                    if isinstance(obj, list):
                        # для карты кликов
                        if isinstance(obj[0], list):
                            for j in obj:
                                l_X.extend(j)
                        else:
                            l_X.extend(obj)
                    else:
                        l_X.append(obj)
                users_X[line[-1]].append(l_X.copy())
        if Norma:
            for name in users:
                n = len(users_X[name])
                if n < Norma:
                    new_array = self.add_vectors(users_X[name], n, Norma)
                    X.extend(new_array.copy())
                    Y.extend([name for i in range(len(new_array))])
                elif n > Norma:
                    new_array = self.reduce_vectors_number(users_X[name], n, Norma)
                    X.extend(new_array.copy())
                    Y.extend([name for i in range(len(new_array))])
                else:
                    X.extend(users_X[name].copy())
                    Y.extend([name for i in range(n)])
        X = np.array(X)
        Y = np.array(Y)
        return X, Y

    def add_vectors(self, array, vectors_quantity, necessary_vectors_quantity):
        """
        Увеличивает количество векторов с vectors_quantity до необходимых necessary_vectors_quantity для пользователя
        name.
        """
        new_array = array
        times = necessary_vectors_quantity // vectors_quantity - 1
        for i in range(times):
            for j in array:
                new_array.append(j.copy())
        difference = necessary_vectors_quantity - (vectors_quantity * (times + 1))
        i = 0
        for j in array:
            if i >= difference:
                break
            i += 1
            new_array.append(j.copy())
        return new_array

    def reduce_vectors_number(self, array, vectors_quantity, necessary_vectors_quantity):
        new_array = []
        step = vectors_quantity // necessary_vectors_quantity
        for i in range(necessary_vectors_quantity):
            new_array.append(array[vectors_quantity - i * step - 1])
        return new_array

    def get_arrays_order(self, criterion, patterns, exclude=[]):
        mass = VectorsOneVersion1.objects.order_by('id').filter(**criterion).values_list(*patterns)
        X = []
        Y = []
        for line in mass:
            if not line[-1] in exclude:
                l_X = []
                for obj in line[:len(line) - 2]:
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
        X = np.array(X)#, dtype=object)
        Y = np.array(Y)#, dtype=object)
        return X, Y



