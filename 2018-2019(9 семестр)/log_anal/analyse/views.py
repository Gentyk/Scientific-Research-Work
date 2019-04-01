from datetime import datetime, timedelta
from pytz import timezone
from os import listdir
from os.path import isfile, join
import re
import time
import threading

from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from django.views.generic.base import View

from analyse.models import Bigrams, Log, Trigrams, Teams, Domains, URLs, VectorsOneVersion1, Collections, ML
from base.new_analyse import base_analyse
from base.filling_the_database import filling
from base.base import create_vectors, train, get_better_patterns
from base.constants import classification_algorithms, patterns, clicks, number_parts_per_day, regression_algorithms
from ML.ML import combine_train

def get_selection(request, full_array):
    find_array = []
    for elem in full_array:
        obj = request.POST.get(elem)
        if obj:
            find_array.append(elem)
    return find_array

class InfoView(View):
    def get(self, request, *args, **kwargs):
        """
        Вывод общей информации
        """
        return render(request, 'analyse/info.html')

class UsersView(View):
    """
    Находит частные штучкки пользователей и заносит их в базу данных. По требованию достает инфу о каждом доступном
    пользователе.
    """

    def get(self, request, *args, **kwargs):
        """
        Вывод общей информации о каждом пользователе
        """
        # соберем имена всех пользователей из логов и БД
        names = []
        log_names = [f.split('.')[0] for f in listdir('logs') if isfile(join('logs', f))]
        base_usernames = [name[0] for name in Log.objects.all().distinct('username').values_list("username")]
        analyse_usernames = [name[0] for name in Teams.objects.all().values_list("username")]

        names = list(set(log_names + analyse_usernames + base_usernames))

        # далее для каждого пользователя собираем инфомацию
        result = [{'name': 'name', 'file':'file availability',  'db':'in database', 'analyse': 'analyse',
                   'log': 'log', 'bi': 'bi', 'tri': 'tri'}]
        for name in names:
            local = {'name': name}
            local['file'] = ("+" if name in log_names else "-")
            # если появится необходимость проверки логов на правильность
            #local['file'] = (check_logfile(name) if name in log_names else '-')
            local['db'] = ('+' if name in base_usernames else "-")
            local['log'] = Log.objects.filter(username=name).count()
            local['bi'] = Bigrams.objects.filter(username=name).count()
            local['tri'] = Trigrams.objects.filter(username=name).count()
            local['analyse'] = ("+" if name in analyse_usernames else "-")
            result.append(local.copy())
        context = {'log_names_list': result, 'teams': []}

        context['teams'].append({'t': 'team', 'u': 'user', 'url': 'urls', 'dom': 'domains', 'url_bi': 'url_bi',
                                 'dom_bi': 'dom_bi', 'url_tri': 'url_tri', 'dom_tri': 'dom_tri',
                                 't_bi': 't_bi', 't_tri': 't_tri', 'c_bi': 'c_bi', 'c_tri': 'c_tri',})
        date = Teams.objects.values()

        for i in date:
            context['teams'].append({
                't': i['team'],
                'u': i['username'],
                'url': len(i['frequent_urls']),
                'dom': len(i['frequent_domains']),
                'url_bi': len(i['frequent_bi_urls']),
                'dom_bi': len(i['frequent_bi_domains']),
                't_bi': len(i['frequent_bi_domains_type']),
                'c_bi': len(i['frequent_bi_domains_categories']),
                'url_tri': len(i['frequent_tri_urls']),
                'dom_tri': len(i['frequent_tri_domains']),
                't_tri': len(i['frequent_tri_domains_type']),
                'c_tri': len(i['frequent_tri_domains_categories']),
            })

        return render(request, 'analyse/users.html', context)

    def post(self, dop_info=None):
        t = threading.Thread(target=filling)
        t.start()
        return HttpResponse("success")


