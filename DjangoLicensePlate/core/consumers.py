import json
import asyncio
import queue
import paho.mqtt.client as mqtt
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from paho.mqtt import publish


class MainConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_queue = queue.Queue()
        self.message_sent = True
        self.check_zone_timer = None

    async def connect(self):
        await self.accept()
        self.loop = asyncio.get_event_loop()
        await self.init_mqtt()
        self.loop.create_task(self.process_queue())

    async def disconnect(self, close_code):
        if self.client.is_connected():
            self.client.disconnect()

    async def init_mqtt(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASS)
        self.client.connect(settings.MQTT_SERVER, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("hoangdieu/rtsp")

    def on_message(self, client, userdata, msg):
        payload = str(msg.payload.decode('utf-8'))
        topic = msg.topic
        if topic == "hoangdieu/rtsp":
            self.message_queue.put(payload)
            if self.message_sent:
                self.loop.create_task(self.send_next_message())

    async def process_queue(self):
        while True:
            if self.message_sent and not self.message_queue.empty():
                await self.send_next_message()
            await asyncio.sleep(0.1)

    async def send_next_message(self):
        self.message_sent = False
        message = self.message_queue.get_nowait()
        await self.send(text_data=message)
        self.reset_check_zone_timer()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = text_data_json.get('command')
        if command == "continue":
            publish.single("hoangdieu/gate", str(text_data_json.get('gate')), hostname=settings.MQTT_SERVER, port=settings.MQTT_PORT)
            self.message_sent = True
        if command == "sendprice":
            publish.single("hoangdieu/price", str(text_data_json.get('price')), hostname=settings.MQTT_SERVER,
                           port=settings.MQTT_PORT)

    def reset_check_zone_timer(self):
        if self.check_zone_timer:
            self.check_zone_timer.cancel()
        self.check_zone_timer = self.loop.call_later(60, self.loop.create_task, self.send_check_zone_message())

    async def send_check_zone_message(self):
        if self.message_sent:
            await self.send(text_data="check_zone")

