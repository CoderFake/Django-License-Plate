from django.urls import path
from payment import views

urlpatterns = [
    path('payment/', views.payment, name='payment'),
    path('payment_ipn/', views.payment_ipn, name='payment_ipn'),
    path('payment/payment_return/', views.payment_return, name='payment_return'),
    path('expired/', views.expired, name='expired'),
]