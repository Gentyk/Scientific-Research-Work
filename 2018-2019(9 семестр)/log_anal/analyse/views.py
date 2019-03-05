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

from analyse.models import Bigrams, Log, Trigrams, Domains, Users
from base.new_analyse import base_analyse
from base.filling_the_database import fil


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
        analyse_usernames = [name[0] for name in Users.objects.all().values_list("username")]

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
                                 'dom_bi': 'dom_bi', 'url_tri': 'url_tri', 'dom_tri': 'dom_tri'})
        date = Users.objects.values()
        for i in date:
            context['teams'].append({
                't': i['team'],
                'u': i['username'],
                'url': len(i['frequent_urls']),
                'dom': len(i['frequent_domains']),
                'url_bi': len(i['frequent_bi_urls']),
                'dom_bi': len(i['frequent_bi_domains']),
                'url_tri': len(i['frequent_tri_urls']),
                'dom_tri': len(i['frequent_tri_domains'])
            })

        return render(request, 'analyse/users.html', context)

    def post(self, dop_info=None):
        Bigrams.objects.all().delete()
        Log.objects.all().delete()
        Trigrams.objects.all().delete()

        t = threading.Thread(target=fil)
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
            start_time = log.earliest('time').time
            data['users_table'].append({
                'name': name,
                'all': log.count(),
                '1': log.filter(time__lte= start_time + timedelta(days=7)).count(),
                '2': log.filter(time__lte=start_time + timedelta(days=14)).count(),
                '3': log.filter(time__lte=start_time + timedelta(days=21)).count(),
            })

        data['teams_table'].append({'team': 'team', 'user': 'user'})
        u_data = Users.objects.values('team', 'username')
        for i in u_data:
            data['teams_table'].append({'team': i['team'], 'user': i['username']})

        return render(request, 'analyse/users_analyse.html', data)

    def post(self, request):
        """
        Для каждого пользователя находит частые url и другие признаки. В результате заполняется таблица Users.
        """
        team = int(request.POST["team"])
        if Users.objects.filter(team=team):
            Users.objects.filter(team=team).delete()
        clicks_thousand = int(request.POST["clicks"])
        users = []
        for name in self.names:
            num = request.POST.get(name)
            if num:
                users.append(name)

        t = threading.Thread(target=base_analyse, args=(team, clicks_thousand, users,))
        t.start()
        return HttpResponse("success")









