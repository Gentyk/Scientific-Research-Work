from sklearn import svm
import pandas
import matplotlib.pyplot as plt
import seaborn as sns
df = pandas.read_csv('flowers.csv')
df.columns = ['X1', 'X2', 'X3', 'X4', 'Y']
df.head()


from sklearn.model_selection import train_test_split
support = svm.SVC()
X = df.values[:, 0:2]
Y = df.values[:, 4]
#print(Y)
trainX, testX, trainY, testY = train_test_split(X, Y, test_size=0.3)

support.fit(trainX, trainY)
print('Accuracy: \n', support.score(testX, testY))
pred = support.predict(testX)
print("!")

sns.set_context("notebook", font_scale=1.1)
sns.set_style("ticks")
sns.lmplot('X1','X2', scatter=True, fit_reg=False, data=df, hue='Y')
plt.ylabel('X2')
plt.xlabel('X1')
plt.show()

