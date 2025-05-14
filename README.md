# IoT Exhaust Fan Control System

## 📌 Project Description

This system is an **IoT solution based on ESP32 and Raspberry Pi** for **automatically controlling two exhaust fans** based on **temperature** and also **manually through an Android application**. The system integrates **temperature sensors**, **relays**, **contactors**, and **wireless communication** with **MQTT**, and provides a **mobile user interface** for monitoring and control.

## 🧩 Main Components

* **ESP32** (2 units): Main microcontroller for each exhaust fan circuit
* **Temperature sensor**: DHT22 / DS18B20 to read temperature
* **Relay 220V + Contactor**: To control the exhaust fan based on system logic
* **Raspberry Pi 4 Model B**: Gateway, backend server, MQTT broker
* **Android App**: To display temperature and exhaust status, and send manual ON/OFF commands
* **WSN**: Wireless protocol like MQTT as the data communication channel
* **Database**: Store temperature data and control history

## ⚙️ Working Mechanism

1. **Temperature sensor** on each ESP32 reads the room temperature.
2. If temperature > 35°C, ESP32 will:
   * Turn on exhaust fan through relay and contactor
   * Send temperature and exhaust status data to Raspberry Pi via MQTT
3. **Raspberry Pi**:
   * Stores data in database
   * Provides REST API for Android app
   * Receives and forwards manual commands from Android to ESP32
4. **Android App**:
   * Displays temperature and ON/OFF status of each exhaust
   * Sends manual ON/OFF commands to server

## 🔧 Repository Structure

```
├── android/                     # Android mobile application
├── backend/                     # Python Flask backend server
├── doc/                         # Documentation and diagrams
├── esp32/                       # ESP32 Arduino code
├── hardware/                    # Hardware datasheets and schematics
├── raspberry_pi/                # Raspberry Pi setup and configuration
└── scripts/                     # Utility scripts for setup and maintenance
```

## 📋 Installation Instructions

### ESP32 Setup

1. Open `esp32/exhaust_fan_controller/exhaust_fan_controller.ino` in Arduino IDE
2. Edit `config.h` with your WiFi and MQTT settings
3. Install required libraries listed in `esp32/libraries.txt`
4. Upload the sketch to your ESP32 devices

### Raspberry Pi Setup

1. Install Raspberry Pi OS (Lite is sufficient)
2. Log in and run the installation script:
   ```
   sudo bash ./raspberry_pi/install.sh
   ```
3. The script installs and configures:
   - Python and required packages
   - Mosquitto MQTT broker
   - Backend server and database
   - Systemd services for automatic startup

### Android App Setup

1. Open `android/ExhaustFanControl` in Android Studio
2. Edit the server URL in `MainActivity.kt` to point to your Raspberry Pi's IP address
3. Build and install the APK on your Android device

## 🔌 Hardware Setup

1. Follow the wiring diagram in `doc/wiring_diagram.png`
2. Connect the temperature sensor to ESP32 as specified in config
3. Connect the relay to ESP32 and to the contactor
4. Connect the contactor to the exhaust fan power supply

## 📱 Using the Android App

1. Launch the app to view the current status of both exhaust fans
2. Use the toggle switch to manually control fans
3. Use the Auto Mode switch to enable/disable automatic temperature-based control
4. Pull down to refresh the data from the server

## 🔍 Monitoring and Maintenance

### Logs
- Backend logs: `/opt/exhaust-fan-system/logs/exhaust_fan.log`
- System service logs: `journalctl -u exhaust-backend.service`
- MQTT logs: `journalctl -u mosquitto.service`

### Database Backup
Run the backup script periodically:
```
sudo bash /opt/exhaust-fan-system/scripts/backup_db.sh
```

## 🔧 Troubleshooting

- Check ESP32 serial output (115200 baud) for debugging
- Verify MQTT connection using `mosquitto_sub -h localhost -t '#' -v`
- Test the API directly: `curl http://localhost:5000/api/health`
- Check systemd service status: `systemctl status exhaust-backend.service`

## 🤝 Contributing

Contributions to this project are welcome. Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.