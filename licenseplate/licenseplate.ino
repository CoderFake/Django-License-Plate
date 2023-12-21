#include <Wire.h>
#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <LiquidCrystal_I2C.h>
#include <PCF8575.h>
#include <Servo.h>

#define TRIGGER_PIN1  4  
#define ECHO_PIN1     5  
#define TRIGGER_PIN2  6  
#define ECHO_PIN2     7

#define MQTT_SERVER "mqtt-dashboard.com"
#define MQTT_PORT 1883
#define MQTT_USER "hoangdieu"
#define MQTT_PASSWORD "Dieu2002@"

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
byte ip[] = { 192, 168, 1, 200};

EthernetClient ethClient;
PubSubClient client(ethClient);

LiquidCrystal_I2C lcd(0x27, 16, 2); 
PCF8575 pcf8575(0x22); 

Servo myServo_in;
Servo myServo_out;


String data = "0000000000000000";
int statusIn = 1;
int statusOut = 1;

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  if (String(topic) == "hoangdieu/price") {
    lcd.clear();
    String price = "Gia ve: " + message;
    lcd.setCursor(0,0);
    lcd.print(price);
    lcd.setCursor(0,1);
    lcd.print("Cam on quy khach!");
  } else if (String(topic) == "hoangdieu/parkingspace") {
    data = message;
    updatePCF8575();
  } else if (String(topic) == "hoangdieu/gate") {
    controlGates(message);
  }
}
void setup() {
  Wire.begin();
  Ethernet.begin(mac, ip);
  Serial.begin(9600);
  pcf8575.begin();
  for(int i = 1; i < 16; i++)
    pcf8575.write(i, LOW);
  lcd.init();
  lcd.backlight();
  myServo_in.attach(2);
  myServo_in.write(85); 
  myServo_out.attach(3);
  myServo_out.write(90); 
  pinMode(TRIGGER_PIN1, OUTPUT);
  pinMode(ECHO_PIN1, INPUT);
  pinMode(TRIGGER_PIN2, OUTPUT);
  pinMode(ECHO_PIN2, INPUT);
  client.setServer(MQTT_SERVER, MQTT_PORT);
  client.setCallback(callback);
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    String clientId = "IoT";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
      Serial.println("Connected!");
      client.subscribe("hoangdieu/price");
      client.subscribe("hoangdieu/parkingspace");
      client.subscribe("hoangdieu/gate");
    }else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  checkDistance();
}


void checkDistance() {
  long duration1, distance1;
  digitalWrite(TRIGGER_PIN1, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN1, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN1, LOW);
  duration1 = pulseIn(ECHO_PIN1, HIGH);
  distance1 = duration1 * 0.034 / 2;
  long duration2, distance2;
  digitalWrite(TRIGGER_PIN2, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN2, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN2, LOW);
  duration2 = pulseIn(ECHO_PIN2, HIGH);
  distance2 = duration2 * 0.034 / 2;
  if (distance1 > 0 && distance1 <= 10) {
    if (statusIn == 1) {
      client.publish("hoangdieu/rtsp", "in");
      Serial.println("publish: in");
      statusIn = 0;
    }
  } 
  if (distance2 > 0 && distance2 <= 10) {
      if (statusOut == 1) {
        client.publish("hoangdieu/rtsp", "out");
        Serial.println("publish: out");
        statusOut = 0;
      }
  }
}

void updatePCF8575() {
  for (int i = 0; i < 16; i++) {  
    pcf8575.write(i, int(data[i] - '0')); 
  }
}

void controlGates(String command) {
  if (command == "in") {
    myServo_in.write(0); 
    delay(5000);
    myServo_in.write(85);
    statusIn = 1;
  } else if (command == "out") {
    myServo_out.write(0); 
    delay(5000);
    lcd.clear();
    myServo_out.write(90);
    statusOut = 1;
  }
  else {
    statusIn = 1;
    statusOut = 1;
  }
}



// #include <SPI.h>
// #include <Ethernet.h>
// #include <PubSubClient.h>

// const int button = 7;

// byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
// byte ip[] = { 192, 168, 1, 200 };

// const char* mqttServerIP = "mqtt-dashboard.com";
// EthernetClient unoClient;
// PubSubClient client(unoClient);
// unsigned long lastMsg = 0;


// void callback(char* topic, byte* payload, unsigned int length) {
//   String str;
//   Serial.print("Message arrived [");
//   Serial.print(topic);
//   Serial.print("] ");
//   for (int i = 0; i < length; i++) {
//     str += (char)payload[i];
//   }
//   Serial.println(str);
// }

// void reconnect() {
//   while (!client.connected()) {
//     Serial.print("Attempting MQTT connection...");
//     String clientId = "ESP32Client-";
//     clientId += String(random(0xffff), HEX);
//     if (client.connect(clientId.c_str())) {
//       Serial.println("Connected to " + clientId);
//       client.subscribe("/hoangdieu/scan/barie_in");
//       client.subscribe("/hoangdieu/scan/barie_out");
//       client.subscribe("/hoangdieu/scan/price");
//       client.subscribe("/hoangdieu/scan/");
//     } else {
//       Serial.print("failed, rc=");
//       Serial.print(client.state());
//       Serial.println(" try again in 5 seconds");
//       delay(5000);
//     }
//   }
// }

// void setup() {
//     Ethernet.begin(mac, ip);
//     Serial.begin(9600);
//     pinMode(button, INPUT);
//     client.setServer(mqttServerIP, 1883);
//     client.setCallback(callback);
// } 

// void loop() {
//   if (!client.connected()) {
//     reconnect();
//   }
//   client.loop();
//   if (digitalRead(button) == HIGH) {
//     client.publish("/hoangdieu/scan", String("1").c_str());
//     // client.publish("/hoangdieu/scan/camera_out", String("out").c_str());
//     // client.publish("/hoangdieu/scan/camera_zone", String("zone").c_str());
//     delay(1000);
//     client.publish("/hoangdieu/scan", String("0").c_str());
//   }
  
// }


// #include "Arduino.h"
// #include "PCF8575.h"

// String data = "1111111100000000";
// PCF8575 pcf8575(0x22);

// void setup()
// {
// 	Serial.begin(9600); 
// 	pcf8575.begin();
//   for(int i = 1; i < 16; i++)
//     pcf8575.write(i, 0);
// }

// void loop()
// {
//   for(int i = 1; i < 16; i++)
//     pcf8575.write(i, int(data[i] - '0')); 

// }


