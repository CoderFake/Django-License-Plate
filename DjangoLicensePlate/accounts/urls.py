from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/comfirm/', views.confirm_view, name='confirm_reset'),
    path('logout/reset_password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
    path("not-found/", TemplateView.as_view(template_name="homepage/not_found.html"), name="not_found"),
]
