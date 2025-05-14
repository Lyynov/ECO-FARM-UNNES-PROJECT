/*
 * Configuration file for ESP32 Exhaust Fan Controller
 */

// Device identification
#define DEVICE_ID "exhaust_fan_1" // Change to exhaust_fan_2 for the second device

// WiFi configuration
#define WIFI_SSID "YourWiFiNetwork"
#define WIFI_PASSWORD "YourWiFiPassword"

// MQTT configuration
#define MQTT_SERVER "192.168.1.100" // IP address of the Raspberry Pi
#define MQTT_PORT 1883
#define MQTT_USERNAME "mqtt_user"
#define MQTT_PASSWORD "mqtt_password"

// Pin configuration
#define RELAY_PIN_CONFIG 26   // GPIO pin connected to relay
#define DHT_PIN_CONFIG 27     // GPIO pin connected to DHT22
#define ONE_WIRE_BUS_CONFIG 5 // GPIO pin connected to DS18B20

// Sensor configuration
#define USE_DHT22 true // Set to false if using DS18B20

// Temperature control parameters
#define TEMP_THRESHOLD 35.0     // Temperature threshold to turn on fan (in Celsius)
#define TEMP_HYSTERESIS 2.0     // Hysteresis to prevent rapid on/off switching

// Timing configuration (in milliseconds)
#define TEMP_CHECK_INTERVAL 10000  // Check temperature every 10 seconds
#define PUBLISH_INTERVAL 30000     // Publish data every 30 seconds