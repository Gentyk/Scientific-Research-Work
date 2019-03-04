from datetime import datetime, timedelta
from pytz import timezone
from os import listdir
from os.path import isfile, join
import time
import re
import threading

from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse
from django.views import generic

from analyse.models import Bigrams, Log, Trigrams, Domains, Users
from base.analys import check_logfile
from base.filling_the_database import Filling


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
        base_users = Users.objects.all()
        base_usernames = [name[0] for name in base_users.values_list("username")]
        if set(base_usernames) != set(log_names):
            names = list(set(log_names + base_usernames))

        # далее для каждого пользователя собираем инфомацию
        result = [{'name': 'name', 'file':'file availability',  'db':'in database', 'analyse': 'analyse'}]
        for name in names:
            local = {'name': name}
            local['file'] = ("+" if name in log_names else "-")
            #local['file'] = (check_logfile(name) if name in log_names else '-')
            local['db'] = ('+' if Log.objects.filter(username=name).count() > 1 else "-")
            local['analyse'] = ("+" if name in base_usernames else "-")
            result.append(local.copy())

        context = {'log_names_list': result}
        return render(request, 'analyse/users.html', context)

    def post(self, dop_info=None):
        Bigrams.objects.all().delete()
        Log.objects.all().delete()
        Trigrams.objects.all().delete()

        log_names = [f.split('.')[0] for f in listdir('logs') if isfile(join('logs', f))]
        for name in log_names:
            t = threading.Thread(target=Filling, args=(name,))
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
    def post(self, add_info=None):
        pass

