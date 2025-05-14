"""
API routes for device control in the Exhaust Fan IoT System.
"""

from flask import Blueprint, jsonify, request, current_app
from services.device_service import (
    get_device_status,
    send_fan_control,
    send_mode_control
)

# Create Blueprint
control_bp = Blueprint('control_routes', __name__)

@control_bp.route('/<device_id>/fan', methods=['POST'])
def control_fan(device_id):
    """Control fan status for a specific device."""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'No status provided'
            }), 400
        
        # Get desired fan status (ON/OFF)
        status = data['status']
        
        # Validate status value
        if not isinstance(status, bool) and status not in ('on', 'off', True, False, 0, 1):
            return jsonify({
                'success': False,
                'error': 'Invalid status value'
            }), 400
        
        # Convert string status to boolean
        if status == 'on' or status == 1 or status is True:
            fan_status = True
        else:
            fan_status = False
        
        # Get source of command (default: "app")
        source = data.get('source', 'app')
        
        # Check if device exists
        device = get_device_status(device_id)
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        # Send control command
        success = send_fan_control(device_id, fan_status, source)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to send control command'
            }), 500
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'fan_status': fan_status
        })
    except Exception as e:
        current_app.logger.error(f"Error controlling fan for device {device_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to control fan'
        }), 500

@control_bp.route('/<device_id>/mode', methods=['POST'])
def control_mode(device_id):
    """Control operating mode for a specific device."""
    try:
        data = request.get_json()
        
        if not data or 'mode' not in data:
            return jsonify({
                'success': False,
                'error': 'No mode provided'
            }), 400
        
        # Get desired mode (AUTO/MANUAL)
        mode = data['mode']
        
        # Validate mode value
        if not isinstance(mode, bool) and mode not in ('auto', 'manual', True, False, 0, 1):
            return jsonify({
                'success': False,
                'error': 'Invalid mode value'
            }), 400
        
        # Convert string mode to boolean
        if mode == 'auto' or mode == 1 or mode is True:
            auto_mode = True
        else:
            auto_mode = False
        
        # Get source of command (default: "app")
        source = data.get('source', 'app')
        
        # Check if device exists
        device = get_device_status(device_id)
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        # Send control command
        success = send_mode_control(device_id, auto_mode, source)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to send mode command'
            }), 500
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'auto_mode': auto_mode
        })
    except Exception as e:
        current_app.logger.error(f"Error controlling mode for device {device_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to control mode'
        }), 500