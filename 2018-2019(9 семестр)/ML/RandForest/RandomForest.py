import csv
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

print("!!!!")
with open('..\\DataSet\\TRAINING.csv','r') as f:

    reader=csv.reader(f,delimiter=',')
    n=len(next(reader))

# обучение
df = pd.read_csv('..\\DataSet\\TRAINING.csv')
df.columns = ['Y'] + ['X'+str(i) for i in range(n-1)]
df.head()

X = df.values[:, 1:n]
Y = df.values[:, 0]
RF = RandomForestClassifier()
RF.fit(X, Y)



# тестирование
df1 = pd.read_csv('..\\DataSet\\TESTING.csv')
df1.columns = ['Y'] + ['X'+str(i) for i in range(n-1)]
df1.head()

test_X = df1.values[:, 1:n]
test_Y = df1.values[:, 0]
result = RF.predict(test_X)

# проверка результатов
n = len(test_Y)
good = 0
names = ['mk', 'ro', 'ys', 'dy', 'bv']
FAR = {name:0 for name in names}  # ложное положительное решение
FRR = {name:0 for name in names}  # случайно заблокировали владельца

for i in range(n):
    if result[i] == test_Y[i]:
        good += 1
    for name in names:
        if result[i] == name and test_Y[i] != name:
            FAR[name] += 1
        if result[i] != name and test_Y[i] == name:
            FRR[name] += 1
print(good/n)
for name in names:
    print(name + " FAR:" + str(FAR[name]/n))
    print(name + " FRR:" + str(FRR[name]/n))
