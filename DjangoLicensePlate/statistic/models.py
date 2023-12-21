from django.db import models

class Statistic(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    total_payments = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_vehicles_in = models.IntegerField(default=0)
    total_vehicles_out = models.IntegerField(default=0)
    total_monthly_subscriptions = models.IntegerField(default=0)
    active_monthly_subscriptions = models.IntegerField(default=0)
