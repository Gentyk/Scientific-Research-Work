# Просматривает таюлицу Лога и заполняет таблицу жанров
import time
import re

from analyse.models import Bigrams, Log, Trigrams, URLs, Domains
from diffbot.client import DiffbotClient

def url_genre():
    urls = [i[0] for i in Log.objects.values('url').distinct().values_list('url')]
    print(len(urls))
    diffbot = DiffbotClient()
    token = 'a8e38e1dccdb5784147317bfd5119c1d'#'18aa09158e10b70ac108c941f060c99a'
    i = 0
    for url in urls:
        i += 1
        if i % 1000 == 999:
            print(i)
        try:
            u = URLs.objects.get(url=url)
        except:
            api = "product"
            j = 0
            while j < 2:
                try:
                    response = diffbot.request(url, token, api)
                    break
                except:
                    time.sleep(5)
                    j += 1
            if j == 5:
                print("error")
                ff = input()

            try:
                category = response['objects'][0]['category']
            except:
                category = "not determined"

            api = "analyze"
            j = 0
            while j < 5:
                try:
                    response = diffbot.request(url, token, api)
                    break
                except:
                    time.sleep(5)
                    j += 1
            if j == 5:
                print("error")
                ff = input()
            try:
                type = response['type']
            except:

                type = "not determined"
            URLs.objects.create(
                url=url,
                type=type,
                category=category,
            )


def domain_genre():
    domains = [(i[1], i[0][:(i[0].find(i[1]) + len(i[1]))]) for i in Log.objects.distinct('click__domain__domain').values_list('click__url__url', 'click__domain__domain')]
    print(len(domains))
    diffbot = DiffbotClient()
    token = '9d5a6ddb2521d8b21c2fa27c4a2db715'
    i = 0
    prefix = ["https://", "http://"]
    for domain, url in domains:
        i += 1
        if i % 1000 == 999:
            print(i)

        # если у нас есть домены в Log? но их нету в Domains
        #try:
        #    dom = Domains.objects.get(domain=domain)
        #except:
        if Domains.objects.get(domain=domain).type == '':
            api = "product"
            j = 0
            while j < 2:
                try:
                    response = diffbot.request(url, token, api)
                    break
                except:
                    time.sleep(5)
                    j += 1
            if j == 2:
                print("error")
                response = None


            try:
                category = response['objects'][0]['category']
            except:
                category = "not determined"

            api = "analyze"
            j = 0
            while j < 2:
                try:
                    response = diffbot.request(url, token, api)
                    break
                except:
                    time.sleep(5)
                    j += 1
            if j == 2:
                print("error")
                response = None
            try:
                if response:
                    type = response['type']
                else:
                    type = "page error"
            except:
                if re.match(r'(http|https|ftp):\/\/', url):
                    type = "not determined"
                else:
                    for pref in prefix:
                        try:
                            new_url = pref + url
                            response = diffbot.request(new_url, token, api)
                            type = response['type']
                            break
                        except:
                            type = "not determined"
                if type == "not determined":
                    print(url)
                    print(domain)
                    print(response)

            # если необходимо добавить домен, то
            # Domains.objects.create(
            #     domain=domain,
            #     type=type,
            #     category=category,
            # )

            # доподняем информацию о домене
            d = Domains.objects.get(
                domain=domain)
            d.type=type
            d.category=category
            d.save()

domain_genre()