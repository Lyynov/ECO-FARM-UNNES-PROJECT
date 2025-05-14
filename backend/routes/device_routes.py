"""
API routes for device management in the Exhaust Fan IoT System.
"""

from flask import Blueprint, jsonify, request, current_app
from services.device_service import (
    get_device_status,
    get_all_devices,
    update_device_info
)
from models.sensor_data import SensorData
from models.control_history import ControlHistory

# Create Blueprint
device_bp = Blueprint('device_routes', __name__)

@device_bp.route('/', methods=['GET'])
def get_devices():
    """Get all registered devices."""
    try:
        devices = get_all_devices()
        return jsonify({
            'success': True,
            'devices': devices
        })
    except Exception as e:
        current_app.logger.error(f"Error getting devices: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve devices'
        }), 500

@device_bp.route('/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get a specific device by ID."""
    try:
        device = get_device_status(device_id)
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        return jsonify({
            'success': True,
            'device': device
        })
    except Exception as e:
        current_app.logger.error(f"Error getting device {device_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve device'
        }), 500

@device_bp.route('/<device_id>', methods=['PUT'])
def update_device(device_id):
    """Update device information."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        name = data.get('name')
        location = data.get('location')
        
        updated_device = update_device_info(device_id, name, location)
        
        if not updated_device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        return jsonify({
            'success': True,
            'device': updated_device
        })
    except Exception as e:
        current_app.logger.error(f"Error updating device {device_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update device'
        }), 500

@device_bp.route('/<device_id>/sensor-data', methods=['GET'])
def get_device_sensor_data(device_id):
    """Get sensor data for a specific device."""
    try:
        # Get query parameters
        limit = request.args.get('limit', default=100, type=int)
        
        # Get device
        device = get_device_status(device_id)
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        # Get sensor data
        sensor_data = SensorData.get_recent_data(device_id, limit)
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'sensor_data': [data.to_dict() for data in sensor_data]
        })
    except Exception as e:
        current_app.logger.error(f"Error getting sensor data for device {device_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve sensor data'
        }), 500

@device_bp.route('/<device_id>/control-history', methods=['GET'])
def get_device_control_history(device_id):
    """Get control history for a specific device."""
    try:
        # Get query parameters
        limit = request.args.get('limit', default=50, type=int)
        
        # Get device
        device = get_device_status(device_id)
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        # Get control history
        control_history = ControlHistory.get_recent_history(device_id, limit)
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'control_history': [history.to_dict() for history in control_history]
        })
    except Exception as e:
        current_app.logger.error(f"Error getting control history for device {device_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve control history'
        }), 500