class UserView(View):
    """
    Выдача информации и изменение каких-либо данных одного определенного пользователя
    """
    def get(self, request, *args, **kwargs):
        """
        Вывод общей информации об определенном пользователе
        """
        return render(request, 'analyse/user.html')

class BaseView(View):
    def get(self, request, *args, **kwargs):
        """
        Вывод общей информации о всех таблицах
        """
        result = []
        result.append({'name': 'URLs', 'count': URLs.objects.all().count()})
        result.append({'name': 'Domains', 'count': Domains.objects.all().count()})
        result.append({'name': 'logs', 'count': Log.objects.all().count()})
        result.append({'name': 'bigramms', 'count': Bigrams.objects.all().count()})
        result.append({'name': 'trigramms', 'count': Trigrams.objects.all().count()})
        context = {'tables_list': result}
        return render(request, 'analyse/base_status.html', context)


class AnalyseView(View):
    """
    Запускает анализ для пользователей, данные которых есть в основных таблицах (Log, Bigramm, Trigramm)
    """
    names = [name[0] for name in Log.objects.all().distinct('username').values_list("username")]

    def get(self, request, *args, **kwargs):
        column_names = {'name': 'user', 'all': 'all', '1': '1 week', '2': '2 weeks', '3': '3 weeks'}
        data = {'users': self.names, 'users_table': [column_names], 'teams_table': []}
        for name in self.names:
            log = Log.objects.filter(username=name)
            start_time = log.earliest('click__time').click.time
            data['users_table'].append({
                'name': name,
                'all': log.count(),
                '1': log.filter(click__time__lte= start_time + timedelta(days=7)).count(),
                '2': log.filter(click__time__lte=start_time + timedelta(days=14)).count(),
                '3': log.filter(click__time__lte=start_time + timedelta(days=21)).count(),
            })

        data['teams_table'].append({'team': 'team', 'user': 'user', 'thousand': 'thousand'})
        u_data = Teams.objects.values('team', 'username', 'thousand')
        for i in u_data:
            data['teams_table'].append({'team': i['team'], 'user': i['username'], 'thousand': i['thousand']})

        return render(request, 'analyse/users_analyse.html', data)

    def post(self, request):
        """
        Для каждого пользователя находит частые url и другие признаки. В результате заполняется таблица Users.
        """
        team = int(request.POST["team"])
        if Teams.objects.filter(team=team):
            Teams.objects.filter(team=team).delete()
        clicks_thousand = int(request.POST["clicks"])
        users = get_selection(request, self.names)
        t = threading.Thread(target=base_analyse, args=(team, clicks_thousand, users,))
        t.start()
        return HttpResponse("success")


class VectorsView(View):
    """
    Запуск процесса формирования обучающих выборок или машинного обучения. В get запросе выводится менюшка для задания
    параметров.
    """
    teams = [str(team[0]) for team in Teams.objects.distinct('team').values_list('team')]

    def get(self, request, *args, **kwargs):
        self.teams = [str(team[0]) for team in Teams.objects.distinct('team').values_list('team')]

        data = {
            'teams': self.teams,
            'clicks': clicks,
            'day_parts': number_parts_per_day,
        }
        return render(request, 'analyse/train.html', data)

    def post(self, request):
        selected_teams = [int(i) for i in get_selection(request, self.teams)]
        selected_clicks = [int(i) for i in get_selection(request, clicks)]
        selected_day_parts = [int(i) for i in get_selection(request, number_parts_per_day)]
        t = threading.Thread(target=create_vectors, args=(selected_clicks, selected_day_parts, selected_teams))
        t.start()
        return HttpResponse("success")


