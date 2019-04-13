from time import time
import random
import numpy as np
from collections import Counter


from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

from analyse.models import AnomalyML, Collections, RSML
from base.constants import V, patterns
from ML.new_ML import ClassificationTest

EXCLUDE=['domain_maps', 'url_maps', 'domain_categories']

class RandomSubspase(ClassificationTest):
    def __init__(self, num_vectors_model, collection):
        self.num_vectors_model = num_vectors_model
        self.vector_model = V[num_vectors_model]
        self.collection = collection
        self.pattern_list = [p for p in patterns if not p in EXCLUDE]
        self.names = [name[0] for name in self.vector_model.objects.filter(collection=collection).distinct('username').values_list('username')]
        self.num_train_vectors = 1250
        self.run()

    def run(self):
        avg_far = 0
        avg_frr = 0

        # формируем рандомные списки признаков
        print('начало формирования признаков')
        patterns_list = []
        for i in range(5):
            while True:
                n = random.randint(1, len(self.pattern_list))
                local_patterns = random.sample(self.pattern_list, n)
                if any([set(local_patterns) == set(j) for j in patterns_list]) == False:
                    patterns_list.append(local_patterns)
                    print(local_patterns)
                    break
        print('конец формирования признаков')
        results = []
        for name in self.names:
            results.append(self.train(patterns_list, name))
        new_results =  [sum(j)/5 for j in zip(*results)]

        print(new_results)
        RSML.objects.create(
            accuracy = new_results[0],
            patterns1 = patterns_list[0],
            patterns2 = patterns_list[1],
            patterns3 = patterns_list[2],
            patterns4 = patterns_list[3],
            patterns5 = patterns_list[4],
            middleFAR = new_results[1],
            middleFRR = new_results[2],
        )


    def train(self, patterns_list, name):
        # данные для обучения
        fil = {'collection' : self.collection, 'type': 1}

        models = []
        scalers = []
        for pat in patterns_list:
            models.append(OneClassSVM(gamma=0.03))#IsolationForest(max_samples=0.5)
            X = self.get_arrays_re(fil, pat, name)
            scalers.append(StandardScaler())
            scalers[-1].fit(X)
            X = scalers[-1].transform(X)
            models[-1].fit(X)
        X = None

        # данные для тестирования
        print('начало тестирования')
        fil = {'collection': self.collection, 'type': 2}
        results = []
        for i in range(5):
            test_X, test_Y = self.get_arrays_order_norma2(fil, patterns_list[i], name)
            test_X = np.array(test_X)
            test_X = scalers[i].transform(test_X)
            results.append(models[i].predict(test_X))
        test_X = None
        n_test = len(test_Y)
        #print(n_test)
        test_Y = [1 if i == name else -1 for i in test_Y]
        test_Y = np.array(test_Y)
        num_good = 3000#self.vector_model.objects.filter(**fil).filter(username=name).count()
        num_bad = 3000#self.vector_model.objects.filter(**fil).count() - num_good
        good = 0
        far = 0
        frr = 0
        for i in range(n_test):
            result = Counter([mass[i] for mass in results]).most_common()[0][0]
            if result == test_Y[i]:
                good += 1
            if result == 1 and test_Y[i] != 1:
                far += 1
            if result != 1 and test_Y[i] == 1:
                frr += 1
        print('frr=' + str(frr / num_good))
        print('far=' + str(far / num_bad))
        accuracy = good / n_test
        far = far / num_bad
        frr = frr / num_good
        return [accuracy, far, frr]


    def get_arrays_order_norma2(self, criterion, patterns, name, exclude=[]):
        X = []
        Y = []
        users = [name[0] for name in
                 self.vector_model.objects.filter(**criterion).distinct('username').values_list('username') if
                 not name[0] in exclude]
        for user in users:
            #print(user)
            n = self.vector_model.objects.filter(**criterion).filter(username=user).count()
            if self.num_train_vectors and int(self.num_train_vectors*0.3) < self.vector_model.objects.filter(**criterion).filter(username=user).count():
                n = int(self.num_train_vectors*0.3)
            if user == name:
                n = int(self.num_train_vectors * 0.3 * 8)
            X.extend([self.get_line(line) for line in self.vector_model.objects.filter(**criterion).filter(
                          username=user).order_by('id').values_list(*patterns)][:n])
            Y.extend([user for i in range(n)])
            if len(X) != len(Y):
                raise
        return X, Y


    def get_arrays_re(self, criterion, patterns, name=None):
        #print(patterns)
        mass = self.vector_model.objects.filter(username=name).filter(**criterion).values_list(*patterns)
        X = []
        for line in mass:
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
            X.append(l_X.copy())
        n = len(X)
        X = self.add_vectors(X,n,10000)
        X = np.array(X)

        return X



