import csv
import numpy as np
import pandas as pd
import time

from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler

from analyse.models import ML, Collections
from base.constants import classification_algorithms, regression_algorithms, V
from ML.new_ML import Classification, ClassificationTest


class OneTrain(Classification):
    def __init__(self, num_vectors_model, collection, pattern_list, algorithm, username, num_train_vectors=1600, file=None, exclude=[]):
        self.num_vectors_model = num_vectors_model
        self.vector_model = V[num_vectors_model]
        self.collection = collection
        self.pattern_list = pattern_list
        self.algorithm = algorithm
        self.filename = file
        self.exclude = exclude
        self.num_train_vectors = num_train_vectors
        self.username = username
        self.train()

    def train(self):
        # данные для обучения
        print(self.pattern_list)
        fil = {'collection': self.collection, 'type': 1}
        names = [name[0] for name in self.vector_model.objects.filter(**fil).distinct('username').values_list('username')]
        exclude = self.exclude.copy()
        exclude.extend([name for name in names if name != self.username])
        X, Y = self.get_arrays_norma(fil, self.pattern_list, exclude, self.num_train_vectors)
        Y = [1 for i in Y]
        exclude = self.exclude.copy()
        exclude.extend([self.username])
        new_X, new_Y = self.get_arrays_norma(fil, self.pattern_list, exclude, self.num_train_vectors // (len(names) - 1))
        new_Y = [-1 for i in new_Y]
        X.extend(new_X.copy())
        new_X = None
        Y.extend(new_Y.copy())
        new_Y = None
        X = np.array(X)
        Y = np.array(Y)
        print('Длина вектора' + str(len(X[0])))
        print('Количество векторов' + str(len(X)))
        # self.check_vectors_len(X,Y)

        scaler = StandardScaler()
        scaler.fit(X)
        X = scaler.transform(X)
        if self.filename:
            scaler_name = './algorithms/' + self.filename + 'scaler.pkl'
            joblib.dump(scaler, scaler_name)
            print('машина нормализации сохранена')
        print('начало обучения')
        a = classification_algorithms[self.algorithm]
        a.fit(X, Y)
        if self.filename:
            joblib.dump(a, './algorithms/' + self.filename + '.pkl')
            print('машина сохранена')
        X = None
        Y = None
        OneTest(self.num_vectors_model, self.collection, self.pattern_list, self.algorithm, self.username, scaler, a, exclude=self.exclude, num_train_vectors=self.num_train_vectors)


class OneTest(ClassificationTest):
    def __init__(self, num_vectors_model, collection, pattern_list, algorithm, username, scaler=None, alg=None, file=None, mistakes=0, exclude=[], num_train_vectors=None):
        self.vector_model = V[num_vectors_model]
        self.collection = collection
        self.pattern_list = pattern_list
        self.algorithm = algorithm
        self.forgivable_mistakes = mistakes
        self.scaler = scaler
        self.alg = alg
        self.file = file
        self.exclude = exclude
        self.username = username
        self.num_train_vectors = num_train_vectors
        self.test()

    def test(self):
        if self.file:
            self.scaler = joblib.load('./algorithms/' + self.file + 'scaler.pkl')
            self.alg = joblib.load('./algorithms/' + self.file + '.pkl')

        # данные для тестирования
        fil = {'collection': self.collection, 'type': 2}
        names = [name[0] for name in
                 self.vector_model.objects.filter(**fil).distinct('username').values_list('username')]
        exclude = self.exclude.copy()
        exclude.extend([name for name in names if name != self.username])
        test_X, test_Y = self.get_arrays_order_norma(fil, self.pattern_list, exclude)
        test_Y = [1 for i in test_Y]
        exclude = self.exclude.copy()
        exclude.extend([self.username])
        self.num_train_vectors = self.num_train_vectors // 8
        new_X, new_Y = self.get_arrays_order_norma(fil, self.pattern_list, exclude)
        new_Y = [-1 for i in new_Y]
        test_X.extend(new_X.copy())
        new_X = None
        test_Y.extend(new_Y.copy())
        new_Y = None
        test_X = np.array(test_X)
        test_Y = np.array(test_Y)
        n_test = len(test_Y)

        test_X = self.scaler.transform(test_X)
        names = [1, -1]
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
            if self.forgivable_mistakes:
                if result[i] != self.username:
                    if test_Y[i] in active_users:
                        active_users = active_users[1:] + [result[i]]
                        result[i] = test_Y[i]
                    else:
                        active_users = active_users[1:] + [result[i]]
                else:
                    active_users = active_users[1:] + [result[i]]
            if result[i] == test_Y[i]:
                good += 1
            if result[i] == 1 and test_Y[i] == -1:
                FAR[1] += 1
            if result[i] == -1 and test_Y[i] == 1:
                FRR[1] += 1
        print('\n' + 'точность:' + str(good / n_test))
        print('\n' + str(1) + " FAR:" + str(FAR[1] / n_login_attempt[-1]))
        print('\n' + str(1) + " FRR:" + str(FRR[1] / n_login_attempt[1]))
        collection = Collections.objects.get(pk=self.collection)
        ML.objects.create(
            collection=collection,
            patterns=self.pattern_list,
            middleFAR=FAR[1] / n_login_attempt[-1],
            middleFRR=FRR[1] / n_login_attempt[1],
            accuracy=good / n_test,
            algorithm=self.algorithm,
            num_group=-1,
        )