import csv
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import time

from fff import MajorityVoteClassifier

# имена юнитов
#names = ['ro', 'bv', 'im']#
names = ['dy', 'im', 'ro', 'ili']
path = "D:\\Documents\\Github\\NIR\\2018-2019(9 семестр)\\log_anal\\dataset\\team 2 perm ['domain', 'domain_maps'] 8t 5cl 33\\"

# находим количество столбцов в csv
with open(path + 'TRAINING.csv','r') as f:
    reader=csv.reader(f,delimiter=',')
    n=len(next(reader))

print(n)
print('start read train')
# данные для обучения
df = pd.read_csv(path + 'TRAINING.csv', engine='python')
df.columns = ['Y'] + ['X'+str(i) for i in range(n-1)]
df.head()
X = df.values[:, 1:20]
Y = df.values[:, 0]

print('end read train')
# данные для тестирования
df1 = pd.read_csv(path + 'TESTING.csv', engine='python')
df1.columns = ['Y'] + ['X' + str(i) for i in range(n - 1)]
df1.head()
test_X = df1.values[:, 1:20]
test_Y = df1.values[:, 0]
n_test = len(test_Y)

# данные для определения FAR и FRR
n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
for name in test_Y:
    n_login_attempt[name] += 1

print(n_login_attempt)

# несколько алгоритмов МО
# ml = {#'rf': RandomForestClassifier(),
#       #'knn': KNeighborsClassifier(n_neighbors=5, weights='uniform', p=1, algorithm='brute'),
#       #'SVC': SVC(),
#       'lg': LogisticRegression(),
#       }
# for name_alg, algorithm in ml.items():
#     print('\n'+name_alg)
#     a = algorithm
#     a.fit(X, Y)
#     result = a.predict(test_X)
#     print(result)
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
#     print('ошибается вообще:' + str(good / n_test))
#     for name in names:
#         print(name + " FAR:" + str(FAR[name] / n_test))
#         print(name + " FRR:" + str(FRR[name] / n_login_attempt[name]))

print('start train')
a = MajorityVoteClassifier(classifiers=[RandomForestClassifier(), SVC(), LogisticRegression()])
# обучение, тестирование, вывод на экран

a.fit(X, Y)
print('end train')
result = a.predict(test_X)
print(result)

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
print('точность:' + str(good / n_test))
FAR = 0
FRR = 0
for name in names:
    FAR += FAR[name] / n_test
    FRR += FRR[name] / n_login_attempt[name]
    print(name + " FAR:" + str(FAR[name] / n_test))
    print(name + " FRR:" + str(FRR[name] / n_login_attempt[name]))
print('средний FAR' + str(FAR / 4))
print('средний FRR' + str(FRR / 4))
