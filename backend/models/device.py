"""
Device model for the Exhaust Fan IoT System.
"""

from datetime import datetime
from database import db

class Device(db.Model):
    """Database model for exhaust fan devices."""
    
    __tablename__ = 'devices'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    last_temperature = db.Column(db.Float)
    fan_status = db.Column(db.Boolean, default=False)
    auto_mode = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sensor_data = db.relationship('SensorData', backref='device', lazy='dynamic')
    control_history = db.relationship('ControlHistory', backref='device', lazy='dynamic')
    
    def __repr__(self):
        return f'<Device {self.id}>'
    
    def to_dict(self):
        """Convert device to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'last_temperature': self.last_temperature,
            'fan_status': self.fan_status,
            'auto_mode': self.auto_mode,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def get_or_create(device_id):
        """
        Get a device by ID or create it if it doesn't exist.
        
        Args:
            device_id (str): The device ID.
            
        Returns:
            Device: The device instance.
        """
        device = Device.query.get(device_id)
        
        if not device:
            # Create a new device with default values
            device = Device(
                id=device_id,
                name=f'Exhaust Fan {device_id[-1]}',  # Assumes device_id ends with a number
                location='Unknown'
            )
            db.session.add(device)
            db.session.commit()
        
        return device