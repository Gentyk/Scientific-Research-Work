from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

# количество кликов в одном векторе (пользователю предлагается выбрать
clicks = [
    '5',
    '15',
    '30'
]

# выделяемые признаки
patterns = [
    'domain',
    'dom_bi',
    'dom_tri',
    'domain_maps',
    'url_maps',
    'grams_pause',
    'url_bi',
    'url_tri'
]

# Применяемые алгоритмы
classification_algorithms = {
        'rf': RandomForestClassifier(),
        'lg': LogisticRegression(),
        'SVC': SVC()
    }

