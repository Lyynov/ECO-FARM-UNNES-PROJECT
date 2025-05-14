"""
Flask application for Exhaust Fan IoT System's backend server
running on Raspberry Pi.
"""

from flask import Flask, jsonify, request
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Import modules
from config import Config
from database import db
from mqtt_client import mqtt_client
from models.device import Device
from models.sensor_data import SensorData
from models.control_history import ControlHistory

# Import routes
from routes.device_routes import device_bp
from routes.control_routes import control_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/exhaust_fan.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Exhaust Fan Backend startup')

# Initialize database
db.init_app(app)

# Initialize MQTT client
mqtt_client.init_app(app)

# Register blueprints
app.register_blueprint(device_bp, url_prefix='/api/devices')
app.register_blueprint(control_bp, url_prefix='/api/control')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error('Server Error: %s', str(error))
    return jsonify({'error': 'Internal server error'}), 500

# Create database tables if they don't exist
@app.before_first_request
def create_tables():
    db.create_all()

# MQTT callbacks
@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        app.logger.info('Connected to MQTT Broker')
        # Subscribe to device topics
        client.subscribe('device/#')
    else:
        app.logger.error(f'Failed to connect to MQTT Broker with code {rc}')

@mqtt_client.on_message()
def handle_message(client, userdata, message):
    try:
        from services.device_service import process_device_message
        process_device_message(message)
    except Exception as e:
        app.logger.error(f'Error processing MQTT message: {str(e)}')

# Run the app if executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)