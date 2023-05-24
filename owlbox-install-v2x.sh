#!/bin/bash
echo "Changing to /home/pi/owlbox_files"
cd /home/pi/owlbox_files
rm /home/pi/owlbox_files/logs/_blank.txt
echo "...Done."
echo "Making makv2xbox executable..."
chmod +x common/makev2xbox
echo "Copying wpa_supplicant-wlan0.conf..."
sudo cp common/wpa_supplicant/v2x/wpa_supplicant-wlan0.conf /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
echo "Copying wpa_supplicant-wlan1.conf..."
sudo cp common/wpa_supplicant/v2x/wpa_supplicant-wlan1.conf /etc/wpa_supplicant/wpa_supplicant-wlan1.conf
echo "Copying rc.local..."
sudo cp common/rc.local /etc/rc.local
echo "OwlBox-V2X Install Complete!"
