from django.db import models

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


# биграммы
class Bigrams(models.Model):
    seance = models.IntegerField(db_index=True, default=-1)
    username = models.CharField(db_index=True, default="I", max_length=50)

    time1 = models.DateTimeField()
    url1 = models.TextField(db_index=True, default="")
    domain1 = models.CharField(db_index=True, default="", max_length=100)
    time2 = models.DateTimeField()
    url2 = models.TextField(db_index=True, default="")
    domain2 = models.CharField(db_index=True, default="", max_length=100)


# триграммы
class Trigrams(models.Model):
    seance = models.IntegerField(db_index=True, default=-1)
    username = models.CharField(db_index=True, default="I", max_length=50)

    time1 = models.DateTimeField()
    url1 = models.TextField(db_index=True, default="")
    domain1 = models.CharField(db_index=True, default="", max_length=100)
    time2 = models.DateTimeField()
    url2 = models.TextField(db_index=True, default="")
    domain2 = models.CharField(db_index=True, default="", max_length=100)
    time3 = models.DateTimeField()
    url3 = models.TextField(db_index=True, default="")
    domain3 = models.CharField(db_index=True, default="", max_length=100)


class Vectors(models.Model):
    username = models.CharField(db_index=True, default="I", max_length=50)
    WeekDay = models.IntegerField(db_index=True, default=-1)    # [1,7]

    # в каждый день недели разделен на 8 частей, т.е. здесь будут стоять
    Time = models.IntegerField(db_index=True, default=-1)    # [1,8]

    # частые url пользователя - владельца
    url0 = models.IntegerField(default=0)
    url1 = models.IntegerField(default=0)
    url2 = models.IntegerField(default=0)
    url3 = models.IntegerField(default=0)
    url4 = models.IntegerField(default=0)
    url5 = models.IntegerField(default=0)
    url6 = models.IntegerField(default=0)
    url7 = models.IntegerField(default=0)
    url8 = models.IntegerField(default=0)
    url9 = models.IntegerField(default=0)
    url10 = models.IntegerField(default=0)
    url11 = models.IntegerField(default=0)
    url12 = models.IntegerField(default=0)
    url13 = models.IntegerField(default=0)
    url14 = models.IntegerField(default=0)
    url15 = models.IntegerField(default=0)
    url16 = models.IntegerField(default=0)
    url17 = models.IntegerField(default=0)
    url18 = models.IntegerField(default=0)
    url19 = models.IntegerField(default=0)

    # частые domains пользователя - владельца
    dom0 = models.IntegerField(default=0)
    dom1 = models.IntegerField(default=0)
    dom2 = models.IntegerField(default=0)
    dom3 = models.IntegerField(default=0)
    dom4 = models.IntegerField(default=0)
    dom5 = models.IntegerField(default=0)
    dom6 = models.IntegerField(default=0)
    dom7 = models.IntegerField(default=0)
    dom8 = models.IntegerField(default=0)
    dom9 = models.IntegerField(default=0)
    dom10 = models.IntegerField(default=0)
    dom11 = models.IntegerField(default=0)
    dom12 = models.IntegerField(default=0)
    dom13 = models.IntegerField(default=0)
    dom14 = models.IntegerField(default=0)
    dom15 = models.IntegerField(default=0)
    dom16 = models.IntegerField(default=0)
    dom17 = models.IntegerField(default=0)
    dom18 = models.IntegerField(default=0)
    dom19 = models.IntegerField(default=0)

    # сколько раз попал в карту кликов, если попал в частый домен или url
    #click = models.IntegerField(default=0)

    # если есть время включения, то отклонение от среднего
    start = models.IntegerField(default=0)
    deviation = models.FloatField(default=1.0)

    # биграммы
    bi0 = models.IntegerField(default=0)
    bi1 = models.IntegerField(default=0)
    bi2 = models.IntegerField(default=0)
    bi3 = models.IntegerField(default=0)
    bi4 = models.IntegerField(default=0)
    bi5 = models.IntegerField(default=0)
    bi6 = models.IntegerField(default=0)
    bi7 = models.IntegerField(default=0)
    bi8 = models.IntegerField(default=0)
    bi9 = models.IntegerField(default=0)
    bi10 = models.IntegerField(default=0)
    bi11 = models.IntegerField(default=0)
    bi12 = models.IntegerField(default=0)
    bi13 = models.IntegerField(default=0)
    bi14 = models.IntegerField(default=0)

    # триграммы
    tri0 = models.IntegerField(default=0)
    tri1 = models.IntegerField(default=0)
    tri2 = models.IntegerField(default=0)
    tri3 = models.IntegerField(default=0)
    tri4 = models.IntegerField(default=0)
    tri5 = models.IntegerField(default=0)
    tri6 = models.IntegerField(default=0)
    tri7 = models.IntegerField(default=0)
    tri8 = models.IntegerField(default=0)
    tri9 = models.IntegerField(default=0)







