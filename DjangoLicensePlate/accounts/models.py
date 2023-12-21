from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

@receiver(pre_save, sender=User)
def prevent_editing_of_admin(sender, instance, **kwargs):
    if instance.username == 'admin2202':
        raise Exception("Không thể chỉnh sửa thông tin của tài khoản admin2202.")