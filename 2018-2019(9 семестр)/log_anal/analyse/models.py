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

    thousand = models.IntegerField(db_index=True, default=0)    # номер тысячи

class ML(models.Model):
    team = models.IntegerField(db_index=True)
    clicks = models.IntegerField(default=0)
    num_users = models.IntegerField(default=0)
    patterns = ArrayField(models.TextField(default=""))
    middleFAR = models.FloatField(default=0.0)
    middleFRR = models.FloatField(default=0.0)
    accuracy = models.FloatField(default=0.0)