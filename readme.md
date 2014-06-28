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
    wireless-power off
```

The wireless-power off is an attempt to fix network dropout by disabling power management
on the wifi interface.

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

Note this ended up not being necessary, so you can ignore this step

``` bash
sudo apt-get install pulseaudio
```









############## WICD SETUP ##################

NOTE: Decided not to use wicd because it doesn't support network fallback with priorities
NOTE: went back to WICD after fighting with the default network management on raspbian.  The
key that I think I was missing from before was deleting the entries from the /etc/network/interfaces file.

If you’re using Raspbian, and you’ve not installed Wicd-curses just type:
You’ll get a list of the wireless network found by the Raspberry PI

``` bash
sudo apt-get update
sudo apt-get install wicd-cli wicd-curses
sudo wicd-curses
```

You also need to remove the lines from the /etc/network/interfaces for wlan0 or it will
cause issues for wicd.





################## FFMPEG SETUP ##############


Before:
``` bash
sudo apt-get install libmp3lame-dev
```

http://sirlagz.net/2012/08/04/how-to-stream-a-webcam-from-the-raspberry-pi/

1. Add the following lines into /etc/apt/sources.list
    deb-src http://www.deb-multimedia.org sid main
    deb http://www.deb-multimedia.org wheezy main non-free
1. Run apt-get update
1. Run apt-get install deb-multimedia-keyring
1. Remove the second line from /etc/apt/sources.list
    deb http://www.deb-multimedia.org wheezy main non-free
1. Run apt-get source ffmpeg-dmo
1. You should now have a folder called ffmpeg-dmo-0.11 <-- The version will change as time goes by.
1. Change the directory to the folder containing the source. e.g. cd ffmpeg-dmo-0.11
1. Run ./configure to setup the source.
1. Run make && make install to compile and install ffmpeg
1. if you are not running as root like I am, then you will need to run the above command with sudo


BENS NOTE: Do ./configure --enable-libmp3lame to add mp3 encoding suppork

Install pydub
https://github.com/jiaaro/pydub/

``` bash
sudo pip install pydub
```


################## Debugging Wifi ##############

NetworkManager - Wifi network manager
wpa_supplicant - implements key negotiation and controls roaming

network manager farms out to wpa_supplicant

the wpa_supplicant package provides the wpa-* options for /etc/network/interfaces.  If they are used wpa_supplicant is started in the background
https://wiki.debian.org/WiFi/HowToUse#wpa_supplicant

``` bash
dmesg | grep wlan0
cat /var/log/messages | grep wlan0
cat /var/log/deamon.log | grep wlan0
sudo wpa_supplicant -c /etc/wpa_supplicant/wpa_supplicant.conf -i wlan0 -d
```

http://manpages.ubuntu.com/manpages/lucid/en/man5/interfaces.5.html
http://www.freebsd.org/cgi/man.cgi?wpa_supplicant.conf(5)

################## Wifi Files before going to WICD again ##############

/etc/network/interfaces
``` 
auto lo

iface lo inet loopback

iface default inet dhcp

allow-hotplug wlan0
auto wlan0
iface wlan0 inet manual
wpa-roam /etc/wpa_supplicant/wpa_supplicantsupplicant.conf

iface ben-home inet static
address 192.168.0.91
netmask 255.255.255.0
gateway 192.168.0.1

iface ben-home-fallback inet staticatic
address 192.168.0.91
netmask 255.255.255.0
gateway 192.168.0.1
```


/etc/wpa_supplicant/wpa_supplicant.conf
``` 
ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1

network={
ssid="GBZ2_4_BR"
priority=2012psk="gbz80211bgn"
proto=WPA2
key_mgmt=WPA-PSK
pairwise=TKIP
group=TKIP
id_str="ben-home"
}

network={
ssid="GBZ2_4"
priority=1
psk="ssidgbz80211bgn"
proto=WPA
key_mgmt=WPA-PSK
pairwise=TKIP
group=TKIP
ind_str="ben-home-fallback"
}
```

################## BACK TO WICD...  ##############
After alot of hacking around with the configuration files I finally
ended up going back to WICD.  My best guess is that last time I attempted
to use it I didn't remove the entries from /etc/network/interfaces.  Here's
what my /etc/network/interfaces looks like now

/etc/network/interfaces
```
auto lo

iface lo inet loopback

iface default inet dhcp

auto wlan0
```

With my two wireless networks configured in WICD I verified that I
can kill the stronger network and have it fallback to the weaker one.

The main limitation here is that I can't prioritize the enabled networks
other than due to their relative strengths.  I think getting it to work
that way will require some further research into the network
management on the RPi (I could get this to work manually running
wpa_supplicant with the last configuration and the debug command from above)


############# SETTING UP THE TUNNEL #################
Create an ssh key on the pi and copy it to the server

http://www.tunnelsup.com/raspberry-pi-phoning-home-using-a-reverse-remote-ssh-tunnel

``` bash
ssh-keygen -t rsa
scp id_rsa.pub <user>@<yourhost>:~/.ssh/authorized_keys
```


Disable password authentication by setting PasswordAuthentication to no in
/etc/ssh/sshd_config and then restart

``` bash
sudo reload ssh
```


Install upstart and autossh

``` bash
sudo apt-get install upstart
sudo apt-get install autossh
```

Add the following to /etc/init/ssh_tunnel.conf so upstart will manage the tunnel

/etc/init/ssh_tunnel.conf
``` bash
description "SSH Tunnel"

start on (net-device-up IFACE=wlan0)
stop on runlevel[016]

respawn

env DISPLAY=:0.0

exec autossh -nNT -o ServerAliveInterval=15 -R 0.0.0.0:9999:localhost:22 tunnel@tunnel.zittlau.ca -i /home/pi/.ssh/id_rsa
```


Manually connect to verify the ssh fingerprint, otherwise the upstart job will fail
``` bash
pi@raspberrypi ~ $ sudo -u root autossh -nNT -o ServerAliveInterval=15 -R 9999:localhost:22 tunnel@54.191.9.88 -i /home/pi/.ssh/id_rsa
```


Had to make this change to open up to external connections directly:
http://superuser.com/questions/588591/how-to-make-ssh-tunnel-open-to-public


################# SOUND CLOUD SETUP ####################

Install the python sdk
``` bash
sudo pip install soundcloud
```
