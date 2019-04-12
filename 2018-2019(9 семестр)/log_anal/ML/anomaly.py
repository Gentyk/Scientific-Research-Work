import csv
import numpy as np
import pandas as pd
import time

from sklearn.preprocessing import StandardScaler

from analyse.models import ML,VectorsOneVersion2, AnomalyML, Collections
from base.constants import classification_algorithms, regression_algorithms
from base.constants import V
import matplotlib.cm as cm
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture

from time import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import offsetbox
from sklearn import (manifold, datasets, decomposition, ensemble,
                     discriminant_analysis, random_projection)
from ML.new_ML import ClassificationTest


class Anomaly(ClassificationTest):
    def __init__(self, num_vectors_model, collection, pattern_list, names):
        self.num_vectors_model = num_vectors_model
        self.vector_model = V[num_vectors_model]
        self.collection = collection
        self.pattern_list = pattern_list
        self.names = names
        self.num_train_vectors = 1250
        self.run()

    def run(self):
        min = 100
        line = None
        for name in self.names:
            local_line = self.anomaly(name)
            if local_line[0] < min:
                line = local_line.copy()
                min = local_line[0]
                if local_line[0] < 0.7:
                    break
        print(line)
        AnomalyML.objects.create(
            collection=Collections.objects.get(pk=self.collection),
            good_accuracy=line[3],
            bad_accuracy = line[4],
            patterns=self.pattern_list,
            middleFAR=line[1],
            middleFRR=line[2],
            accuracy=line[0],
            algorithm='OneClassSVM',
            num_group=3,
        )

    def anomaly(self, name):
        # данные для обучения

        #patterns.append('username')
        fil = {'collection' : self.collection, 'type': 1}
        X = self.get_arrays_re(fil, self.pattern_list, name)
        print(len(X))
        n = len(X[0])
        print('Длина вектора' + str(n))

        scaler = StandardScaler()
        scaler.fit(X)
        X = scaler.transform(X)
        a = OneClassSVM(gamma=0.03)#IsolationForest(max_samples=0.5)
        a.fit(X)
        print('начало тестирования')
        X = None


        # данные для тестирования
        fil = {'collection': self.collection, 'type': 2}
        test_X, test_Y = self.get_arrays_order_norma2(fil, self.pattern_list, name)
        test_Y = [1 if i == name else -1 for i in test_Y]
        test_X = np.array(test_X)
        test_Y = np.array(test_Y)
        n_test = len(test_Y)
        print(n_test)
        test_X = scaler.transform(test_X)
        result = a.predict(test_X)
        print(set(result))
        aver_g = 0
        num_good = 3000#self.vector_model.objects.filter(**fil).filter(username=name).count()
        num_bad = 3000#self.vector_model.objects.filter(**fil).count() - num_good
        aver_b = 0
        err = 0
        far = 0
        frr = 0
        for i in range(n_test):
            if result[i] == 1 and test_Y[i] == 1:
                aver_g += 1
            elif result[i] == -1 and test_Y[i] == -1:
                aver_b += 1
            else:
                err += 1
            if result[i] == 1 and test_Y[i] != 1:
                far += 1
            if result[i] != 1 and test_Y[i] == 1:
                frr += 1
        print(err)
        print(name)
        print('good aver=' + str(aver_g/num_good))
        print('bad aver=' + str(aver_b / num_bad))
        print('frr=' + str(frr / num_good))
        print('far=' + str(far / num_bad))
        accuracy = (aver_g + aver_b) / n_test
        far = far / num_bad
        frr = frr / num_good
        good = aver_g/num_good
        bad = aver_b / num_bad
        print('точность=' + str(accuracy))
        return [accuracy, far, frr, good, bad]


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
        print(patterns)
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



def get_test_arrays(criterion, patterns, name=None, l = 0):
    mass = VectorsOneVersion2.objects.filter(**criterion).values_list(*patterns)
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



def get_test2_arrays(criterion, patterns, name=None, l = 0):
    mass = VectorsOneVersion2.objects.filter(**criterion).values_list(*patterns)
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
    Y = [1 if i == name else -1 for i in Y]
    X = np.array(X)
    Y = np.array(Y)
    return X, Y


def reg_f(X):
    Y = []
    for i in X:
        gg = [l / len(i) for l in i]
        Y.append(sum(gg))
    return Y



def SNE(collection, pattern_list):

    patterns = pattern_list.copy()

    patterns.append('username')
    fil = {'collection' : collection, 'type': 1}
    X, Y = get_test_arrays(fil, patterns)

    # ----------------------------------------------------------------------
    # t-SNE embedding of the digits dataset
    print("Computing t-SNE embedding")
    tsne = manifold.TSNE(n_components=2, init='pca', random_state=0)
    X_tsne = tsne.fit_transform(X)

    names = list(set(Y))
    for name in names:
        xx = []
        yy = []
        j=400
        for i in range(len(X_tsne)):
            if Y[i] == name:
                j -=1
                xx.append(X_tsne[i][0])
                yy.append(X_tsne[i][1])
            if j==0:
                break
        print(len(xx))
        plt.scatter(xx, yy, label=name)
    plt.legend()
    plt.show()