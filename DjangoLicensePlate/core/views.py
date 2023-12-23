from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import render
from django.contrib.auth import get_user_model
from camera.views import scan_plate, parking_space, find_plate
from django.views.decorators.csrf import csrf_exempt
import json
from PIL import Image
import base64
from io import BytesIO
from camera.models import CarManagement
from datetime import timedelta, datetime
from django.db.models import Max


User = get_user_model()

def save_screen_size(request):
    if request.method == 'POST':
        width = request.POST.get('width')
        height = request.POST.get('height')
        if width < 1300 or height < 760:
            return False
        return True

@csrf_exempt
def gate(request):
    if request.method == 'POST':
        response_data = scan_plate(int(request.POST.get('gate')))
        return JsonResponse(json.loads(response_data))

@csrf_exempt
def find_infor(request):
    if request.method == 'POST':
        response_data = find_plate(request.POST.get('licenseplate'))
        return JsonResponse(json.loads(response_data))

@csrf_exempt
def current_parked(request):
    if request.method == 'POST':
        response_data = parking_space()
        return JsonResponse(json.loads(response_data))
@csrf_exempt
def SaveData(request):
    if request.method == 'POST':
        gate = request.POST.get('gate')
        licenseplate = request.POST.get('licenseplate')
        img_file = request.FILES.get('image')
        img_binary = img_file.read() if img_file else None
        if gate == '0':
            time_in = request.POST.get('time_in')
            if time_in != 'undefined':
                time_in = datetime.strptime(time_in, "%Y-%m-%d %H:%M:%S")
            CarManagement.objects.create(
                license_plate=licenseplate.split(":")[1].strip(),
                time_in=time_in + timedelta(hours=7),
                time_out=None,
                plate_img=img_binary,
            )
        else:
            time_out = request.POST.get('time_out')
            if time_out != 'undefined':
                time_out = datetime.strptime(time_out, "%Y-%m-%d %H:%M:%S")
            print(f"{licenseplate} {time_out} {img_binary}")
            car_instance = CarManagement.objects.filter(license_plate=licenseplate.split(":")[1].strip()).order_by('-time_in').first()
            if car_instance is not None:
                car_instance.time_out = time_out + timedelta(hours=7)
                car_instance.save()

        return HttpResponse("success: Đã lưu vào cơ sở dữ liệu!")
    return HttpResponse("Invalid request")

class HomeView(View):
    def get(self, request):
        if not self.request.user.is_authenticated:
            return render(request, "homepage/index.html")
        else:
            return render(request, "homepage/main.html")
        return render(request, "homepage/index.html")


class MainControl(View):
    def get(self, request):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return render(request, "homepage/main.html")



    # os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
    # cap = cv2.VideoCapture(rtsp_url)
    # while True:
    #     success, frame = cap.read()
    #     if not success:
    #         print("Error: failed to capture image")
    #         break
    #     ret, buffer = cv2.imencode(".jpg", frame)
    #     if not ret:
    #         continue
    #     yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
