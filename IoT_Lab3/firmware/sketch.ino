#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

const char* MQTT_SERVER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "iot/sensors/esp32";

#define DHT_PIN 15
#define DHT_TYPE DHT22
const int TRIG_PIN = 5;
const int ECHO_PIN = 18;
const int LED_PIN = 2;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
DHT dht(DHT_PIN, DHT_TYPE);

const unsigned long SEND_INTERVAL_MS = 5000;
unsigned long lastSend = 0;
unsigned long sequenceNo = 0;

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;
  Serial.print("Connecting WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected | IP: " + WiFi.localIP().toString());
}

void connectMQTT() {
  while (!mqttClient.connected()) {
    String clientId = "ESP32-Bai2-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    Serial.print("Connecting MQTT...");
    if (mqttClient.connect(clientId.c_str())) {
      Serial.println(" connected");
    } else {
      Serial.print(" failed, rc=");
      Serial.println(mqttClient.state());
      delay(2000);
    }
  }
}

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return NAN;
  return duration * 0.0343f / 2.0f;
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  dht.begin();
  connectWiFi();

  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setBufferSize(256);
  Serial.println("System ready.");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (!mqttClient.connected()) connectMQTT();
  mqttClient.loop();

  unsigned long now = millis();
  if (now - lastSend < SEND_INTERVAL_MS) return;
  lastSend = now;

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  float distance = readDistanceCm();

  if (isnan(temperature) || isnan(humidity) || isnan(distance)) {
    Serial.println("Invalid sensor data - skip publish");
    return;
  }

  sequenceNo++;
  int rssi = WiFi.RSSI();
  unsigned long uptime_s = millis() / 1000;

  char payload[256];
  snprintf(
    payload,
    sizeof(payload),
    "{\"device_id\":\"ESP32_WOKWI_01\","
    "\"temperature\":%.2f,"
    "\"humidity\":%.2f,"
    "\"distance_cm\":%.2f,"
    "\"rssi\":%d,"
    "\"sequence\":%lu,"
    "\"uptime_s\":%lu}",
    temperature, humidity, distance, rssi, sequenceNo, uptime_s
  );

  bool ok = mqttClient.publish(MQTT_TOPIC, payload);

  Serial.println();
  Serial.println("========== TELEMETRY ==========");
  Serial.print("JSON    : "); Serial.println(payload);
  Serial.print("Publish : "); Serial.println(ok ? "OK" : "FAILED");
  Serial.println("================================");

  digitalWrite(LED_PIN, HIGH);
  delay(80);
  digitalWrite(LED_PIN, LOW);
}