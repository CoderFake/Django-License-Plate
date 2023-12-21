from django import forms

class SettingFormInfor(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False, max_length=30)
    new_password = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False, max_length=30)
    confirm_password = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False, max_length=30)
    first_name = forms.CharField(required=False, max_length=30)
    last_name = forms.CharField(required=False, max_length=30)
    email = forms.CharField(required=False, max_length=100)
    phone = forms.CharField(required=False, max_length=20)
    address = forms.CharField(required=False, max_length=200)

class SettingFormCamera(forms.Form):
    rtsp_in = forms.CharField(required=False, max_length=100)
    rtsp_out = forms.CharField(required=False, max_length=100)
    rtsp_zone = forms.CharField(required=False, max_length=100)

class SettingFormPayment(forms.Form):
    month_price = forms.IntegerField(required=False)
    day_price1 = forms.IntegerField(required=False)
    day_price2 = forms.IntegerField(required=False)
    time_day1 = forms.IntegerField(required=False)
    time_day2 = forms.IntegerField(required=False)


