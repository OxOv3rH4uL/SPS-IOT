#!/bin/bash
pip3 install adafruit-circuitpython-dht --break-system-packages
pip3 install pymongo --break-system-packages
cd Desktop
mkdir -p Sensor
cd Sensor
SCRIPT_PATH="/home/singreed/Desktop/Sensor/final_script.py"

if [ ! -f "$SCRIPT_PATH" ]; then
    curl -o "$SCRIPT_PATH" "https://...../SENSOR_TEMPERATURE.py"
fi

if [ ! -f /home/singreed/Desktop/Sensor/startup.sh ]; then
    curl "https://....../setup_temperature.sh" -o startup.sh
fi

chmod +x /home/singreed/Desktop/Sensor/startup.sh

cat <<EOT | sudo tee /etc/systemd/system/startup_sensor.service
[Unit]
Description=Startup Script Service
After=network.target

[Service]
ExecStart=/bin/bash /home/singreed/Desktop/Sensor/startup.sh
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=startup_sensor

[Install]
WantedBy=default.target
EOT

sudo systemctl daemon-reload
sudo systemctl enable startup_sensor.service
sudo systemctl start startup_sensor.service

echo "### REBOOTING ###"
sudo reboot
