# ESP32 Exhaust Fan Controller

This directory contains the Arduino code for the ESP32 microcontroller that manages the exhaust fan based on temperature readings and allows for remote control via MQTT.

## Hardware Requirements

- ESP32 development board
- DHT22 or DS18B20 temperature sensor
- Relay module (5V)
- Power supply (5V for ESP32, appropriate voltage for relay and fan)
- Wires and connectors
- Contactor (for controlling high-power exhaust fan)

## Installation

1. Install Arduino IDE and ESP32 board support
2. Install the following libraries:
   - WiFi
   - PubSubClient (MQTT client)
   - ArduinoJson
   - DHT (if using DHT22 sensor)
   - OneWire and DallasTemperature (if using DS18B20 sensor)
3. Modify the `config.h` file with your configuration settings
4. Upload the sketch to your ESP32

## Configuration

Edit the `config.h` file to set:

- WiFi credentials
- MQTT broker settings
- Pin configurations
- Temperature thresholds
- Sensor type
- Update intervals

## Wiring Instructions

### Using DHT22 Sensor:
- Connect DHT22 VCC to ESP32 3.3V
- Connect DHT22 GND to ESP32 GND
- Connect DHT22 DATA to ESP32 GPIO27 (configurable in config.h)
- Connect Relay VCC to ESP32 5V or external 5V source
- Connect Relay GND to ESP32 GND
- Connect Relay IN pin to ESP32 GPIO26 (configurable in config.h)
- Connect Relay COM and NO pins to control the contactor

### Using DS18B20 Sensor:
- Connect DS18B20 VCC to ESP32 3.3V
- Connect DS18B20 GND to ESP32 GND
- Connect DS18B20 DATA to ESP32 GPIO5 (configurable in config.h)
- Connect a 4.7kΩ resistor between VCC and DATA
- Connect Relay as described above

## Operation

The ESP32 controller operates in the following modes:

### Automatic Mode
- Reads temperature values at regular intervals
- If temperature exceeds threshold (default: 35°C), it turns on the fan
- If temperature drops below threshold minus hysteresis, it turns off the fan
- Reports temperature and fan status to MQTT broker

### Manual Mode
- Allows control of the fan via MQTT commands
- Continues to read and report temperature values
- Does not automatically control the fan based on temperature

## MQTT Topics

### Publishing (ESP32 to Server)
- `device/{device_id}`: Publishes JSON messages with temperature, fan status, and mode

### Subscribing (ESP32 listens for commands)
- `control/{device_id}`: Listens for control commands from the server

## Troubleshooting

1. Check serial output (115200 baud) for debug information
2. Verify WiFi connection and credentials
3. Ensure MQTT broker is running and accessible
4. Check sensor connections and wiring
5. Verify relay is working by testing manual control

## Power Management

For reliable operation, consider:
- Using a stable power supply for the ESP32
- Adding a capacitor (100-220μF) between VCC and GND to stabilize power
- Implementing a hardware watchdog for automatic reset in case of crash