from django.db import models


class Log(models.Model):
    day = models.DateTimeField(db_index=True)
    local_time = models.DateTimeField(default=None)
    time = models.DateTimeField()
    url = models.TextField(default="")
    domain = models.CharField(db_index=True, default="", max_length=100)
    window_coordinates = models.CharField(default="", max_length=30)
    cursor_coordinates = models.CharField(default="", max_length=20)
    start_computer = models.BooleanField(db_index=True, default=False)
    seance = models.IntegerField(db_index=True)
    username = models.CharField(db_index=True, default="I", max_length=50)


class Easy(models.Model):
    time = models.DateTimeField()
    url = models.TextField(default="")


