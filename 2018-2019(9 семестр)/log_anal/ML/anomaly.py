import csv
import numpy as np
import pandas as pd
import time

from sklearn.preprocessing import StandardScaler

from analyse.models import ML,VectorsOneVersion2
from base.constants import classification_algorithms, regression_algorithms
from base.constants import patterns as pattern_list
import matplotlib.cm as cm
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

from time import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import offsetbox
from sklearn import (manifold, datasets, decomposition, ensemble,
                     discriminant_analysis, random_projection)


def anomaly(collection, pattern_list, name):
    # данные для обучения
    # patterns = [
    #    # 'days', 'day_parts',
    #     'activity_time',
    #     'middle_pause', 'middle_pause2', 'middle_pause3',
    #   #  'quantity_middle_pause', 'quantity_middle_pause2', 'quantity_middle_pause3',
    #     'start_comp_pause',
    #     'urls', 'url_freq_pause', 'url_maps',
    #     'domains', 'dom_freq_pause', 'domain_maps',
    #  #   'url_bi', 'url_bi_pauses',
    #     'dom_bi', 'dom_bi_pauses',
    #   #  'url_tri', 'url_tri_pauses',
    #   #  'dom_tri', 'dom_tri_pauses',
    #     'domain_type',
    #   #  'domain_categories'
    # ]
    patterns = pattern_list.copy()
    patterns.append('username')
    fil = {'collection' : collection, 'type': 1}
    X = get_arrays_re(fil, patterns, name)
    print(len(X))
    n = len(X[0])
    print('Длина вектора' + str(n))

    scaler = StandardScaler()
    scaler.fit(X)
    X = scaler.transform(X)
    a = OneClassSVM(gamma=0.03)#IsolationForest()
    a.fit(X)
    X = None
    
    # данные для тестирования
    fil = {'collection': collection, 'type': 2}
    test_X, test_Y = get_test2_arrays(fil, patterns, name, n)
    n_test = len(test_Y)
    print(n_test)
    test_X = scaler.transform(test_X)
    result = a.predict(test_X)
    print(set(result))
    aver_g = 0
    num_good = VectorsOneVersion2.objects.filter(**fil).filter(username=name).count()
    num_bad = VectorsOneVersion2.objects.filter(**fil).count() - num_good
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
    print('good aver=' + str(aver_g/num_good))
    print('bad aver=' + str(aver_b / num_bad))
    print('frr=' + str(frr / num_good))
    print('far=' + str(far / num_bad))





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


def get_arrays_re(criterion, patterns, name=None):
    print(patterns)
    mass = VectorsOneVersion2.objects.filter(username=name).filter(**criterion).values_list(*patterns)
    X = []
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
        X.append(l_X.copy())
    X = np.array(X)
    return X

def SNE(collection, pattern_list):
    # данные для обучения
    # patterns = [
    #    # 'days', 'day_parts',
    #     'activity_time',
    #      'middle_pause', 'middle_pause2', 'middle_pause3',
    #   #  'quantity_middle_pause', 'quantity_middle_pause2', 'quantity_middle_pause3',
    #   #  'start_comp_pause',
    #     'urls',# 'url_freq_pause',
    #     #'url_maps',
    #     'domains',
    #     #'dom_freq_pause',
    #      'domain_maps',
    #  #   'url_bi', 'url_bi_pauses',
    #  #   'dom_bi', 'dom_bi_pauses',
    #   #  'url_tri', 'url_tri_pauses',
    #   #  'dom_tri', 'dom_tri_pauses',
    #    'domain_type',
    #   #  'domain_categories'
    # ]

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