sudo mkdir -p /lib/systemd/system/
sudo cp pi-active-cooling.service /lib/systemd/system/pi-active-cooling.service

sudo mkdir -p /usr/python/
#sudo cp pi-active-cooling.py /usr/python/pi-active-cooling.py

sudo systemctl enable pi-active-cooling.service 
sudo systemctl start pi-active-cooling.service 
