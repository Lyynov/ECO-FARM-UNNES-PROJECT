#!/bin/bash

# Exhaust Fan IoT System Installation Script for Raspberry Pi
# This script installs and configures all necessary components for the backend server

# Exit on error
set -e

# Show commands as they are executed
set -x

# Variables
PROJECT_DIR="/opt/exhaust-fan-system"
BACKEND_DIR="$PROJECT_DIR/backend"
MOSQUITTO_DIR="$PROJECT_DIR/mosquitto"
SYSTEMD_DIR="/etc/systemd/system"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_DIR="$PROJECT_DIR/logs"

# Make sure we're running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" 
    exit 1
fi

echo "========================================"
echo "Exhaust Fan IoT System Installation"
echo "========================================"

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "Installing dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    mosquitto \
    mosquitto-clients \
    sqlite3 \
    git \
    nginx

# Create project directories
echo "Creating project directories..."
mkdir -p $PROJECT_DIR
mkdir -p $BACKEND_DIR
mkdir -p $MOSQUITTO_DIR
mkdir -p $BACKUP_DIR
mkdir -p $LOG_DIR

# Clone the repository (if this script is not already part of it)
if [ ! -d "$BACKEND_DIR/app.py" ]; then
    echo "Cloning project repository..."
    # Assuming the repository is not already cloned or copied
    # You would replace this with your actual repository URL
    # git clone https://github.com/yourusername/exhaust-fan-system.git $PROJECT_DIR
    
    # For now, just copy the files from the current directory
    echo "Copying project files..."
    cp -r . $PROJECT_DIR
fi

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
cd $BACKEND_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configure Mosquitto MQTT broker
echo "Configuring Mosquitto MQTT broker..."
cp $PROJECT_DIR/raspberry_pi/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf
mkdir -p /etc/mosquitto/conf.d

# Create MQTT user
echo "Creating MQTT user..."
mosquitto_passwd -c /etc/mosquitto/passwd mqtt_user
# Note: You'll be prompted to enter a password

# Set up Systemd service for Mosquitto
echo "Setting up Systemd service for Mosquitto..."
cp $PROJECT_DIR/raspberry_pi/systemd/mosquitto.service $SYSTEMD_DIR/

# Set up Systemd service for the backend
echo "Setting up Systemd service for the backend..."
cp $PROJECT_DIR/raspberry_pi/systemd/exhaust-backend.service $SYSTEMD_DIR/

# Initialize the database
echo "Initializing database..."
cd $BACKEND_DIR
source venv/bin/activate
python scripts/init_db.py

# Enable and start services
echo "Enabling and starting services..."
systemctl daemon-reload
systemctl enable mosquitto.service
systemctl start mosquitto.service
systemctl enable exhaust-backend.service
systemctl start exhaust-backend.service

# Set up NGINX as a reverse proxy (optional)
echo "Setting up NGINX as a reverse proxy..."
cat > /etc/nginx/sites-available/exhaust-fan-system << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/exhaust-fan-system /etc/nginx/sites-enabled/
systemctl restart nginx

echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo "Backend API: http://localhost/api"
echo "MQTT Broker: localhost:1883"
echo ""
echo "You can check the service status with:"
echo "  systemctl status exhaust-backend.service"
echo "  systemctl status mosquitto.service"
echo ""
echo "View logs with:"
echo "  journalctl -u exhaust-backend.service"
echo "  journalctl -u mosquitto.service"
echo "========================================"