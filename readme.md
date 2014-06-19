# Setup instructions
Install NOOBS raspbian onto the device
Update keyboard layout and locale to be en_US

############### WiFi INSTRUCTIONS ###############

Add a WPA_Supplicant configuration:

/etc/wpa_supplicant/wpa_supplicant.conf
```
ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1

network={
    ssid="#####"
    psk="######"
    proto=WPA
    key_mgmt=WPA-PSK
    pairwise=TKIP
    group=TKIP
    id_str="GBZ"
}
```

Configure the network interfaces file:

/etc/network/interfaces
```
auto lo

iface lo inet loopback
iface eth0 inet dhcp

allow-hotplug wlan0
iface default inet dhcp

auto wlan0
    iface wlan0 inet static
    address 192.168.0.90
    netmask 255.255.255.0
    gateway 192.168.0.1
    wpa-conf            /etc/wpa_supplicant/wpa_supplicant.conf
```

############### ADAFRUIT INSTRUCTIONS ###############
https://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/cm108-type

``` bash
# Update firmware because it is a C-Media 108
sudo apt-get install git-core
sudo wget https://raw.github.com/Hexxeh/rpi-update/master/rpi-update -O /usr/bin/rpi-update
sudo chmod +x /usr/bin/rpi-update
sudo BRANCH=next rpi-update
sudo reboot
```

``` bash
# Update Alsa config https://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/updating-alsa-config
```

``` bash
# Tests  
speaker-test -c2 -D hw:0,0
aplay /usr/share/sounds/alsa/Front_Center.wav
```

############### Python setup ###############

Clone the git project:
``` bash
sudo git clone https://github.com/benzittlau/pi_ano.git .
```

Install PIP:
``` bash
sudo apt-get install python-pip
```

Install Python.h for pyaudio compilation:
``` bash
sudo apt-get install python-dev
```

Install PortAudio:
``` bash
sudo apt-get install portaudio19-dev
```

Install PyAudio:
``` bash
#sudo apt-get install python-pyaudio
sudo pip install pyaudio
```


########### PULSE AUDIO #############
``` bash
sudo apt-get install pulseaudio
```




