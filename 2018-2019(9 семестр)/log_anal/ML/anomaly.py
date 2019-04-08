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

from time import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import offsetbox
from sklearn import (manifold, datasets, decomposition, ensemble,
                     discriminant_analysis, random_projection)


def SNE(collection):#exit(), pattern_list):
    # данные для обучения
    patterns = [
       # 'days', 'day_parts',
        'activity_time',
        'middle_pause', 'middle_pause2', 'middle_pause3',
      #  'quantity_middle_pause', 'quantity_middle_pause2', 'quantity_middle_pause3',
        'start_comp_pause',
        'urls', 'url_freq_pause', 'url_maps',
        'domains', 'dom_freq_pause', 'domain_maps',
     #   'url_bi', 'url_bi_pauses',
        'dom_bi', 'dom_bi_pauses',
      #  'url_tri', 'url_tri_pauses',
      #  'dom_tri', 'dom_tri_pauses',
        'domain_type',
      #  'domain_categories'
    ]

    patterns.append('username')
    fil = {'collection' : collection, 'type': 1}
    X, Y = get_arrays_re(fil, patterns, 'tanchik')
    print(X)
    n = len(Y)
    print('Длина вектора' + str(len(X[0])))

    # данные для тестирования
    fil = {'collection': collection, 'type': 2}
    test_X, test_Y = get_test_arrays(fil, patterns, 'tanchik', len(X[0]))
    print(test_X)

    n_test = len(test_Y)
    ml = {'IF': IsolationForest()}
    # обучение, тестирование, вывод на экран
    for name_alg, algorithm in ml.items():
        print('\n' + name_alg)
        a = algorithm
        a.fit(X)
        result = a.predict(test_X)
        aver_g = 0
        aver_b = 0
        for i in range(n_test):
            if result[i] == test_Y[i]:
                aver_g += 1
            else:
                aver_b += 1
        print('good aver=' + str(aver_g/n_test))





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

        # if len(l_X) != l:
        #     continue
        Y.append(line[-1])
        X.append(l_X.copy())
    print(set(Y))
   # Y = [1 if name==i else -1 for i in Y]

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
    Y = [1 for i in Y]

    print('line'+str(len(X[0])))
    X = np.array(X)
    Y = np.array(Y)
    return X, Y






def anomaly1(collection):#exit(), pattern_list):
    # данные для обучения
    patterns = [
       # 'days', 'day_parts',
        'activity_time',
         'middle_pause', 'middle_pause2', 'middle_pause3',
      #  'quantity_middle_pause', 'quantity_middle_pause2', 'quantity_middle_pause3',
      #  'start_comp_pause',
        'urls',# 'url_freq_pause',
        #'url_maps',
        'domains',
        #'dom_freq_pause',
         'domain_maps',
     #   'url_bi', 'url_bi_pauses',
     #   'dom_bi', 'dom_bi_pauses',
      #  'url_tri', 'url_tri_pauses',
      #  'dom_tri', 'dom_tri_pauses',
       'domain_type',
      #  'domain_categories'
    ]

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



