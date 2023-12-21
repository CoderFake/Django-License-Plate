from django.db import models
class BuyMonthTicket(models.Model):
    order_id = models.CharField(max_length=50, primary_key=True)
    license_plate = models.CharField(max_length=15)
    time_buy = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vehicle_type = models.CharField(max_length=50)
    expired = models.DateTimeField()
