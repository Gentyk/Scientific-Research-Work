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

path = "D:\\Documents\\Github\\NIR\\2018-2019(9 семестр)\\log_anal\\dataset\\team 2 perm ['domain', 'domain_maps'] 8t 5cl 33continuous a"
test_path = "D:\\Documents\\Github\\NIR\\2018-2019(9 семестр)\\log_anal\\dataset\\team 2 perm ['domain', 'domain_maps'] 8t 15cl 33"
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
X = df.values[:, 1:]
Y = df.values[:, 0]
len_X = len(X)
#print(len_X0)


# данные для тестирования
df1 = pd.read_csv(path + '\\TESTING.csv', engine='python')
df1.columns = ['Y'] + ['X' + str(i) for i in range(n - 1)]
df1.head()
test_X = df1.values[:, 1:]
#test_Y = df1.values[:, 0]


print(type(X))
print(type(test_X))

# нормализация
scaler = StandardScaler()
scaler.fit(X)
X = scaler.transform(X)
test_X = scaler.transform(test_X)

df2 = pd.read_csv(test_path + '\\TESTING.csv', engine='python')
df2.columns = ['Y'] + ['X' + str(i) for i in range(2088)]
df2.head()
test_Y = df2.values[:, 0]
n_test = len(test_Y)


# данные для определения FAR и FRR
n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
for name in test_Y:
    n_login_attempt[name] += 1

print(n_login_attempt)

# несколько алгоритмов МО
ml = {
     #'rf': RandomForestClassifier(),
     #'knn': KNeighborsClassifier(n_neighbors=5, weights='uniform', p=1, algorithm='brute'),
      'lg': LogisticRegression(),
      'SVC': SVC(),
    #'bg': BaggingClassifier(RandomForestClassifier(), max_samples=0.5, max_features=0.5),

    # 'pr': MLPClassifier(hidden_layer_sizes=(100, 50, ), max_iter=50)
      }
for name_alg, algorithm in ml.items():
    print('\n'+name_alg)
    a = algorithm
    a.fit(X, Y)

    #print(result)

    # проверка результатов
    FAR = {name: 0 for name in names}  # ложное положительное решение
    FRR = {name: 0 for name in names}  # случайно заблокировали владельца

    good = 0
    j = 0
    ff = test_X.tolist()
    for i in range(n_test):
        mass = np.array(ff[j:j+10])
        if not mass:
        n_results = a.predict(mass)
        results = n_results.tolist()
        result = max(set(results), key=results.count)
        if result == test_Y[i]:
            good += 1
        for name in names:
            if result == name and test_Y[i] != name:
                FAR[name] += 1
            if result != name and test_Y[i] == name:
                FRR[name] += 1
        print("!")
        j += 15
    print('точность:' + str(good / n_test))
    for name in names:
        print(name + " FAR:" + str(FAR[name] / n_test))
        print(name + " FRR:" + str(FRR[name] / n_login_attempt[name]))

