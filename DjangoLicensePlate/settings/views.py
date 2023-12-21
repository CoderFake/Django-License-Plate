from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.http import HttpResponse
from settings.models import EditInfor
from payment.models import BuyMonthTicket as Bt
from .forms import SettingFormInfor, SettingFormCamera, SettingFormPayment
from camera.views import check_camera_ping
from django.http import HttpResponse
import cv2
import re

User = get_user_model()


def check_connection(request):
    rtsp_url = request.POST.get('rtsp_url')
    if check_camera_ping(rtsp_url):
        return HttpResponse("success")
    return HttpResponse("false")
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


@login_required
def setting_info(request):
    username = request.user.username
    user = User.objects.filter(username=username).first()
    mess = []
    context = {
        'user': username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone': user.phone,
        'address': user.address,
        'messages': mess,
    }
    if request.method == 'POST':
        form = SettingFormInfor(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['password']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            email = form.cleaned_data['email'].strip()
            phone = form.cleaned_data['phone'].strip()
            first_name = form.cleaned_data['first_name'].strip()
            last_name = form.cleaned_data['last_name'].strip()
            address = form.cleaned_data['address'].strip()
            pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            status = 1
            if user:
                if old_password and new_password and confirm_password:
                    if authenticate(request, username=username,
                                    password=old_password) is None or confirm_password != new_password:
                        status = 0
                        if authenticate(request, username=username, password=old_password) is None:
                            mess.append("Mật khẩu cũ không chính xác!")
                        if confirm_password != new_password:
                            mess.append("Mật khẩu không trùng khớp!")
                    elif authenticate(request, username=username, password=new_password) is not None:
                        status = 0
                        mess.append("Mật khẩu mới trùng mật khẩu cũ!")
                    else:
                        if is_strong_password(new_password, username):
                            user.set_password(new_password)
                elif old_password and (not new_password or not confirm_password):
                    status = 0
                    mess.append("Bạn chưa nhập mật khẩu mới!")
                if not email or not pattern.match(email):
                    status = 0
                    mess.append('Email không hợp lệ!')
                elif email != user.email:
                    user.email = email

                pattern = r'^0(2\d|3[2-9]|5[6-8]|7[0-9]|8[6-8]|9[0-9])[0-9]{7}$'
                if not re.match(pattern, phone) or not first_name or not last_name or not address:
                    status = 0
                    if not re.match(pattern, phone):
                        mess.append('Định dạng số điện thoại không hợp lệ!')
                    if not first_name or not last_name or not address:
                        mess.append('Thông tin cá nhân không được để trống!')
                elif phone != user.phone or first_name != user.first_name or last_name != user.last_name or address != user.address:
                    user.phone = phone
                    user.first_name = first_name
                    user.last_name = last_name
                    user.address = address
                if status == 0:
                    context = {
                        'user': username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'phone': user.phone,
                        'address': user.address,
                        'messages': mess,
                    }
                    return render(request, "homepage/settings.html", context)
                    mess.clear()
                user.save()
                mess.append("1")
                context = {
                    'user': username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone': user.phone,
                    'address': user.address,
                    'messages': mess,
                }
    return render(request, "homepage/settings.html", context)


@login_required()
def camera(request):
    username = request.user.username
    user = User.objects.filter(username=username).first()
    first_record = EditInfor.objects.filter(id=1).first()
    first_rtsp_in = first_record.rtsp_in
    first_rtsp_out = first_record.rtsp_out
    first_rtsp_zone = first_record.rtsp_zone
    mess = []
    context = {
        'user': username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'messages': mess,
        'rtsp_in': first_rtsp_in,
        'rtsp_out': first_rtsp_out,
        'rtsp_zone': first_rtsp_zone,
    }
    if request.method == 'POST':
        form = SettingFormCamera(request.POST)
        if form.is_valid():
            cam_in = form.cleaned_data['rtsp_in'].strip()
            cam_out = form.cleaned_data['rtsp_out'].strip()
            cam_zone = form.cleaned_data['rtsp_zone'].strip()
            if not cam_in or not cam_out or not cam_zone:
                mess.append('Không được để trống rtsp!')
                context['mess'] = mess
                return render(request, "homepage/cameras_setting.html", context)
            elif cam_in != first_rtsp_in or cam_out != first_rtsp_out or cam_zone != first_rtsp_zone:
                if check_camera_ping(cam_in):
                    first_record.rtsp_in = cam_in
                if check_camera_ping(cam_out):
                    first_record.rtsp_out = cam_out
                if check_camera_ping(cam_zone):
                    first_record.rtsp_zone = cam_zone
            mess.append("1")
            first_record.save()
            context = {
                'user': username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'messages': mess,
                'rtsp_in': first_record.rtsp_in,
                'rtsp_out': first_record.rtsp_out,
                'rtsp_zone': first_record.rtsp_zone,
            }
    return render(request, "homepage/cameras_setting.html", context)

def payment(request):
    username = request.user.username
    user = User.objects.filter(username=username).first()
    first_record = EditInfor.objects.filter(id=1).first()
    month_price = first_record.month_price
    day_price1 = first_record.day_price1
    day_price2 = first_record.day_price2
    time_day1 = first_record.time_day1
    time_day2 = first_record.time_day2
    mess = []
    context = {
        'user': username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'messages': mess,
        'month_price': month_price,
        'day_price1': day_price1,
        'day_price2': day_price2,
        'time_day1': time_day1,
        'time_day2': time_day2,
    }
    if request.method == 'POST':
        form = SettingFormPayment(request.POST)
        if form.is_valid():
            m_price = form.cleaned_data['month_price']
            d_price1 = form.cleaned_data['day_price1']
            d_price2 = form.cleaned_data['day_price2']
            am = form.cleaned_data['time_day1']
            pm = form.cleaned_data['time_day2']
            if not m_price or not d_price1 or not d_price2:
                mess.append("Không được để trống giá tiền!")
                context['mess'] = mess
                return render(request, "homepage/payment_setting.html", context)
            elif m_price and d_price1 and d_price2:
                first_record.month_price = m_price
                first_record.day_price1 = d_price1
                first_record.day_price2 = d_price2
            if am and pm:
                first_record.time_day1 = am
                first_record.time_day2 = pm
            mess.append("1")
            first_record.save()
            context = {
                'user': username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'messages': mess,
                'month_price': first_record.month_price,
                'day_price1': first_record.day_price1,
                'day_price2': first_record.day_price2,
                'time_day1': first_record.time_day1,
                'time_day2': first_record.time_day2,
            }
            return render(request, "homepage/payment_setting.html", context)
    return render(request, "homepage/payment_setting.html", context)