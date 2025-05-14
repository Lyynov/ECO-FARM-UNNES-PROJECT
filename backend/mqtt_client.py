"""
MQTT client for the Exhaust Fan IoT System backend.
"""

from flask import current_app
from flask_mqtt import Mqtt

# Initialize Flask-MQTT
mqtt_client = Mqtt()

def publish_control_command(device_id, command):
    """
    Publish a control command to a specific device.
    
    Args:
        device_id (str): The ID of the device to control.
        command (dict): The command to send (as a dictionary).
    
    Returns:
        bool: True if publish was successful, False otherwise.
    """
    import json
    
    try:
        # Convert command to JSON string
        payload = json.dumps(command)
        
        # Create topic for the device
        topic = f'control/{device_id}'
        
        # Publish the message
        result = mqtt_client.publish(topic, payload)
        
        # Check if publish was successful
        return result[0] == 0
    except Exception as e:
        current_app.logger.error(f'Error publishing MQTT message: {str(e)}')
        return False