import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# 1. CẤU HÌNH INFLUXDB LOCAL
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "baMu4IPo-l0Fv2upMh26YsInfOCjXymmQC71_-Buv_yn9qiFyZEvIHzBvXMkW2tbsBJLqG8exAUFJUz5H728Bg=="  # <--- Thay Token của bạn vào đây
INFLUX_ORG = "IoT_Org"
INFLUX_BUCKET = "iot_raw_db"

influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# 2. CẤU HÌNH MQTT BROKER
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "iot/sensors/esp32"

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Đã kết nối Broker! Mã: {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        required_fields = ["device_id", "temperature", "humidity", "distance_cm"]
        
        # Validate dữ liệu đầu vào
        if all(k in payload for k in required_fields):
            temp = float(payload["temperature"])
            hum = float(payload["humidity"])
            dist = float(payload["distance_cm"])
            dev_id = str(payload["device_id"])

            if -40 <= temp <= 80 and 0 <= hum <= 100 and 2 <= dist <= 400:
                point = Point("sensor_data") \
                    .tag("device_id", dev_id) \
                    .field("temperature", temp) \
                    .field("humidity", hum) \
                    .field("distance_cm", dist) \
                    .field("rssi", int(payload.get("rssi", 0))) \
                    .field("sequence", int(payload.get("sequence", 0)))
                
                write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
                print(f"[SUCCESS] Đã lưu vào InfluxDB: Temp={temp}°C, Hum={hum}%, Dist={dist}cm")
    except Exception as e:
        print(f"[ERROR] Lỗi xử lý dữ liệu: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)

print("Đang chờ dữ liệu gửi tới từ Wokwi...")
client.loop_forever()