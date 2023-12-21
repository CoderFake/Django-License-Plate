from django.db import models
from django.utils import timezone

class EditInfor(models.Model):
    rtsp_in = models.CharField(max_length=100, default="0", unique=True)
    rtsp_out = models.CharField(max_length=100, default="0", unique=True)
    rtsp_zone = models.CharField(max_length=100, default="0", unique=True)
    month_price = models.IntegerField(default=1000000)
    day_price1 = models.IntegerField(default=20000)
    day_price2 = models.IntegerField(default=30000)
    time_day1 = models.IntegerField(default=6)
    time_day2 = models.IntegerField(default=18)


