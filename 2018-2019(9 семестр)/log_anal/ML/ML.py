import csv
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import time

def ml(path, names):
    # находим количество столбцов в csv
    with open(path + '\\TRAINING.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        n = len(next(reader))
    time.sleep(1000)
    # данные для обучения
    df = pd.read_csv(path + '\\TRAINING.csv')
    df.columns = ['Y'] + ['X' + str(i) for i in range(n - 1)]
    df.head()
    X = df.values[:, 1:n]
    Y = df.values[:, 0]

    # данные для тестирования
    df1 = pd.read_csv(path + '\\TESTING.csv')
    df1.columns = ['Y'] + ['X' + str(i) for i in range(n - 1)]
    df1.head()
    test_X = df1.values[:, 1:n]
    test_Y = df1.values[:, 0]
    n_test = len(test_Y)

    # данные для определения FAR и FRR
    n_login_attempt = {name: 0 for name in names}  # сколько раз легитимный пользователь пытался войти
    for name in test_Y:
        n_login_attempt[name] += 1

    print(n_login_attempt)

    # несколько алгоритмов МО
    ml = {'rf': RandomForestClassifier(),
          'lg': LogisticRegression(),
          'SVC': SVC()}

    with open(path + "\\otch.txt", 'w') as f:
        f.write(str(names) + " " + str(n))
        # обучение, тестирование, вывод на экран
        for name_alg, algorithm in ml.items():
            f.write('\n' + name_alg)
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
            f.write('\n' +'точность:' + str(good / n_test))
            summ_FAR = 0
            summ_FRR = 0
            for name in names:
                f.write('\n' + name + " FAR:" + str(FAR[name] / n_test))
                f.write('\n' + name + " FRR:" + str(FRR[name] / n_login_attempt[name]))
                summ_FAR += FAR[name] / n_test
                summ_FRR += FRR[name] / n_login_attempt[name]
            f.write("\nсредний FAR:" + str(summ_FAR / len(names)))
            f.write("\nсредний FRR:" + str(summ_FRR / len(names)))
