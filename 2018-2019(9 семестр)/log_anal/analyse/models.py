from django.db import models
from django.contrib.postgres.fields import ArrayField

# Когда вводятся данные пользователей, таблицы URLs и Domains запуолняются только в полях url и domain соответсвенно.
# Типы и категории заполняются отдельно с помощью diffbot.com.
class URLs(models.Model):
    """
    Информация о каждом отдельно url. Информация о его типе и категории (пока что нету).
    """
    url = models.TextField(default="")
    type = models.TextField(db_index=True, default="")
    category = models.TextField(db_index=True, default="")


class Domains(models.Model):
    """
    Информация о каждом отдельно домене. Информация о его типе и категории.
    """
    domain = models.CharField(primary_key=True, default="", max_length=100)
    type = models.TextField(db_index=True, default="")
    category = models.TextField(db_index=True, default="")


class Clicks(models.Model):
    time = models.DateTimeField()   # время в полном формате (day + local_time)
    url = models.ForeignKey(URLs, db_index=True, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domains, db_index=True, on_delete=models.CASCADE)


class Log(models.Model):
    """
    Основной лог. В отличие от кликов, также содержит информацию о пользователе и сеансе. Удобен и используется для анализа.
    """
    day = models.DateTimeField(db_index=True)   # день календаря
    local_time = models.DateTimeField(default=None) # часы минуты секунды
    click = models.ForeignKey(Clicks, default=None, db_index=True, on_delete=models.CASCADE)

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

    click1 = models.ForeignKey(Clicks, db_index=True, default=None, on_delete=models.CASCADE, related_name='first_click_in_bi')
    click2 = models.ForeignKey(Clicks, db_index=True, default=None, on_delete=models.CASCADE, related_name='second_click_in_bi')


# триграммы
class Trigrams(models.Model):
    seance = models.IntegerField(db_index=True, default=-1)
    username = models.CharField(db_index=True, default="I", max_length=50)

    click1 = models.ForeignKey(Clicks, default=None, db_index=True, on_delete=models.CASCADE, related_name='first_click_in_tri')
    click2 = models.ForeignKey(Clicks, default=None, db_index=True, on_delete=models.CASCADE, related_name='second_click_in_tri')
    click3 = models.ForeignKey(Clicks, default=None, db_index=True, on_delete=models.CASCADE, related_name='third_click_in_tri')


# Важные личные признаки пользователей
class Teams(models.Model):
    """
    Пользователей делим на команды. Считаем количество кликов для обучающей выборки. Далее для каждого пользователя из
    команды считаем его индивидуальные особенности и фиксируем в таблице.
    """
    team = models.IntegerField(db_index=True)
    username = models.CharField(db_index=True, default="I", max_length=50)

    frequent_urls = ArrayField(models.TextField(default=""))
    frequent_domains = ArrayField(models.CharField(default="", max_length=100))
    frequent_domains_categories = ArrayField(models.TextField(default=""), default=list)

    frequent_bi_urls = ArrayField(ArrayField(models.TextField(default="")))
    frequent_tri_urls = ArrayField(ArrayField(models.TextField(default="")))
    frequent_bi_domains = ArrayField(ArrayField(models.CharField(default="", max_length=100)))
    frequent_tri_domains = ArrayField(ArrayField(models.CharField(default="", max_length=100)))

    frequent_bi_domains_type = ArrayField(ArrayField(models.TextField(default="")), default=list)
    frequent_bi_domains_categories = ArrayField(ArrayField(models.TextField(default="")), default=list)
    frequent_tri_domains_type = ArrayField(ArrayField(models.TextField(default="")), default=list)
    frequent_tri_domains_categories = ArrayField(ArrayField(models.TextField(default="")), default=list)

    thousand = models.IntegerField(db_index=True, default=0)    # количество тысяч кликов, использованных для анализа


class BaseCollections(models.Model):
    team = models.IntegerField(db_index=True)
    thousand = models.IntegerField(db_index=True, default=0)  # количество тысяч кликов, использованных для обучения
    users_quantity = models.IntegerField(db_index=True, default=0)
    number_parts_per_day = models.IntegerField(default=0)  # на сколько частей разделены сутки

