import requests

from django.test import TestCase, Client

from base.analys import Main
from ML.create_vectors import CreateVectors
from ML.create_vectors_in_two_files import CreateVectorsApart


class Test1(TestCase):
    client = Client()

    def test1(self):
        #requests.post('http://127.0.0.1:8000/user/')

        clicks = [5, 15, 30]#, 10, 15, 20]    # количество кликов, которое будет в одном векторе
        teams = {                   # команды и перечень тех, кто в них входит
            1: ('bv', 'im', 'ro'),
            #2: ('bv', 'dy', 'im')
            #2: ('dy', 'im', 'ro', 'ili')
        }
        teams_set = {               # команды и перечень (обучающих, обучающих+тестовых данных) в тысячах
            1: [(47, 67)],#, (81, 115)],
            #2: [(33, 47)]
        }

        day_parts = [8] # на сколько частей делим день
        permissions = [
            #['-'],
            # ['domain'],
            ['domain', 'domain_maps'],
            # ['domain', 'url_maps'],
            # ['domain', 'url_maps', 'domain_maps'],
            # ['domain', 'dom_bi'],
            # ['domain', 'dom_bi', 'dom_tri'],
            # ['domain', 'dom_bi', 'dom_tri', 'url_bi', 'url_tri'],
            # ['domain', 'url_bi', 'url_tri'],
            # ['domain', 'dom_bi', 'dom_tri', 'grams_pause'],
            # ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'grams_pause'],
            #['domain', 'domain_maps', 'url_maps', 'start_comp'],
            ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'url_maps', 'grams_pause', 'url_bi', 'url_tri'],
        ]
        for num, names in teams.items():
            print('team ' + str(num))
            for data in teams_set[num]:
                #Main(data[0], names, mode='work', team=str(num))
                for permission in permissions:
                    CreateVectorsApart(data, names, clicks, day_parts, permission, 'team ' + str(num))

    def test2(self):
        add_info_by_namedir = " new"
        clicks = [15]#, 10, 15, 20]    # количество кликов, которое будет в одном векторе
        teams = {                   # команды и перечень тех, кто в них входит
            #1: ('bv', 'im', 'ro'),
            #2: ('bv', 'dy', 'im')
            2: ('dy', 'im', 'ro', 'ili')
        }
        teams_set = {               # команды и перечень (обучающих, обучающих+тестовых данных) в тысячах
            #1: [(47, 67)],#, (81, 115)],
            2: [(33, 47)]
        }

        day_parts = [8] # на сколько частей делим день
        permissions = [
            ['-'],
            ['domain_maps'],

            ['domain'],
            ['domain', 'domain_maps'],

            ['domain', 'url_maps'],
            ['domain', 'url_maps', 'domain_maps'],

            ['domain', 'dom_bi', 'dom_tri', 'grams_pause'],
            ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'grams_pause'],

            ['domain', 'dom_bi', 'dom_tri', 'url_maps', 'grams_pause', 'url_bi', 'url_tri'],
            ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'url_maps', 'grams_pause', 'url_bi', 'url_tri'],
            # ['domain', 'dom_bi'],
            # ['domain', 'dom_bi', 'dom_tri'],
            # ['domain', 'dom_bi', 'dom_tri', 'url_bi', 'url_tri'],
            # ['domain', 'url_bi', 'url_tri'],
            # ['domain', 'dom_bi', 'dom_tri', 'grams_pause'],

            #['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'url_maps', 'grams_pause'],
            #['domain', 'domain_maps', 'url_maps', 'start_comp'],

            # ['domain', 'dom_bi', 'dom_tri', 'grams_pause', 'url_bi', 'url_tri'],

        ]
        for num, names in teams.items():
            print('team ' + str(num))
            for data in teams_set[num]:
                #Main(data[0], names, mode='work', team=str(num))
                for permission in permissions:
                    CreateVectorsApart(data, names, clicks, day_parts, permission, 'team ' + str(num), add_info_by_namedir)

    def test3(self):
        payload = {'key1': ['value1', 'kk'] , 'key2': 'value2'}
        resp = self.client.get('/user/', payload)
        print(resp.content)





