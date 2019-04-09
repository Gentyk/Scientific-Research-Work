import csv
import numpy as np
import pandas as pd
import time

from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler

from analyse.models import ML, VectorsOneVersion1, Collections
from base.constants import classification_algorithms, regression_algorithms

class Classification(object):
    def __init__(self, collection, pattern_list, algorithm, num_train_vectors=1600, filename=None, exclude=[]):
        self.collection = collection
        self.pattern_list = pattern_list
        self.algorithm = algorithm
        self.filename = filename
        self.exclude = exclude
        self.num_train_vectors = num_train_vectors

    def train(self):
        # данные для обучения
        print(self.pattern_list)
        #exclude = ['ys', 'mk']
        fil = {'collection': self.collection, 'type': 1}
        X, Y = self.get_arrays_norma(fil, self.pattern_list, self.exclude, self.num_train_vectors)
        X = np.array(X)
        Y = np.array(Y)
        print('Длина вектора' + str(len(X[0])))
        print('Количество векторов' + str(len(X)))
        #self.check_vectors_len(X,Y)

        scaler = StandardScaler()
        scaler.fit(X)
        X = scaler.transform(X)
        if self.filename:
            scaler_name = self.filename.split('.')
            scaler_name = '.' + scaler_name[1] + 'scaler.' + scaler_name[2]
            joblib.dump(scaler, scaler_name)
            print('машина нормализации сохранена')
        print('начало обучения')
        a = classification_algorithms[self.algorithm]
        a.fit(X, Y)
        if self.filename:
            joblib.dump(a, self.filename)
            print('машина сохранена')
        X = None
        Y = None
        ClassificationTest(self.collection, self.pattern_list, self.algorithm, scaler, a, exclude=self.exclude, num_train_vectors=self.num_train_vectors)

    def check_vectors_len(self, X, Y):
        n = len(X[0])
        for i in range(len(X)):
            try:
                if len(X[i]) != n:
                    print(Y[i])
                    print(str(n)+ ' ' + str(len(X[i])))
            except:
                print(Y[i])
                print(X[i])

    def get_arrays_norma(self, criterion, patterns, exclude=[], Norma=None):
        X = []
        Y = []
        users = [name[0] for name in
                 VectorsOneVersion1.objects.filter(**criterion).distinct('username').values_list('username') if
                 not name[0] in exclude]
        for user in users:
            print(user)
            n = VectorsOneVersion1.objects.filter(**criterion).filter(username=user).count()
            if n < Norma:
                mass = [self.get_line(line) for line in VectorsOneVersion1.objects.filter(**criterion).filter(username=user).values_list(*patterns)]
                X.extend(self.add_vectors(mass, n, Norma))
                mass = None
                Y.extend([user for i in range(Norma)])
            elif n > Norma:
                step = n // Norma
                X.extend([self.get_line(line) for line in VectorsOneVersion1.objects.filter(**criterion).order_by('-id').filter(username=user).values_list(*patterns)[:n:step][:Norma]])
                Y.extend([user for i in range(Norma)])
            else:
                X.extend([self.get_line(line) for line in
                          VectorsOneVersion1.objects.filter(**criterion).order_by('-id').filter(
                              username=user).values_list(*patterns)])
                Y.extend([user for i in range(Norma)])
        return X, Y

    def get_line(self, line):
        l_X = []
        for obj in line:
            if isinstance(obj, list):
                # для карты кликов
                if isinstance(obj[0], list):
                    for j in obj:
                        l_X.extend(j)
                else:
                    l_X.extend(obj)
            else:
                l_X.append(obj)
        return l_X

    def add_vectors(self, array, vectors_quantity, necessary_vectors_quantity):
        """
        Увеличивает количество векторов с vectors_quantity до необходимых necessary_vectors_quantity для пользователя
        name.
        """
        times = necessary_vectors_quantity // vectors_quantity
        new_array = array * times
        difference = necessary_vectors_quantity - (vectors_quantity * (times))
        new_array.extend(array[:difference])
        print(str(necessary_vectors_quantity) + ' ' +str(len(new_array)))
        return new_array

    def reduce_vectors_number(self, array, vectors_quantity, necessary_vectors_quantity):
        new_array = []
        step = vectors_quantity // necessary_vectors_quantity
        for i in range(necessary_vectors_quantity):
            new_array.append(array[vectors_quantity - i * step - 1])
        return new_array


class ClassificationTest(Classification):
    def __init__(self, collection, pattern_list, algorithm, scaler=None, alg=None, file=None, mistakes=0, exclude=[], num_train_vectors=None):
        self.collection = collection
        self.pattern_list = pattern_list
        self.algorithm = algorithm
        self.forgivable_mistakes = mistakes
        self.scaler = scaler
        self.alg = alg
        self.file = file
        self.exclude = exclude
        self.num_train_vectors=num_train_vectors
        self.test()

    def test(self):
        if self.file:
            self.scaler = joblib.load('./algorithms/' + self.file + 'scaler.pkl')
            self.alg = joblib.load('./algorithms/' + self.file + '.pkl')

        # данные для тестирования
        fil = {'collection': self.collection, 'type': 2}
        test_X, test_Y = self.get_arrays_order_norma(fil, self.pattern_list, self.exclude)
        test_X = np.array(test_X)
        test_Y = np.array(test_Y)
        n_test = len(test_Y)

        test_X = self.scaler.transform(test_X)
        names = [i[0] for i in
                 VectorsOneVersion1.objects.filter(collection=self.collection).distinct('username').values_list(
                     'username') if not i[0] in self.exclude]
        n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
        for name in test_Y:
            n_login_attempt[name] += 1
        active_users = [test_Y[i] for i in range(self.forgivable_mistakes)]
        result = self.alg.predict(test_X)

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

    def get_arrays_order(self, criterion, patterns, exclude=[]):
        mass = VectorsOneVersion1.objects.order_by('id').filter(**criterion).values_list(*patterns)
        print(patterns)
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
                Y.append(line[-1])
                X.append(l_X.copy())
        X = np.array(X)#, dtype=object)
        Y = np.array(Y)#, dtype=object)
        return X, Y

    def get_arrays_order_norma(self, criterion, patterns, exclude=[]):
        X = []
        Y = []
        users = [name[0] for name in
                 VectorsOneVersion1.objects.filter(**criterion).distinct('username').values_list('username') if
                 not name[0] in exclude]
        for user in users:
            print(user)
            n = VectorsOneVersion1.objects.filter(**criterion).filter(username=user).count()
            if self.num_train_vectors and int(self.num_train_vectors*0.3) < VectorsOneVersion1.objects.filter(**criterion).filter(username=user).count():
                n = int(self.num_train_vectors*0.3)
            X.extend([self.get_line(line) for line in VectorsOneVersion1.objects.filter(**criterion).filter(
                          username=user).order_by('id').values_list(*patterns)][:n])
            Y.extend([user for i in range(n)])
            if len(X) != len(Y):
                break
        return X, Y



