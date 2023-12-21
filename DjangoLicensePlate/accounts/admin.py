from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import *
#
# class CustomUserAdmin(BaseUserAdmin):
#
#     def has_delete_permission(self, request, obj=None):
#         if request.user.username == "admin2202":
#             return True
#         elif obj is not None and obj.username == 'admin2202':
#             return False
#         return True
#
#     def has_change_permission(self, request, obj=None):
#         if request.user.username == "admin2202":
#             return True
#         elif obj is not None and obj.username == 'admin2202':
#             return False
#         return True

admin.site.register(CustomUser)