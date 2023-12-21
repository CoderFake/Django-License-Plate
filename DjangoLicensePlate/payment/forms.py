from django import forms
from datetime import datetime


class PaymentForm(forms.Form):
    license_plate = forms.CharField(max_length=50, required=False)
    order_id = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), max_length=250)
    amount = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), max_length=50)
    order_desc = forms.CharField(max_length=100)
    bank_code = forms.CharField(max_length=20, required=False)
    language = forms.CharField(max_length=2)

class SearchForm(forms.Form):
    license_plate = forms.CharField(max_length=50, required= False)
