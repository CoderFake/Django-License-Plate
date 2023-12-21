from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponse, render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, ConfirmForm, CustomPasswordResetForm
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib import messages
import re

User = get_user_model()
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            username = username.strip()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main')
            else:
                messages.error(request, 'error:Sai tên đăng nhập hoặc mật khẩu!')
    else:
        form = LoginForm()
    user = request.user
    return render(request, "homepage/login.html", {'form': form, 'user': user})

def logout_view(request):
    logout(request)
    return redirect('index')

def confirm_view(request):
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            email = email.strip()
            pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            if not pattern.match(email):
                messages.error(request, 'error:Email không hợp lệ!')
            else:
                user = User.objects.filter(email=email).first()
                if user:
                    subject = 'Password Request'
                    email_template_name = "homepage/send_email.txt"
                    parameters = {
                        'user': user,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Parking Management Systems',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    mail = render_to_string(email_template_name, parameters)
                    try:
                        send_mail(subject, mail, '', [user.email], fail_silently=False)
                        hide_button_container = True
                        return render(request, 'homepage/confirm_reset.html', {'hide_button_container': hide_button_container})
                    except Exception as e:
                        messages.error(request, 'error:Có lỗi xảy ra khi gửi email: ' + str(e))
                else:
                    messages.error(request, 'error:Email không tồn tại!')
    else:
        form = ConfirmForm()
    return render(request, 'homepage/confirm_reset.html', {'form': form})


def is_strong_password(password, username):
    if len(password) < 8 and len(password) > 30:
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c.isupper() for c in password) or not any(c.islower() for c in password):
        return False
    if not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\\-]', password):
        return False
    common_words = ["password", "admin1234", "123456789", "12345678", username.lower()]
    if any(common_word in password.lower() for common_word in common_words):
        return False

    return True
def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    success_message = False
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomPasswordResetForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username'].strip()
                new_password = form.cleaned_data['new_password']
                confirm_new_password = form.cleaned_data['confirm_new_password']
                user_exists = User.objects.filter(username=username).exists()

                if user_exists:
                    if new_password != confirm_new_password:
                        messages.error(request, 'error:Mật khẩu không trùng khớp!')
                    elif is_strong_password(new_password, username):
                        user.set_password(new_password)
                        user.save()
                        success_message = True
                    else:
                        messages.error(request, 'error:Mật khẩu không hợp lệ!')
                else:
                    messages.error(request, 'error:Sai tên đăng nhập!')
        else:
            form = CustomPasswordResetForm()
        if success_message:
            messages.success(request, 'success:Đặt lại mật khẩu thành công!')
        return render(request, 'homepage/reset_pass.html', {'form': form, 'success_message': success_message, 'user': request.user})
    else:
        messages.error(request, 'error:Đường dẫn đặt lại mật khẩu không hợp lệ!')
        return redirect('login')
