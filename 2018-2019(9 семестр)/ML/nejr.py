import csv
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier

from fff import MajorityVoteClassifier

team = 2
s_path = "..\\log_anal\\dataset\\"
paths = [
    "team {} perm ['-'] 8t {}cl 33",
    # "team {} perm ['domain', 'domain_maps'] 8t {}cl 47",
    # "team {} perm ['domain', 'url_maps', 'domain_maps'] 8t {}cl 47",
    # "team {} perm ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'grams_pause'] 8t {}cl 47",
    # "team {} perm ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'url_maps', 'grams_pause', 'url_bi', 'url_tri'] 8t {}cl 47",
]
# имена юнитов
names = ['dy', 'im', 'ro', 'ili']
#names = ['bv', 'im', 'ro']
clicks = [5, 15, 30]

for pt in paths:
    for click in clicks:
        path = s_path + pt.format(team, click)
        # находим количество столбцов в csv
        with open(path + '\\TRAINING.csv','r') as f:
            reader=csv.reader(f,delimiter=',')
            n=len(next(reader))

        print(n)
        # данные для обучения
        df = pd.read_csv(path + '\\TRAINING.csv')
        df.columns = ['Y'] + ['X'+str(i) for i in range(n-1)]
        df.head()
        X = df.values[:, 1:]
        Y = df.values[:, 0]
        len_X0 = len(X[0])
        #print(len_X0)

        # нормализация
        scaler = StandardScaler()
        scaler.fit(X)
        X = scaler.transform(X)

        # данные для тестирования
        df1 = pd.read_csv(path + '\\TESTING.csv')
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
        iters = [5, 10, 15, 25, 50, 75, 100, 150]
        ml = {
            # 'pr': MLPClassifier(hidden_layer_sizes=(100, 50, ), max_iter=50)
              }
        with open(path + '\\nej_otch.txt', 'w') as f:
            print('start make file')

        for iter in iters:
            print('\n'+str(iter))
            a = MLPClassifier(hidden_layer_sizes=(100, ), max_iter=iter)
            a.fit(X, Y)
            result = a.predict(test_X)
            #print(result)

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
            with open(path + '\\nej_otch.txt', 'a') as f:
                f.write('\nэпохи:' + str(iter))
                f.write('\n' + 'точность:' + str(good / n_test))
                summ_FAR = 0
                summ_FRR = 0
                for name in names:
                    f.write('\n' + name + " FAR:" + str(FAR[name] / n_test))
                    f.write('\n' + name + " FRR:" + str(FRR[name] / n_login_attempt[name]))
                    summ_FAR += FAR[name] / n_test
                    summ_FRR += FRR[name] / n_login_attempt[name]
                f.write("\nсредний FAR:" + str(summ_FAR / len(names)))
                f.write("\nсредний FRR:" + str(summ_FRR / len(names)))

