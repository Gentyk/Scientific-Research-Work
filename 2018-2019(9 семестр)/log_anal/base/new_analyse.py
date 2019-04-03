import time
import datetime

from analyse.models import Bigrams, Log, Trigrams, Teams
from base.analys import Analyst


def base_analyse(team, clicks_thousand, users):
    """
    Запуск анализа в случае, когда у всех пользователей одинаковый размер обучающей выборки
    :param team: целое число - номер команды
    :param clicks_thousand: количество тысяч кликов
    :param users: list, в котором перечислены имена пользователей
    """
    start_time = time.time()
    for name in users:
        print('start ' + name)
        log = Log.objects.filter(username=name)
        u_log = log.filter(thousand__lt=clicks_thousand)
        finish_time = u_log.latest('click__time').click.time

        bi_log = Bigrams.objects.filter(username=name).filter(click1__time__lt=finish_time).filter(click2__time__lt=finish_time)
        tri_log = Trigrams.objects.filter(username=name).filter(click2__time__lt=finish_time).filter(click3__time__lt=finish_time)

        a = Analyst(u_log, bi_log, tri_log, name, finish_time)
        a.activity_analyse()
        Teams.objects.create(
            username=name,
            team=team,

            frequent_urls=a.result['частые url'],
            frequent_domains=a.result['частые домены'],

            frequent_bi_urls=a.result['url биграммы'],
            frequent_tri_urls=a.result['url триграммы'],
            frequent_bi_domains=a.result['domain биграммы'],
            frequent_tri_domains=a.result['domain триграммы'],

            frequent_bi_domains_type=a.result['type биграммы'],
            frequent_bi_domains_categories=a.result['category биграммы'],
            frequent_tri_domains_type=a.result['type триграммы'],
            frequent_tri_domains_categories = a.result['category триграммы'],

            thousand=clicks_thousand,
        )
        print('end ' + name)
    msg = "Анализ выполнен за время: %s seconds ---" % (
    time.time() - start_time)
    print(msg)

def base_analyse2(team, weeks, users):
    """
    Запуск анализа в случае, когда у всех пользователей период обучающий выбоки одинаков, но оп количеству кликов - разный
    :param team: целое число - номер команды
    :param clicks_thousand: количество недель, из которых мы берем данные для обучения
    :param users: list, в котором перечислены имена пользователей
    """

    start_time = time.time()

    # определим количество кликов (максимальное от всех)
    #clicks = [Log.objects.filter(username=name).filter(click__time__lt=Log.objects.filter(username=name).earliest('click__time').click.time + datetime.timedelta(days=7*weeks)).count() for name in users]
    #clicks_thousand = (sum(clicks)/len(clicks)) // 1000

    for name in users:
        print('start ' + name)
        log = Log.objects.filter(username=name)
        finish = log.earliest('click__time').click.time + datetime.timedelta(days=7*weeks)
        u_log = log.filter(click__time__lt=finish)
        clicks_thousand = (2 if u_log.count() // 1000 == 1 else u_log.count() // 1000)
        finish_time = u_log.latest('click__time').click.time

        bi_log = Bigrams.objects.filter(username=name).filter(click1__time__lt=finish_time).filter(click2__time__lt=finish_time)
        tri_log = Trigrams.objects.filter(username=name).filter(click2__time__lt=finish_time).filter(click3__time__lt=finish_time)

        a = Analyst(u_log, bi_log, tri_log, name, finish_time)
        a.activity_analyse()
        Teams.objects.create(
            username=name,
            team=team,

            frequent_urls=a.result['частые url'],
            frequent_domains=a.result['частые домены'],

            frequent_bi_urls=a.result['url биграммы'],
            frequent_tri_urls=a.result['url триграммы'],
            frequent_bi_domains=a.result['domain биграммы'],
            frequent_tri_domains=a.result['domain триграммы'],

            frequent_bi_domains_type=a.result['type биграммы'],
            frequent_bi_domains_categories=a.result['category биграммы'],
            frequent_tri_domains_type=a.result['type триграммы'],
            frequent_tri_domains_categories = a.result['category триграммы'],

            thousand=clicks_thousand,
        )
        print('end ' + name)
    msg = "Анализ выполнен за время: %s seconds ---" % (
    time.time() - start_time)
    print(msg)