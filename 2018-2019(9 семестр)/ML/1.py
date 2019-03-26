import csv
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import normalize

from fff import MajorityVoteClassifier

path = "D:\\Documents\\Github\\NIR\\2018-2019(9 семестр)\\log_anal\\dataset\\team 2 perm ['domain', 'domain_maps'] 8t 5cl 33"
#path = "..\\log_anal\\dataset\\team 1 perm ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'url_maps', 'grams_pause', 'url_bi', 'url_tri'] 8t 15cl 47"
# имена юнитов
names = ['dy', 'im', 'ro', 'ili']
#names = ['bv', 'im', 'ro']

# находим количество столбцов в csv
with open(path + '\\TRAINING.csv','r') as f:
    reader=csv.reader(f,delimiter=',')
    n=len(next(reader))

print(n)
# данные для обучения
df = pd.read_csv(path + '\\TRAINING.csv', engine='python')
df.columns = ['Y'] + ['X'+str(i) for i in range(n-1)]
df.head()
X = df.values[:, 1:3]
Y = df.values[:, 0]
print(type(X))
print(Y[0])
print(X)
# len_X = len(X)
# #print(len_X0)
#
# # нормализация
# # scaler = StandardScaler()
# # scaler.fit(X)
# # X = scaler.transform(X)
#
# # нормализация 2
#
#
# # данные для тестирования
# df1 = pd.read_csv(path + '\\TESTING.csv', engine='python')
# df1.columns = ['Y'] + ['X' + str(i) for i in range(n - 1)]
# df1.head()
# test_X = df1.values[:, 1:]
# test_Y = df1.values[:, 0]
# n_test = len(test_Y)
# #test_X = scaler.transform(test_X)
# print(type(X))
# print(type(test_X))
#
# # нормализация 2
# l_X = X.tolist()
# l_test_X = test_X.tolist()
# XX = l_X + l_test_X
# XX = np.asarray(XX)
# X2 = normalize(XX)
# X = X2[:len_X]
# test_X = X2[len_X:]
#
#
# # данные для определения FAR и FRR
# n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
# for name in test_Y:
#     n_login_attempt[name] += 1
#
# print(n_login_attempt)
#
# # несколько алгоритмов МО
# ml = {
#      #'rf': RandomForestClassifier(),
#      #'knn': KNeighborsClassifier(n_neighbors=5, weights='uniform', p=1, algorithm='brute'),
#       'lg': LogisticRegression(),
#       'SVC': SVC(),
#     #'bg': BaggingClassifier(RandomForestClassifier(), max_samples=0.5, max_features=0.5),
#
#     # 'pr': MLPClassifier(hidden_layer_sizes=(100, 50, ), max_iter=50)
#       }
# for name_alg, algorithm in ml.items():
#     print('\n'+name_alg)
#     a = algorithm
#     a.fit(X, Y)
#     result = a.predict(test_X)
#     #print(result)
#
#     # проверка результатов
#     FAR = {name: 0 for name in names}  # ложное положительное решение
#     FRR = {name: 0 for name in names}  # случайно заблокировали владельца
#
#     good = 0
#     for i in range(n_test):
#         if result[i] == test_Y[i]:
#             good += 1
#         for name in names:
#             if result[i] == name and test_Y[i] != name:
#                 FAR[name] += 1
#             if result[i] != name and test_Y[i] == name:
#                 FRR[name] += 1
#     print('точность:' + str(good / n_test))
#     for name in names:
#         print(name + " FAR:" + str(FAR[name] / n_test))
#         print(name + " FRR:" + str(FRR[name] / n_login_attempt[name]))
#
