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

    def __init__(self, classifiers, vote='classlabel', weights=None):
        print("!!!")
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

    def predict(self, X):
        """ Спрогнозировать метки классов для Х.

    Параметры
    Х: {массивоподобный, разреженная матрица),
    форма = (n_sarnples, n_features]
    Матрица
    тренировочных
    образцов.
    Возвращает
    rnaj
    _vote: массивоnодобный, форма = [n_sarnples]
    Сnрогнозированные
    метки
    классов."""
        if self.vote == 'probability ':
            maj_vote = np.argmax(self.predict_proba(X), axis=1)
        else:  # голосование 'classlabel'
        # Аккумулировать результаты из вызовов clf.predict
            predictions = np.asarray([clt.predict(X)
                                         for clt in
                                     self.classifiers_])
            print(predictions)
            maj_vote = np.apply_along_axis(
                lambda x: np.argmax(np.bincount(x, weights=self.weights)),
                axis = 0,
                arr = predictions)
            print(maj_vote)
        maj_vote = self.lablenc_.inverse_transform(maj_vote)
        return maj_vote

    def predict_proba(self, X):
        probas = np.asarray([clf.predict_proba(X)
                             for clf in self.classifiers])
        avg_proba = np.average(probas,
                               axis=0, weights=self.weights)
        return avg_proba