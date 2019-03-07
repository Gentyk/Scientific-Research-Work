from django.db import models
from django.contrib.postgres.fields import ArrayField

# основной лог, с которым будут проводится действия
class Log(models.Model):
    day = models.DateTimeField(db_index=True)   # день календаря
    local_time = models.DateTimeField(default=None) # часы минуты секунды
    time = models.DateTimeField()   # время в полном формате (day + local_time)
    url = models.TextField(db_index=True, default="")
    domain = models.CharField(db_index=True, default="", max_length=100)

    x_cursor_coordinates = models.IntegerField(default=0)
    y_cursor_coordinates = models.IntegerField(default=0)
    x1_window_coordinates = models.IntegerField(default=0)
    y1_window_coordinates = models.IntegerField(default=0)
    x2_window_coordinates = models.IntegerField(default=0)
    y2_window_coordinates = models.IntegerField(default=0)

    start_computer = models.BooleanField(db_index=True, default=False)
    seance = models.IntegerField(db_index=True)
    username = models.CharField(db_index=True, default="I", max_length=50)

    thousand = models.IntegerField(db_index=True, default=0)    # номер тысячи - для ускорения анализа


# биграммы
class Bigrams(models.Model):
    seance = models.IntegerField(db_index=True, default=-1)
    username = models.CharField(db_index=True, default="I", max_length=50)

    time1 = models.DateTimeField()
    url1 = models.TextField(db_index=True, default="")
    domain1 = models.CharField(db_index=True, default="", max_length=100)
    type1 = models.TextField(db_index=True, default="")
    category1 = models.TextField(db_index=True, default="")
    time2 = models.DateTimeField()
    url2 = models.TextField(db_index=True, default="")
    domain2 = models.CharField(db_index=True, default="", max_length=100)
    type2 = models.TextField(db_index=True, default="")
    category2 = models.TextField(db_index=True, default="")


# триграммы
class Trigrams(models.Model):
    seance = models.IntegerField(db_index=True, default=-1)
    username = models.CharField(db_index=True, default="I", max_length=50)

    time1 = models.DateTimeField()
    url1 = models.TextField(db_index=True, default="")
    domain1 = models.CharField(db_index=True, default="", max_length=100)
    type1 = models.TextField(db_index=True, default="")
    category1 = models.TextField(db_index=True, default="")
    time2 = models.DateTimeField()
    url2 = models.TextField(db_index=True, default="")
    domain2 = models.CharField(db_index=True, default="", max_length=100)
    type2 = models.TextField(db_index=True, default="")
    category2 = models.TextField(db_index=True, default="")
    time3 = models.DateTimeField()
    url3 = models.TextField(db_index=True, default="")
    domain3 = models.CharField(db_index=True, default="", max_length=100)
    type3 = models.TextField(db_index=True, default="")
    category3 = models.TextField(db_index=True, default="")

# Типы и жанры урлов
class URLs(models.Model):
    """
    Типы:
    - article,
    - discussion,
    - image,
    - product,
    - video,
    - other.

    Жанры - 21 штука(https://www.diffbot.com/dev/docs/product/categories/) + если никакая категория

    Данная таблица только дополняется в случае отсутствия урлов в таблице,а не перезаписывается каждый раз
    """
    url = models.TextField(default="")
    type = models.TextField(db_index=True, default="")
    category = models.TextField(db_index=True, default="")

# Важные личные признаки пользователей
class Users(models.Model):
    username = models.CharField(db_index=True, default="I", max_length=50)
    team = models.IntegerField(db_index=True)
    frequent_urls = ArrayField(models.TextField(default=""))
    frequent_bi_urls = ArrayField(ArrayField(models.TextField(default="")))
    frequent_tri_urls = ArrayField(ArrayField(models.TextField(default="")))
    frequent_domains = ArrayField(models.TextField(default=""))
    frequent_bi_domains = ArrayField(ArrayField(models.TextField(default="")))
    frequent_tri_domains = ArrayField(ArrayField(models.TextField(default="")))
    thousand = models.IntegerField(db_index=True, default=0)    # номер тысячи

# Типы и жанры урлов
class Domains(models.Model):
    domain = models.CharField(default="", max_length=100)
    type = models.TextField(db_index=True, default="")
    category = models.TextField(db_index=True, default="")


class ML(models.Model):
    team = models.IntegerField(db_index=True)
    clicks = models.IntegerField(default=0)
    num_users = models.IntegerField(default=0)
    patterns = ArrayField(models.TextField(default=""))
    middleFAR = models.FloatField(default=0.0)
    middleFRR = models.FloatField(default=0.0)
    accuracy = models.FloatField(default=0.0)










