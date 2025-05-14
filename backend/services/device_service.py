"""
Device service for the Exhaust Fan IoT System.
"""

import json
from datetime import datetime
from flask import current_app
from database import db
from models.device import Device
from models.sensor_data import SensorData
from models.control_history import ControlHistory
from mqtt_client import publish_control_command

def process_device_message(message):
    """
    Process a message received from a device via MQTT.
    
    Args:
        message (mqtt.Message): The received MQTT message.
    
    Returns:
        bool: True if message was processed successfully, False otherwise.
    """
    try:
        # Extract topic and payload
        topic = message.topic
        payload = message.payload.decode('utf-8')
        
        # Parse the payload as JSON
        data = json.loads(payload)
        
        # Extract device_id from topic or data
        if 'device_id' in data:
            device_id = data['device_id']
        else:
            # Extract from topic (format should be 'device/{device_id}')
            device_id = topic.split('/')[-1]
        
        # Get or create device in database
        device = Device.get_or_create(device_id)
        
        # Update device status
        if 'temperature' in data:
            device.last_temperature = data['temperature']
        if 'fan' in data:
            device.fan_status = data['fan']
        if 'auto' in data:
            device.auto_mode = data['auto']
        
        # Update last seen timestamp
        device.last_seen = datetime.utcnow()
        
        # Save device changes
        db.session.commit()
        
        # Add sensor data record
        if 'temperature' in data:
            SensorData.add_sensor_reading(
                device_id=device_id,
                temperature=data['temperature'],
                fan_status=data.get('fan', device.fan_status),
                auto_mode=data.get('auto', device.auto_mode)
            )
        
        current_app.logger.info(f"Processed device message from {device_id}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error processing device message: {str(e)}")
        return False

def send_fan_control(device_id, fan_status, source="app"):
    """
    Send a fan control command to a device.
    
    Args:
        device_id (str): The device ID.
        fan_status (bool): The desired fan status (True = ON, False = OFF).
        source (str): Source of the command (default: "app").
        
    Returns:
        bool: True if command was sent successfully, False otherwise.
    """
    try:
        # Create command
        command = {
            "fan": fan_status
        }
        
        # Publish command to device
        success = publish_control_command(device_id, command)
        
        if success:
            # Record command in control history
            ControlHistory.add_control_record(
                device_id=device_id,
                command_type="fan_control",
                command_value="on" if fan_status else "off",
                source=source
            )
            
            current_app.logger.info(f"Fan control command sent to {device_id}: {'ON' if fan_status else 'OFF'}")
        
        return success
        
    except Exception as e:
        current_app.logger.error(f"Error sending fan control command: {str(e)}")
        return False

def send_mode_control(device_id, auto_mode, source="app"):
    """
    Send a mode control command to a device.
    
    Args:
        device_id (str): The device ID.
        auto_mode (bool): The desired mode (True = AUTO, False = MANUAL).
        source (str): Source of the command (default: "app").
        
    Returns:
        bool: True if command was sent successfully, False otherwise.
    """
    try:
        # Create command
        command = {
            "auto": auto_mode
        }
        
        # Publish command to device
        success = publish_control_command(device_id, command)
        
        if success:
            # Record command in control history
            ControlHistory.add_control_record(
                device_id=device_id,
                command_type="mode_change",
                command_value="auto" if auto_mode else "manual",
                source=source
            )
            
            current_app.logger.info(f"Mode control command sent to {device_id}: {'AUTO' if auto_mode else 'MANUAL'}")
        
        return success
        
    except Exception as e:
        current_app.logger.error(f"Error sending mode control command: {str(e)}")
        return False

def get_device_status(device_id):
    """
    Get the current status of a device.
    
    Args:
        device_id (str): The device ID.
        
    Returns:
        dict: Device status information or None if device not found.
    """
    device = Device.query.get(device_id)
    
    if not device:
        return None
    
    return device.to_dict()

def get_all_devices():
    """
    Get all registered devices.
    
    Returns:
        list: List of devices as dictionaries.
    """
    devices = Device.query.all()
    return [device.to_dict() for device in devices]

def update_device_info(device_id, name=None, location=None):
    """
    Update device information.
    
    Args:
        device_id (str): The device ID.
        name (str, optional): New device name.
        location (str, optional): New device location.
        
    Returns:
        dict: Updated device information or None if device not found.
    """
    device = Device.query.get(device_id)
    
    if not device:
        return None
    
    if name is not None:
        device.name = name
    
    if location is not None:
        device.location = location
    
    db.session.commit()
    
    return device.to_dict()