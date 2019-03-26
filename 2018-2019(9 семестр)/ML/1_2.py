import csv
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier

from fff import MajorityVoteClassifier

# имена юнитов
names = ('bv', 'im', 'ro')#['dy', 'im', 'ro', 'ili']

# находим количество столбцов в csv
with open('..\\log_anal\\dataset\\www8t 5cl 47\\TRAINING.csv','r') as f:
    reader=csv.reader(f,delimiter=',')
    n=len(next(reader))

print(n)

# данные для обучения
df = pd.read_csv('..\\log_anal\\dataset\\www8t 5cl 47\\TRAINING.csv')
df.columns = ['Y'] + ['X'+str(i) for i in range(n-1)]
df.head()
X = df.values[:, 1:]
Y = df.values[:, 0]
len_X0 = len(X[0])
print(len_X0)

# нормализация
scaler = StandardScaler()
scaler.fit(X)
X = scaler.transform(X)

# данные для тестирования
df1 = pd.read_csv('..\\log_anal\\dataset\\www8t 5cl 47\\TESTING.csv')
df1.columns = ['Y'] + ['X' + str(i) for i in range(n - 1)]
df1.head()
test_X = df1.values[:, 1:]
test_Y = df1.values[:, 0]
n_test = len(test_Y)
test_X = scaler.transform(test_X)

# данные для определения FAR и FRR
n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
for name in test_Y:
    n_login_attempt[name] += 1

print(n_login_attempt)

# несколько алгоритмов МО
ml = {#'rf': RandomForestClassifier(criterion='gini'),
      #'knn': KNeighborsClassifier(n_neighbors=5, weights='uniform', p=1, algorithm='brute'),
      'SVC': SVC(),
      #'lg': LogisticRegression(),
    #'pr': MLPClassifier(hidden_layer_sizes=(100, ), max_iter=100)
      }
for name_alg, algorithm in ml.items():
    print('\n'+name_alg)
    a = algorithm
    a.fit(X, Y)
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
    print('ошибается вообще:' + str(good / n_test))
    for name in names:
        print(name + " FAR:" + str(FAR[name] / n_test))
        print(name + " FRR:" + str(FRR[name] / n_login_attempt[name]))

