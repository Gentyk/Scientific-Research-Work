from django.db import models


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


class Easy(models.Model):
    time = models.DateTimeField()
    url = models.TextField(default="")


