"""
Configuration file for the Exhaust Fan IoT System backend.
"""

import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///exhaust_fan.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MQTT configuration
    MQTT_BROKER_URL = os.environ.get('MQTT_BROKER_URL') or 'localhost'
    MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT') or 1883)
    MQTT_USERNAME = os.environ.get('MQTT_USERNAME') or 'mqtt_user'
    MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD') or 'mqtt_password'
    MQTT_CLIENT_ID = os.environ.get('MQTT_CLIENT_ID') or 'exhaust_fan_backend'
    MQTT_KEEPALIVE = int(os.environ.get('MQTT_KEEPALIVE') or 60)
    
    # Application-specific configuration
    TEMPERATURE_THRESHOLD = float(os.environ.get('TEMPERATURE_THRESHOLD') or 35.0)
    TEMPERATURE_HYSTERESIS = float(os.environ.get('TEMPERATURE_HYSTERESIS') or 2.0)
    
    # API configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Logging configuration
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT') or False
    
    # Data retention configuration (in days)
    SENSOR_DATA_RETENTION = int(os.environ.get('SENSOR_DATA_RETENTION') or 30)
    CONTROL_HISTORY_RETENTION = int(os.environ.get('CONTROL_HISTORY_RETENTION') or 60)