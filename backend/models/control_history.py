"""
Control History model for the Exhaust Fan IoT System.
"""

from datetime import datetime
from database import db

class ControlHistory(db.Model):
    """Database model for control commands sent to exhaust fan devices."""
    
    __tablename__ = 'control_history'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), db.ForeignKey('devices.id'), nullable=False)
    command_type = db.Column(db.String(50), nullable=False)  # 'fan_control', 'mode_change', etc.
    command_value = db.Column(db.String(50), nullable=False)  # 'on', 'off', 'auto', 'manual', etc.
    source = db.Column(db.String(50), nullable=False)  # 'app', 'auto', 'schedule'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ControlHistory {self.id} for device {self.device_id}>'
    
    def to_dict(self):
        """Convert control history to dictionary representation."""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'command_type': self.command_type,
            'command_value': self.command_value,
            'source': self.source,
            'timestamp': self.timestamp.isoformat()
        }
    
    @staticmethod
    def add_control_record(device_id, command_type, command_value, source):
        """
        Add a new control record to the database.
        
        Args:
            device_id (str): The device ID.
            command_type (str): Type of command ('fan_control', 'mode_change', etc.).
            command_value (str): Value of the command ('on', 'off', 'auto', 'manual', etc.).
            source (str): Source of the command ('app', 'auto', 'schedule').
            
        Returns:
            ControlHistory: The new control history record.
        """
        control_record = ControlHistory(
            device_id=device_id,
            command_type=command_type,
            command_value=command_value,
            source=source
        )
        
        db.session.add(control_record)
        db.session.commit()
        
        return control_record
    
    @staticmethod
    def get_recent_history(device_id, limit=50):
        """
        Get recent control history for a device.
        
        Args:
            device_id (str): The device ID.
            limit (int): Maximum number of records to return.
            
        Returns:
            list: List of control history records.
        """
        return ControlHistory.query.filter_by(device_id=device_id) \
                                  .order_by(ControlHistory.timestamp.desc()) \
                                  .limit(limit) \
                                  .all()