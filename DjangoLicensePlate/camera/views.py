import cv2
import math
import base64
import json
from PIL import Image
import numpy as np
import torch
from ultralytics import YOLO
from collections import Counter
import os
from datetime import timedelta, datetime
from django.utils import timezone
from settings.models import EditInfor
from payment.models import BuyMonthTicket
from django.conf import settings
from .models import CarManagement
from django.db.models import Max

plate_model_path = os.path.join(settings.BASE_DIR, 'static', 'model', 'plate.pt')
ocr_model_path = os.path.join(settings.BASE_DIR, 'static', 'model', 'ocr.pt')

Lp_detect = YOLO(plate_model_path)
OCR_detect = YOLO(ocr_model_path)

frames = []
best_plate = []

def pay_day_ticket(time_in, time_out):

    if isinstance(time_in, str):
        time_in = datetime.strptime(time_in, "%Y-%m-%d %H:%M:%S")
    if isinstance(time_out, str):
        time_out = datetime.strptime(time_out, "%Y-%m-%d %H:%M:%S")
    if time_in is None or time_out is None:
        raise ValueError("time_in và time_out không được phép là None")

    first_record = EditInfor.objects.filter(id=1).first()
    time_difference = (time_out - time_in).total_seconds() / 3600
    if int(time_difference) < 24:
        if first_record.time_day1 <= time_out.hour < first_record.time_day2:
            return first_record.day_price1
        else:
            return first_record.day_price2
    elif int(time_difference) == 24:
        return first_record.day_price1 + first_record.day_price2
    else:
        if first_record.time_day1 <= time_in.hour + (time_difference % 24) < first_record.time_day2:
            return int(time_difference / 24) * (first_record.day_price1 + first_record.day_price2) + first_record.day_price1
        else:
            return int(time_difference /24) * (first_record.day_price1 + first_record.day_price2)
def expired(license_plate):
    tickets = BuyMonthTicket.objects.filter(license_plate=license_plate).order_by('-time_buy')
    if tickets.exists():
        if tickets.first().expired + timedelta(hours=7) < timezone.now():
            return False
        else:
            return True
    return False

def distance_from_origin(x, y):
    distance = math.sqrt(x**2 + y**2)
    return distance

def process_frames(RTSP_URL):
    cap = cv2.VideoCapture(RTSP_URL)
    # os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
    # cap = cv2.VideoCapture(0)
    for i in range(0, 5):
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc khung hình từ luồng RTSP.")
            break
        frames.append(frame)

