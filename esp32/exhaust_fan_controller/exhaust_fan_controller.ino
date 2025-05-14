/*
 * ESP32 Exhaust Fan Controller
 * This code controls an exhaust fan based on temperature readings
 * and can be controlled manually via MQTT
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "config.h"

// Pin definitions
#define RELAY_PIN       RELAY_PIN_CONFIG  // Relay control pin
#define DHT_PIN         DHT_PIN_CONFIG    // DHT22 sensor pin
#define ONE_WIRE_BUS    ONE_WIRE_BUS_CONFIG  // DS18B20 data pin

// Temperature sensors
#if USE_DHT22
  DHT dht(DHT_PIN, DHT22);
#else
  OneWire oneWire(ONE_WIRE_BUS);
  DallasTemperature sensors(&oneWire);
#endif

// WiFi and MQTT clients
WiFiClient espClient;
PubSubClient client(espClient);

// Variables
float temperature = 0.0;
bool fanStatus = false;
bool autoMode = true;
unsigned long lastTempCheck = 0;
unsigned long lastPublish = 0;
char topic[50];

void setup() {
  Serial.begin(115200);
  
  // Initialize relay pin as output and turn it off
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  
  // Initialize temperature sensor
  #if USE_DHT22
    dht.begin();
  #else
    sensors.begin();
  #endif
  
  // Connect to WiFi
  setupWiFi();
  
  // Initialize MQTT client
  client.setServer(MQTT_SERVER, MQTT_PORT);
  client.setCallback(callback);
  
  // Set device topic
  sprintf(topic, "device/%s", DEVICE_ID);
}

void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  }
  
  // Check MQTT connection
  if (!client.connected()) {
    reconnect();
  }
  
  // MQTT loop to process messages
  client.loop();
  
  // Check temperature every TEMP_CHECK_INTERVAL
  unsigned long currentMillis = millis();
  if (currentMillis - lastTempCheck >= TEMP_CHECK_INTERVAL) {
    lastTempCheck = currentMillis;
    readTemperature();
    
    // Auto control based on temperature
    if (autoMode) {
      if (temperature > TEMP_THRESHOLD && !fanStatus) {
        setFanStatus(true);
      } else if (temperature <= TEMP_THRESHOLD - TEMP_HYSTERESIS && fanStatus) {
        setFanStatus(false);
      }
    }
  }
  
  // Publish sensor data and status every PUBLISH_INTERVAL
  if (currentMillis - lastPublish >= PUBLISH_INTERVAL) {
    lastPublish = currentMillis;
    publishData();
  }
}

void setupWiFi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    // Create client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    // Attempt to connect
    if (client.connect(clientId.c_str(), MQTT_USERNAME, MQTT_PASSWORD)) {
      Serial.println("connected");
      
      // Subscribe to control topic
      char controlTopic[50];
      sprintf(controlTopic, "control/%s", DEVICE_ID);
      client.subscribe(controlTopic);
      
      // Publish initial status
      publishData();
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  // Convert payload to string
  char message[length + 1];
  for (int i = 0; i < length; i++) {
    message[i] = (char)payload[i];
  }
  message[length] = '\0';
  Serial.println(message);
  
  // Parse JSON message
  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, message);
  
  if (!error) {
    // Process control commands
    if (doc.containsKey("fan")) {
      bool newFanStatus = doc["fan"];
      autoMode = false;  // Switch to manual mode
      setFanStatus(newFanStatus);
    }
    
    if (doc.containsKey("auto")) {
      autoMode = doc["auto"];
      if (autoMode) {
        // Immediately apply temperature-based control when switching to auto
        if (temperature > TEMP_THRESHOLD && !fanStatus) {
          setFanStatus(true);
        } else if (temperature <= TEMP_THRESHOLD - TEMP_HYSTERESIS && fanStatus) {
          setFanStatus(false);
        }
      }
    }
  }
}

void readTemperature() {
  #if USE_DHT22
    // Read temperature from DHT22
    float newTemperature = dht.readTemperature();
    
    // Check if reading is valid
    if (!isnan(newTemperature)) {
      temperature = newTemperature;
    }
  #else
    // Read temperature from DS18B20
    sensors.requestTemperatures();
    float newTemperature = sensors.getTempCByIndex(0);
    
    // Check if reading is valid
    if (newTemperature != DEVICE_DISCONNECTED_C) {
      temperature = newTemperature;
    }
  #endif
  
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");
}

void setFanStatus(bool status) {
  fanStatus = status;
  digitalWrite(RELAY_PIN, status ? HIGH : LOW);
  Serial.print("Fan status changed to: ");
  Serial.println(status ? "ON" : "OFF");
  
  // Publish status change immediately
  publishData();
}

void publishData() {
  // Create JSON document
  DynamicJsonDocument doc(1024);
  doc["device_id"] = DEVICE_ID;
  doc["temperature"] = temperature;
  doc["fan"] = fanStatus;
  doc["auto"] = autoMode;
  doc["timestamp"] = millis();
  
  // Serialize JSON to string
  char buffer[256];
  size_t n = serializeJson(doc, buffer);
  
  // Publish to MQTT topic
  client.publish(topic, buffer, n);
}