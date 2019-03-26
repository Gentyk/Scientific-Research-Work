# Просматривает таюлицу Лога и заполняет таблицу жанров

from analyse.models import Bigrams, Log, Trigrams, URLs
from diffbot.client import DiffbotClient

urls = Log.objects.values('url').distinct().values_list('url')
print(urls)
diffbot = DiffbotClient()
token = '18aa09158e10b70ac108c941f060c99a'
for i, url in urls.items():
    try:
        u = URLInfo.objects.get(url=url)
    except:
        api = "product"
        response = diffbot.request(url, token, api)
        try:
            category = response['objects'][0]['category']
        except:
            category = ""

        api = "analyze"
        response = diffbot.request(url, token, api)
        type = response['type']
        URLInfo.objects.create(
            url=url,
            type=type,
            category=category,
        )