from django.urls import path
from settings import views
urlpatterns = [
    path('settings/infor/', views.setting_info, name='setting_info'),
    path('settings/', views.setting_info, name='setting_info'),
    path('settings/camera/', views.camera, name='camera'),
    path('settings/payment/', views.payment, name='payment_setting'),
    path('check_connection/', views.check_connection, name='check_connection'),
]