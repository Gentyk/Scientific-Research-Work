from django.test import TestCase

from work_files.analys import Main
from ML.create_vectors import CreateVectors
from ML.create_vectors_in_two_files import CreateVectorsApart


class Test1(TestCase):

    def test1(self):
        clicks = [5]#, 10, 15, 20]    # количество кликов, которое будет в одном векторе
        teams = {                   # команды и перечень тех, кто в них входит
            1: ('bv', 'im', 'ro'),
            2: ('bv', 'dy', 'im')
        }
        teams_set = {               # команды и перечень (обучающих, обучающих+тестовых данных) в тысячах
            1: [(47, 67), (81, 115)],
            #2: [(33, 47)]
        }
        excludes = ['map', 'gramms', 'pause']    #   исключения, с которыми и без которых стоит сделать datasetы
        day_parts = [8, 12] # на сколько частей делим день
        for num, names in teams.items():
            print('team ' + str(num))
            for data in teams_set[num]:
                Main(data[0], names)
                CreateVectorsApart(data, names, clicks, day_parts)


