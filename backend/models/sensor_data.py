"""
Sensor Data model for the Exhaust Fan IoT System.
"""

from datetime import datetime
from database import db

class SensorData(db.Model):
    """Database model for sensor data from exhaust fan devices."""
    
    __tablename__ = 'sensor_data'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), db.ForeignKey('devices.id'), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    fan_status = db.Column(db.Boolean, nullable=False)
    auto_mode = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<SensorData {self.id} for device {self.device_id}>'
    
    def to_dict(self):
        """Convert sensor data to dictionary representation."""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'temperature': self.temperature,
            'fan_status': self.fan_status,
            'auto_mode': self.auto_mode,
            'timestamp': self.timestamp.isoformat()
        }
    
    @staticmethod
    def add_sensor_reading(device_id, temperature, fan_status, auto_mode):
        """
        Add a new sensor reading to the database.
        
        Args:
            device_id (str): The device ID.
            temperature (float): The temperature reading.
            fan_status (bool): Current fan status (on/off).
            auto_mode (bool): Whether the device is in automatic mode.
            
        Returns:
            SensorData: The new sensor data record.
        """
        sensor_data = SensorData(
            device_id=device_id,
            temperature=temperature,
            fan_status=fan_status,
            auto_mode=auto_mode
        )
        
        db.session.add(sensor_data)
        db.session.commit()
        
        return sensor_data
    
    @staticmethod
    def get_recent_data(device_id, limit=100):
        """
        Get recent sensor data for a device.
        
        Args:
            device_id (str): The device ID.
            limit (int): Maximum number of records to return.
            
        Returns:
            list: List of sensor data records.
        """
        return SensorData.query.filter_by(device_id=device_id) \
                              .order_by(SensorData.timestamp.desc()) \
                              .limit(limit) \
                              .all()