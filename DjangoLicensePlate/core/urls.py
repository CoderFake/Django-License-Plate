from django.urls import path
from .views import HomeView, MainControl
from django.views.generic import TemplateView
from . import views
urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("main/", MainControl.as_view(), name="main"),
    path("gate/", views.gate, name="gate"),
    path("current_parked/", views.current_parked, name="current_parked"),
    path("find_infor/", views.find_infor, name="find_infor"),
    path('savedata/', views.SaveData, name='savedata'),
    path("not-found/", TemplateView.as_view(template_name="homepage/not_found.html"), name="not_found"),
]