class Collections(models.Model):
    team = models.IntegerField(db_index=True)
    thousand = models.IntegerField(db_index=True, default=0)  # количество тысяч кликов, использованных для обучения
    users_quantity = models.IntegerField(db_index=True, default=0)
    number_parts_per_day = models.IntegerField(default=0)  # на сколько частей разделены сутки
    clicks = models.IntegerField(default=0) # количество кликов в одном векторе

class VectorsOneVersion1(models.Model):
    """
    Вектора со всеми признаками. Впоследствии мы будем брать только часть этих признаков
    """
    collection = models.ForeignKey(Collections, default=None, db_index=True, on_delete=models.CASCADE)
    username = models.CharField(db_index=True, default="I", max_length=50)
    type = models.IntegerField(db_index=True, default=0)  # флаг, который говорит - обучающий вектор, или нет

    """
    Далее перечисляются признаки
    """
    days = ArrayField(models.IntegerField(default=0))   # активность по дням недели
    day_parts = ArrayField(models.IntegerField(default=0))  # активность по времени суток
    activity_time = ArrayField(models.IntegerField(default=0), default=list)  # совмещенная активность по дням недели и времени суток

    middle_pause = models.FloatField(default=0) # средняя пауза, среди пауз менее 5 мин
    middle_pause2 = models.FloatField(default=0)  # средняя пауза, среди пауза от 5 мин до 10 мин
    middle_pause3 = models.FloatField(default=0)  # средняя пауза, среди пауза от 10 мин
    quantity_middle_pause = models.IntegerField(default=0)
    quantity_middle_pause2 = models.IntegerField(default=0)
    quantity_middle_pause3 = models.IntegerField(default=0)

    start_comp_pause = models.FloatField(default=0)

    urls = ArrayField(models.IntegerField(default=0)) # количество переходов на частые url
    url_freq_pause = ArrayField(models.FloatField(default=0))
    url_maps = ArrayField(ArrayField(models.IntegerField(default=0)))

    domains = ArrayField(models.IntegerField(default=0))
    dom_freq_pause = ArrayField(models.FloatField(default=0))
    domain_maps = ArrayField(ArrayField(models.IntegerField(default=0)))

    url_bi = ArrayField(models.IntegerField(default=0))
    url_bi_pauses = ArrayField(models.FloatField(default=0))
    dom_bi = ArrayField(models.IntegerField(default=0))
    dom_bi_pauses = ArrayField(models.FloatField(default=0))
    url_tri = ArrayField(models.IntegerField(default=0))
    url_tri_pauses = ArrayField(models.FloatField(default=0))
    dom_tri = ArrayField(models.IntegerField(default=0))
    dom_tri_pauses = ArrayField(models.FloatField(default=0))

    domain_type = ArrayField(models.IntegerField(default=0))
    domain_categories = ArrayField(models.IntegerField(default=0))

    last_click = models.IntegerField(default=0) # для синхронизации тестирования пачек из нескольких кликов


class Patterns(models.Model):
    patterns = ArrayField(models.TextField(default=""))


# результаты МО на отельную команду
class ML(models.Model):
    collection = models.ForeignKey(Collections ,default=None, db_index=True, on_delete=models.CASCADE)
    accuracy = models.FloatField(default=0.0)
    patterns = ArrayField(models.TextField(default=""))
    middleFAR = models.FloatField(default=0.0)
    middleFRR = models.FloatField(default=0.0)
    algorithm = models.TextField(db_index=True, default="")

# результаты МО на отельную команду
class CombineMLs(models.Model):
    collection = models.ForeignKey(BaseCollections ,default=None, db_index=True, on_delete=models.CASCADE)
    accuracy = models.FloatField(default=0.0)
    patterns = ArrayField(models.TextField(default=""))
    middleFAR = models.FloatField(default=0.0)
    middleFRR = models.FloatField(default=0.0)
    algorithm = models.TextField(db_index=True, default="")