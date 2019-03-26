from sklearn import svm
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import tree
df = pd.read_csv('vnames.csv')
df.columns = ['Y',
                'X1', 'X2', 'X3', 'X4', 'X5',
                'X6', 'X7', 'X8', 'X9', 'X10',
                'X11', 'X12', 'X13', 'X14', 'X15',
                'X16', 'X17', 'X18', 'X19', 'X20',
                'X21', 'X22', 'X23', 'X24', 'X25',
                'X26', 'X27', 'X28', 'X29', 'X30',
                'XX1', 'XX2', 'XX3', 'XX4', 'XX5',
                'XX6', 'XX7', 'XX8', 'XX9', 'XX10',
                'XX11', 'XX12', 'XX13', 'XX14', 'XX15',
                'XX16', 'XX17', 'XX18', 'XX19', 'XX20',
                'XX21', 'XX22', 'XX23', 'XX24', 'XX25',
                'XX26', 'XX27', 'XX28', 'XX29', 'XX30',
                'XXX1', 'XXX2', 'XXX3', 'XXX4', 'XXX5',
                'XXX6', 'XXX7', 'XXX8', 'XXX9',

              ]
df.head()
from sklearn.model_selection  import train_test_split
decision = tree.DecisionTreeClassifier(criterion='gini')
X = df.values[:, 1:70]
Y = df.values[:, 0]
trainX, testX, trainY, testY = train_test_split( X, Y, test_size = 0.3)
decision.fit(trainX, trainY)
print('Accuracy: \n', decision.score(testX, testY))
from sklearn.externals.six import StringIO
from IPython.display import Image
import pydotplus as pydot
dot_data = StringIO()
tree.export_graphviz(decision, out_file=dot_data)
graph = pydot.graph_from_dot_data(dot_data.getvalue())
graph.write_png("iris.png")