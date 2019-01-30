from sklearn.base import BaseEstimator
from sklearn.base import ClassifierMixin
from sklearn.preprocessing import LabelEncoder
from sklearn.externals import six
from sklearn .base import clone
from sklearn.pipeline import _name_estimators
import numpy as np
import operator


class MajorityVoteClassifier(BaseEstimator, ClassifierMixin) :
    """ Ансамблевый классификатор на основе мажоритарного голосования
    Параметры
    classifiers : массивоподобный , форма = [n_classifiers]
    Разные классификаторы для ансамбля
    vote : str, ( 'classlabel' , 'p robaЬility )
    По умолчанию: <classlabel '
    Если метка класса <classlabel ', то прогноз
    основывается на argmax меток классов .
    В противном случае если <probaЬility , то для
    рогноза метки класса используется
    argmax суммы вероятностей
    (рекомендуется для откалиброванных классификаторов) .
    weights : массивоподобный , фо ма = [n_classifiers]
    Факультативно , о умолчанию: None
    Если предоставлен список из значений 'int' либо 'float ' , то
    Классификаторы взвешиваются по важности;
    Если 'weights=None·, то используются равномерные веса
    """

    def init(self, classifiers, vote='classlabel', weights=None):
        self.classifiers = classifiers
        self.named_classifiers = {key: value for key, value in _name_estimators(classifiers)}
        self.vote = vote
        self.weights = weights

    def fit(self, X, y):
        """ВЫполнение подгонки классификаторов"""

        # Использовать LabelEncoder, чтобы гарантировать , что
        # метки классов начинаются с , что важно для
        # вызова np .argmax в self.predict
        self.lablenc_ = LabelEncoder()
        self.lablenc_.fit(y)

        self.classes = self.lablenc_.classes_
        self.classifiers_ = []
        for clf in self.classifiers:
            fitted_clf = clone(clf).fit(X,
                                        self.lablenc_.transform(y))
            self.classifiers_.append(fitted_clf)
        return self