class PatternsView(View):
    """
    Находит и выводит лучшие комбинации признаков
    """
    collections = ['|'.join([str(i) for i in team]) for team in Collections.objects.values_list()]

    def get(self, request):
        self.collections = [ '|'.join([str(i) for i in team]) for team in Collections.objects.values_list()]
        data = {
            'collections': self.collections,
        }
        return render(request, 'analyse/patterns.html', data)

    def post(self, request):
        collections_dict = {'|'.join([str(i) for i in team]): team for team in Collections.objects.values_list()}
        selected_collections = [collections_dict[i] for i in get_selection(request, self.collections)]
        t = threading.Thread(target=get_better_patterns, args=(selected_collections,))
        t.start()
        return HttpResponse("success")


class MLView(View):
    """
    Запуск машинного обучения с выбором признаков
    """

    collections = [ str(col.team) + '_' + str(col.clicks)
                             for col in Collections.objects.all() if VectorsOneVersion1.objects.filter(collection=col).count() > 1]
    local_patterns = patterns + ['5_best_patterns_set']
    def get(self, request, *args, **kwargs):
        self.collections = [ str(col.team) + '_' + str(col.clicks)
                             for col in Collections.objects.all() if VectorsOneVersion1.objects.filter(collection=col).count() > 1]
        best_results = [{'collection': 'collection', 'best_accuracy':'best_accuracy'}]
        for collection in Collections.objects.all():
            accuracy = [i[0] for i in ML.objects.filter(collection=collection).values_list('accuracy')]
            accuracy.sort(reverse=True)
            if accuracy:
                best_results.append({'collection': str(collection.team) + '_' + str(collection.clicks), 'best_accuracy': accuracy[0]})

        data = {
            'collections': self.collections,
            'patterns': self.local_patterns,
            'classification_algorithms': classification_algorithms,
            'regression_algorithms': regression_algorithms,
            'best_results': best_results,
        }
        return render(request, 'analyse/ML_run.html', data)

    def post(self, request):
        collections_dict = { str(col.team) + '_' + str(col.clicks): col
                             for col in Collections.objects.all() if VectorsOneVersion1.objects.filter(collection=col).count() > 1}
        selected_collections = [collections_dict[i] for i in get_selection(request, self.collections)]

        selected_patterns = [i for i in get_selection(request, self.local_patterns)]

        selected_algorithms = [i for i in get_selection(request, classification_algorithms)] + \
                              [i for i in get_selection(request, regression_algorithms)]
        print(selected_algorithms)
        t = threading.Thread(target=train, args=(selected_collections, selected_patterns, selected_algorithms))
        t.start()
        return HttpResponse("success")

class CombineML(View):
    def get(self, request, *args, **kwargs):
        """
        Выводим таблицу с информацией по точности и ошибкам
        """
        collections = [str(col.team) + '_' + str(col.clicks)
                            for col in Collections.objects.all() if
                            VectorsOneVersion1.objects.filter(collection=col).count() > 1]
        best_results = [{'collection': 'collection', 'best_accuracy': 'best_accuracy'}]
        for collection in Collections.objects.all():
            accuracy = [i[0] for i in ML.objects.filter(collection=collection).values_list('accuracy')]
            accuracy.sort(reverse=True)
            if accuracy:
                best_results.append(
                    {'collection': str(collection.team) + '_' + str(collection.clicks), 'best_accuracy': accuracy[0]})

        data = {
            'collections': collections,
           # 'classification_algorithms': classification_algorithms,
           # 'regression_algorithms': regression_algorithms,
            'best_results': best_results,
        }
        return render(request, 'analyse/CombineMLRun.html', data)

    def post(self, request):
        collections = [str(col.team) + '_' + str(col.clicks)
                            for col in Collections.objects.all() if
                            VectorsOneVersion1.objects.filter(collection=col).count() > 1]

        collections_dict = { str(col.team) + '_' + str(col.clicks): col
                             for col in Collections.objects.all() if VectorsOneVersion1.objects.filter(collection=col).count() > 1}
        selected_collections = [collections_dict[i] for i in get_selection(request, collections)]

        t = threading.Thread(target=combine_train, args=(selected_collections,))
        t.start()
        return HttpResponse("success")
