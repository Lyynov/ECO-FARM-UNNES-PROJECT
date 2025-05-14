"""
MQTT test script for the Exhaust Fan IoT System.
"""

import os
import sys
import json
import time
import random
import logging
import argparse
import paho.mqtt.client as mqtt

# Add the parent directory to the path so we can import the config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MQTT Client for testing
client = mqtt.Client()

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    """Callback when client connects to the broker."""
    if rc == 0:
        logger.info("Connected to MQTT broker")
        # Subscribe to control topics
        client.subscribe("control/#")
    else:
        logger.error(f"Failed to connect to MQTT broker with code {rc}")

def on_message(client, userdata, msg):
    """Callback when a message is received."""
    logger.info(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    """Callback when client disconnects from the broker."""
    if rc != 0:
        logger.warning(f"Unexpected disconnection from MQTT broker with code {rc}")
    else:
        logger.info("Disconnected from MQTT broker")

# Set callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

def send_device_data(device_id, temperature=None, fan_status=None, auto_mode=None):
    """
    Send simulated device data to MQTT broker.
    
    Args:
        device_id (str): Device ID.
        temperature (float, optional): Temperature value. If None, a random value is generated.
        fan_status (bool, optional): Fan status. If None, a random value is generated.
        auto_mode (bool, optional): Auto mode status. If None, defaults to True.
    """
    # Generate random values if not provided
    if temperature is None:
        temperature = round(random.uniform(25.0, 40.0), 1)
    
    if fan_status is None:
        fan_status = temperature > 35.0
    
    if auto_mode is None:
        auto_mode = True
    
    # Create message payload
    payload = {
        "device_id": device_id,
        "temperature": temperature,
        "fan": fan_status,
        "auto": auto_mode,
        "timestamp": int(time.time() * 1000)
    }
    
    # Convert to JSON
    message = json.dumps(payload)
    
    # Publish to device topic
    topic = f"device/{device_id}"
    client.publish(topic, message)
    
    logger.info(f"Published to {topic}: {message}")

def simulate_devices(device_ids, interval=5, duration=60):
    """
    Simulate multiple devices sending data at regular intervals.
    
    Args:
        device_ids (list): List of device IDs to simulate.
        interval (int): Interval between messages in seconds.
        duration (int): Total duration of simulation in seconds.
    """
    start_time = time.time()
    end_time = start_time + duration
    
    logger.info(f"Starting device simulation for {duration} seconds")
    
    while time.time() < end_time:
        for device_id in device_ids:
            # Simulate temperature fluctuations
            temperature = round(random.uniform(30.0, 38.0), 1)
            fan_status = temperature > 35.0
            
            # Send data
            send_device_data(device_id, temperature, fan_status)
        
        # Wait for the next interval
        time.sleep(interval)
    
    logger.info("Device simulation complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test MQTT communication for the Exhaust Fan IoT System.')
    parser.add_argument('--broker', type=str, default=Config.MQTT_BROKER_URL, help='MQTT broker address')
    parser.add_argument('--port', type=int, default=Config.MQTT_BROKER_PORT, help='MQTT broker port')
    parser.add_argument('--username', type=str, default=Config.MQTT_USERNAME, help='MQTT username')
    parser.add_argument('--password', type=str, default=Config.MQTT_PASSWORD, help='MQTT password')
    parser.add_argument('--devices', type=str, default='exhaust_fan_1,exhaust_fan_2', help='Comma-separated list of device IDs')
    parser.add_argument('--interval', type=int, default=5, help='Interval between messages in seconds')
    parser.add_argument('--duration', type=int, default=60, help='Duration of simulation in seconds')
    parser.add_argument('--temperature', type=float, help='Fixed temperature value (if not random)')
    parser.add_argument('--fan', type=str, choices=['on', 'off'], help='Fixed fan status (if not random)')
    
    args = parser.parse_args()
    
    # Set MQTT client credentials
    if args.username and args.password:
        client.username_pw_set(args.username, args.password)
    
    try:
        # Connect to MQTT broker
        logger.info(f"Connecting to MQTT broker at {args.broker}:{args.port}")
        client.connect(args.broker, args.port, 60)
        
        # Start the MQTT loop in a background thread
        client.loop_start()
        
        # Parse device IDs
        device_ids = args.devices.split(',')
        
        # Parse fan status
        fan_status = None
        if args.fan:
            fan_status = args.fan == 'on'
        
        if args.temperature is not None or fan_status is not None:
            # Send a single message with fixed values
            for device_id in device_ids:
                send_device_data(device_id, args.temperature, fan_status)
        else:
            # Run continuous simulation
            simulate_devices(device_ids, args.interval, args.duration)
        
        # Allow time for messages to be sent
        time.sleep(1)
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        # Disconnect from MQTT broker
        client.loop_stop()
        client.disconnect()