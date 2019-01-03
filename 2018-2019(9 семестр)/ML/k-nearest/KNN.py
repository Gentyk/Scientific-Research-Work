import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

# обучение
df = pd.read_csv('TRAINING.csv')
df.columns = ['Y'] + ['X'+str(i) for i in range(69)]
df.head()

X = df.values[:, 1:70]
Y = df.values[:, 0]
knn = KNeighborsClassifier()
knn.fit(X, Y)

# тестирование
df1 = pd.read_csv('TESTING.csv')
df1.columns = ['Y'] + ['X'+str(i) for i in range(69)]
df1.head()

test_X = df1.values[:, 1:70]
test_Y = df1.values[:, 0]
result = knn.predict(test_X)

# проверка результатов
n = len(test_Y)
good = 0
FAR = 0 # ложное положительное решение
FRR = 0 # случайно заблокировали владельца
for i in range(n):
    if result[i] == test_Y[i]:
        good += 1
    if result[i] == 'ili' and test_Y[i] != 'ili':
        FAR += 1
    if result[i] != 'ili' and test_Y[i] == 'ili':
        FRR += 1
print(good/n)
print(FAR/n)
print(FRR/n)
