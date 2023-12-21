from django.db import models

class CarManagement(models.Model):
    license_plate = models.CharField(max_length=15)
    time_in = models.DateTimeField(null=True)
    time_out = models.DateTimeField(null=True)
    plate_img = models.BinaryField(null=True)
