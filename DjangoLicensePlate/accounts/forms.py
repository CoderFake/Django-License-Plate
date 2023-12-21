from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '', 'class': 'input100'}), )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '', 'class': 'input100'}, render_value=False), )
class ConfirmForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ví dụ: name@example.com', 'class': 'input100'}), )
class CustomPasswordResetForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '', 'class': 'input100'}), )
    new_password = forms.CharField(label='New password', widget=forms.PasswordInput(render_value=False), )
    confirm_new_password = forms.CharField(label='Confirm new password',widget=forms.PasswordInput(render_value=False), )