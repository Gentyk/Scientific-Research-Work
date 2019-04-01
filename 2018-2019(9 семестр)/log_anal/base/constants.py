from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingRegressor

from analyse.models import VectorsOneVersion1
# количество кликов в одном векторе (пользователю предлагается выбрать
clicks = [
    '5',
    '15',
    '30'
]

# выделяемые признаки
exclude = ['id', 'team', 'username', 'number_parts_per_day', 'clicks', 'thousand', 'type', 'last_click', 'collection']
patterns = [f.name for f in VectorsOneVersion1._meta.fields if f.name not in exclude]

number_parts_per_day = [
    '8',
    '12',
]
# Применяемые алгоритмы
classification_algorithms = {
        'rf': RandomForestClassifier(),
        'lg': LogisticRegression(),
        'SVC': SVC(),
        'AdaBoost': AdaBoostClassifier(),
        'GradientBoost': GradientBoostingClassifier(),
    }

regression_algorithms = {
        'GradientBoostRegress': GradientBoostingRegressor(),
}

