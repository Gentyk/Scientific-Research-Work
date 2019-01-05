import csv
import pandas as pd

# имена юнитов
names = ['ys', 'bv']#['mk', 'ro', 'ys', 'dy', 'bv']
#names = ['ili', 'bv', 'valli']
# находим количество столбцов в csv
with open('.\\DataSet\\TRAINING.csv','r') as f:
    reader=csv.reader(f,delimiter=',')
    n=len(next(reader))

# данные для обучения
df = pd.read_csv('.\\DataSet\\TRAINING.csv')
df.columns = ['Y'] + ['X'+str(i) for i in range(n-1)]
df.head()

X = df.values[:, 1:n]
Y = df.values[:, 0]

mass = [0 for i in range(n)]
ff = {i: mass[:] for i in names}
ff1 = {i: 0 for i in names}
for j in range(len(Y)):
    ff1[Y[j]] += X[j][4]
    for i in range(n-1):
         ff[Y[j]][i] +=  X[j][i]
#print(ff)

import xlsxwriter
workbook = xlsxwriter.Workbook('Expenses1.xlsx')
worksheet = workbook.add_worksheet()
row = 0
col = 0

# Iterate over the data and write it out row by row.
for name, v in ff.items():
    #print(ff[name][8])
    worksheet.write(row, col, name)
    j = 1

    for i in v:
        worksheet.write(row, col + j, i)
        j += 1
    row += 1

workbook.close()
