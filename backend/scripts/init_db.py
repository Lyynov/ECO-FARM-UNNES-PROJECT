"""
Database initialization script for the Exhaust Fan IoT System.
"""

import os
import sys
import logging

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models.device import Device
from models.sensor_data import SensorData
from models.control_history import ControlHistory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize the database with tables and default data."""
    with app.app_context():
        logger.info("Creating database tables...")
        db.create_all()
        
        # Check if default devices exist
        logger.info("Creating default devices if they don't exist...")
        
        # Default device 1
        device1 = Device.query.get('exhaust_fan_1')
        if not device1:
            device1 = Device(
                id='exhaust_fan_1',
                name='Exhaust Fan 1',
                location='Room 1',
                last_temperature=0.0,
                fan_status=False,
                auto_mode=True
            )
            db.session.add(device1)
            logger.info("Created default device: exhaust_fan_1")
        
        # Default device 2
        device2 = Device.query.get('exhaust_fan_2')
        if not device2:
            device2 = Device(
                id='exhaust_fan_2',
                name='Exhaust Fan 2',
                location='Room 2',
                last_temperature=0.0,
                fan_status=False,
                auto_mode=True
            )
            db.session.add(device2)
            logger.info("Created default device: exhaust_fan_2")
        
        # Commit changes
        db.session.commit()
        logger.info("Database initialization complete.")

def purge_database():
    """Remove all data from the database."""
    with app.app_context():
        logger.warning("Purging all data from the database...")
        
        # Remove all data from tables
        ControlHistory.query.delete()
        SensorData.query.delete()
        Device.query.delete()
        
        # Commit changes
        db.session.commit()
        logger.warning("Database purge complete.")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize or purge the database.')
    parser.add_argument('--purge', action='store_true', help='Purge all data from the database')
    args = parser.parse_args()
    
    if args.purge:
        purge_database()
    else:
        initialize_database()