def scan_plate(gate):
    first_record = EditInfor.objects.filter(id=1).first()
    RTSP_URL = first_record.rtsp_in
    if gate:
        RTSP_URL = first_record.rtsp_out
    last_frame = None
    last_crop_img = None
    process_frames(RTSP_URL)
    for i, img in zip(range(0, 5), frames):
        # img = cv2.resize(img, (640, 640), interpolation=cv2.INTER_AREA)
        # img = img[320:960, 640: 1280]
        height, width, channels = img.shape
        center_x = width // 2
        center_y = height // 2
        img = img[int(center_y - 320):int(center_y + 320), int(center_x - 320):int(center_x + 320)]
        plates = Lp_detect(img)
        if plates:
            for r in plates:
                if len(r.boxes.xywh) > 0:
                    x, y, w, h = r.boxes.xywh[0]
                # scale_x = 1920 / 640
                # scale_y = 1080 / 640
                # new_x = x * scale_x
                # new_y = y * scale_y
                # new_w = w * scale_x
                # new_h = h * scale_y
                # crop_img = frames[i][int(new_y - new_h / 2):int(new_y + new_h / 2), int(new_x - new_w / 2):int(new_x + new_w / 2)]
                    crop_img = img[int(y - h / 2):int(y + h / 2), int(x - w / 2):int(x + w / 2)]
                    last_frame = img
                    last_crop_img = crop_img
                    if w > h:
                        ocrplates = OCR_detect(crop_img)
                        arr_plates = []
                        y_arr = []
                        if ocrplates:
                            for ocrplate in ocrplates:
                                pos = torch.tensor(ocrplate.boxes.xywh).numpy()[:, 0:2]
                                for c, row in zip(ocrplate.boxes.cls, pos):
                                    arr_plates.append([row[0], row[1], ocrplate.names[int(c)]])
                                    y_arr.append(row[1])
                            if len(y_arr) > 0:
                                y_min = min(y_arr)
                                y_max = max(y_arr)
                            else:
                                pass
                            license_plate = ""
                            if y_max / y_min > 1.8:
                                dis1 = []
                                dis2 = []
                                for row in arr_plates:
                                    if abs(y_min - row[1]) < abs(y_max - row[1]):
                                        dis1.append([int(distance_from_origin(row[0], row[1])), row[2]])
                                    else:
                                        dis2.append([int(distance_from_origin(row[0], row[1])), row[2]])
                                sorted_dis1 = sorted(dis1, key=lambda x: x[0])
                                sorted_dis2 = sorted(dis2, key=lambda x: x[0])
                                for item in sorted_dis1:
                                    license_plate += str(item[1])
                                for item in sorted_dis2:
                                    license_plate += str(item[1])
                            else:
                                dis = []
                                for row in arr_plates:
                                    dis.append([int(distance_from_origin(row[0], row[1])), row[2]])
                                sorted_dis = sorted(dis, key=lambda x: x[0])
                                for item in sorted_dis:
                                    license_plate += str(item[1])
                            best_plate.append(license_plate)
                            arr_plates.clear()
                            y_arr.clear()
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    if len(frames) > 0:
        _, buffer = cv2.imencode('.jpg', last_frame)
        last_frame_str = base64.b64encode(buffer).decode('utf-8')

    if last_crop_img is not None:
        _, buffer = cv2.imencode('.jpg', last_crop_img)
        last_crop_img_str = base64.b64encode(buffer).decode('utf-8')

    frames.clear()
    if len(best_plate) > 0:
        most_plate, count = Counter(best_plate).most_common(1)[0]
        best_plate.clear()
        time_in = (timezone.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
        if gate:
            print(most_plate)
            car_instance = CarManagement.objects.filter(license_plate=most_plate).order_by('-time_in').first()
            time_out = (timezone.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
            latest_time_in = None
            if car_instance is not None:
                latest_time_in = car_instance.time_in.strftime("%Y-%m-%d %H:%M:%S")
            if expired(most_plate):
                price = 0
            else:
                price = pay_day_ticket(latest_time_in, time_out)
            return json.dumps({
                'last_frame': last_frame_str,
                'last_crop_img': last_crop_img_str,
                'last_time_in': str(latest_time_in),
                'last_time_out': str(time_out),
                'price': price,
                'most_plate': most_plate
            })
        return json.dumps({
            'last_frame': last_frame_str,
            'last_crop_img': last_crop_img_str,
            'last_time_in': str(time_in),
            'last_time_out': "",
            'price': "",
            'most_plate': most_plate
        })

# def count_parked_cars_today():
#     today = timezone.now().date() + timedelta(hours=7)
#     parked_cars_count = CarManagement.objects.filter(
#         time_in__date__gte=today,
#         time_out__isnull=True
#     ).count()
#     return parked_cars_count if parked_cars_count is not None else 0
#
# def count_parked_cars_in_today():
#     today = timezone.now().date() + timedelta(hours=7)
#     parked_cars_count = CarManagement.objects.filter(
#         time_in__date__gte=today,
#     ).count()
#     return parked_cars_count if parked_cars_count is not None else 0
#
# def count_parked_cars_out_today():
#     today = timezone.now().date() + timedelta(hours=7)
#     parked_cars_count = CarManagement.objects.filter(
#         time_out__date__gte=today,
#     ).count()
#     return parked_cars_count if parked_cars_count is not None else 0

def count_current_cars_parked_cars():
    now = timezone.now() + timedelta(hours=7)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    parked_cars_count = CarManagement.objects.filter(
        time_in__isnull=False,
        time_out__isnull=True,
        time_in__range=(start_of_day, end_of_day),
    ).count()
    return parked_cars_count if parked_cars_count is not None else 0

def count_current_parked_cars():
    now = timezone.now() + timedelta(hours=7)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    parked_cars_count = CarManagement.objects.filter(
        time_in__isnull=False,
        time_out__isnull=False,
        time_in__range=(start_of_day, end_of_day),
        time_out__range=(start_of_day, end_of_day),
    ).count()
    return parked_cars_count if parked_cars_count is not None else 0

def parking_space():
    total_car_in_out = count_current_cars_parked_cars() + count_current_parked_cars()
    total_car_out = count_current_parked_cars()
    car_in = count_current_cars_parked_cars()
    print(f"{total_car_in_out}  {total_car_out}  {car_in}")
    return json.dumps({
        'total_car_in_out': total_car_in_out,
        'total_car_out': total_car_out,
        'car_in': car_in
    })

def find_plate(licenseplate):
    car_instance = CarManagement.objects.filter(
        license_plate=licenseplate,
        time_in__isnull=False,
    ).order_by('-time_in').first()
    if car_instance:
        price = ""
        if expired(licenseplate):
            price = "0"
        else:
            price = pay_day_ticket(car_instance.time_in.strftime("%Y-%m-%d %H:%M:%S"), car_instance.time_out.strftime("%Y-%m-%d %H:%M:%S")) if car_instance.time_out is not None else "",
        return json.dumps({
            'car_plate': car_instance.license_plate,
            'time_car_in': str(car_instance.time_in.strftime("%Y-%m-%d %H:%M:%S")),
            'time_car_out': str(car_instance.time_out.strftime("%Y-%m-%d %H:%M:%S")) if car_instance.time_out is not None else "Xe chưa ra khỏi bãi!",
            'car_price': price,
            'blob_img': base64.b64encode(car_instance.plate_img).decode('utf-8')
        })
    else:
        return json.dumps({
            'car_plate': "",
        })


def check_camera_ping(camera_url):
    rtsp_url = camera_url
    os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
    try:
        cap = cv2.VideoCapture(rtsp_url)
        if cap.isOpened():
            return True
    except Exception as e:
        pass
    return False


