from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from analyse.models import VectorsOneVersion
# количество кликов в одном векторе (пользователю предлагается выбрать
clicks = [
    '5',
    '15',
    '30'
]

# выделяемые признаки
exclude = ['id', 'team', 'username', 'number_parts_per_day', 'clicks', 'thousand', 'type']
patterns = [f.name for f in VectorsOneVersion._meta.fields if f.name not in exclude]

number_parts_per_day = [
    '8',
    '12',
]
# Применяемые алгоритмы
classification_algorithms = {
        'rf': RandomForestClassifier(),
        'lg': LogisticRegression(),
        'SVC': SVC()
    }

