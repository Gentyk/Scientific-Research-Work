import csv
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# имена юнитов
names = ['ys', 'bv']#['mk', 'ro', 'ys', 'dy', 'bv']

# находим количество столбцов в csv
with open('..\\log_anal\\simple2TRAINING.csv','r') as f:
    reader=csv.reader(f,delimiter=',')
    n=len(next(reader))

# данные для обучения
df = pd.read_csv('..\\log_anal\\simple2TRAINING.csv')
df.columns = ['Y'] + ['X'+str(i) for i in range(n-1)]
df.head()
X = df.values[:, 1:42]
Y = df.values[:, 0]

# данные для тестирования
df1 = pd.read_csv('..\\log_anal\\simple2TESTING.csv')
df1.columns = ['Y'] + ['X' + str(i) for i in range(n - 1)]
df1.head()
test_X = df1.values[:, 1:42]
test_Y = df1.values[:, 0]
n_test = len(test_Y)

# данные для определения FAR и FRR
n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
for name in test_Y:
    n_login_attempt[name] += 1

print(n_login_attempt)

# несколько алгоритмов МО
ml = {'rf': RandomForestClassifier(),
      'knn': KNeighborsClassifier(n_neighbors=5, weights='uniform', p=1, algorithm='brute'),
      'SVC': SVC()}

# обучение, тестирование, вывод на экран
for name_alg, algorithm in ml.items():
    print('\n'+name_alg)
    a = algorithm
    a.fit(X, Y)
    result = a.predict(test_X)

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
