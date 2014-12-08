# Setup instructions
Install NOOBS raspbian onto the device
Update keyboard layout and locale to be en_US

If you don't see a us option edit
/etc/default/keyboard
instead

############### WiFi INSTRUCTIONS ###############

NOTE: The second time around I just followed the instructions
[here](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-3-network-setup/setting-up-wifi-with-occidentalis) instead of messing around with all of this.

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

NOTE: After doing this trying to setup the V2 I was no longer able to use a USB keyboard with the raspberry pi.  I'm hoping this actually isn't necessary with a Model B+

``` bash
# Update firmware because it is a C-Media 108
sudo apt-get install git-core
sudo wget https://raw.github.com/Hexxeh/rpi-update/master/rpi-update -O /usr/bin/rpi-update
sudo chmod +x /usr/bin/rpi-update
sudo BRANCH=next rpi-update
sudo reboot
```

NOTE: REGARDLESS OF IF YOU DO ABOVE, DO THIS
``` bash
# Update Alsa config https://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/updating-alsa-config

# sudo nano /etc/modprobe.d/alsa-base.conf
# Change
options snd-usb-audio index=-2
# to
options snd-usb-audio index=0
```

``` bash
# Tests  
speaker-test -c2 -D hw:0,0
aplay /usr/share/sounds/alsa/Front_Center.wav
```

############### Python setup ###############

Setup a project directory
```
sudo mkdir /srv/pi_ano
cd /srv/pi_ano
sudo chown /srv/pi_ano
sudo chgrp /srv/pi_ano
```


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

Install pyyaml:
``` bash
sudo pip install pyyaml
```

Install pytz:
``` bash
sudo pip install pytz
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

BENS NOTE: At stop 8 Do ./configure --enable-libmp3lame to add mp3 encoding support

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

################## USED THESE NEWS INSTRUCTIONS ON V2

```
cd /usr/src
git clone git://source.ffmpeg.org/ffmpeg.git
```

Git retrieved the source code I needed to build ffmpeg from scratch, which is next up !
*Note*
If you need sound for ffmpeg, you will need to also install the
```
libasound2-dev package which enables ALSA.

cd ffmpeg
./configure
make && make install
````

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
cd ~/.ssh
ssh-keygen -t rsa
# This is probably oversimplified as you'll need to use a computer which has the
# ssh key to copy to the server

# WARNING: Take care not to overwrite any existing authorized keys and that this
# goes to the tunnel user, not the primary ubuntu user
scp id_rsa.pub <user>@<yourhost>:~/.ssh/authorized_keys
```


Disable password authentication **on the server** by setting PasswordAuthentication to no in
/etc/ssh/sshd_config and then restart

``` bash
sudo reload ssh
```


Install upstart and autossh on the pi

``` bash
sudo apt-get install upstart
sudo apt-get install autossh
```

After that we need to ensure the ssh gateways are all still starting under upstart, or
we'll lose the ability to use the serial cable to communicate with the device.

Here's what the getty ps listing looks like on a raspberry pi before installing upstart
``` bash
pi@raspberrypi /etc/init $ ps aux | grep getty
root      2276  0.0  0.1   3988   812 tty2     Ss+  Dec01   0:00 /sbin/getty 38400 tty2
root      2277  0.0  0.1   3988   812 tty3     Ss+  Dec01   0:00 /sbin/getty 38400 tty3
root      2278  0.0  0.1   3988   812 tty4     Ss+  Dec01   0:00 /sbin/getty 38400 tty4
root      2279  0.0  0.1   3988   812 tty5     Ss+  Dec01   0:00 /sbin/getty 38400 tty5
root      2280  0.0  0.1   3988   812 tty6     Ss+  Dec01   0:00 /sbin/getty 38400 tty6
root      2281  0.0  0.1   2068   732 ?        Ss+  Dec01   0:00 /sbin/getty -L ttyAMA0 115200 vt100
pi        6442  0.0  0.1   3760   744 pts/1    S+   18:27   0:00 grep --color=auto getty
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

You should then be able to connect through the tunnel
``` bash
ruby-2.1.2 ➜  ~  ssh tunnel.zittlau.ca -l pi -p 9999
```

################# SOUND CLOUD SETUP ####################

Install the python sdk

``` bash
sudo pip install --upgrade distribute
```

``` bash
sudo pip install soundcloud
```

################# PYTHON UPSTART TASK ####################

/etc/init/pi_ano.conf
``` bash
start on runlevel [2345]
stop on runlevel [016]

chdir /srv/pi_ano

setgid pi
setuid pi

respawn
exec python /srv/pi_ano/listen.py
```


################### HOW THE TRIGGERS WORK ####################
"start_trigger_time": 2,
"start_trigger_threshold": 0.02,
"start_trigger_percentage": 0.5,


The time defines a rolling window in seconds for which the frames
will be inspected to determine whether a trigger has occurred.

The trigger threshold is the value that is used to evaluate whether
a given frame is "in".  For example, with the value above the rms
of a frame that is above 0.02 counts as "in" for calculating
the start trigger percentage.

The percentage is the number of frames in the defined window that must be above
the threshold to cause a start or stop trigger.


################### DETERMINING DEFAULT SAMPLING RATE FOR A DEVICE ###############
http://www.voxforge.org/home/docs/faq/faq/linux-how-to-determine-your-audio-cards-or-usb-mics-maximum-sampling-rate

This makes a big differences towards avoiding input overflows

Use arecord with a sampling rate higher than you think it supports (in this case 80k)
``` bash
arecord -f cd -D hw:0,0 -c 1 -d 4 -r 80000 test.wav
```

############# SETTING UP MY VIM FILES ##############
Install updated version of ruby using rvm for homesick
This is very slow; an hour plus.
``` bash
\curl -sSL https://get.rvm.io | bash -s stable --ruby
```

Install ruby gems
``` bash
sudo apt-get install rubygems
```

Install homesick
``` bash
gem install homesick --no-ri --no-doc
```

Install the castle
``` bash
homesick clone benzittlau/vim-castle
```

Link the castle
``` bash
homesick link vim-castle
```

Install full vim
``` bash
sudo apt-get install vim
```

This needs more work because my current vim config doesn't work with the version of vim on the pi


############# SETTING UP MY VIM FILES ##############
Implementing our custom API

Install requests
``` bash
sudo pip install requests
```


############## SETTING UP WIFI IN THE WILD ##########
RPi's mac address: 00:0f:13:38:13:52
Mac's mac address: 7c:d1:c3:f6:95:bd

############## USING THE USB TO TTL CABLE ##########
https://learn.adafruit.com/adafruits-raspberry-pi-lesson-5-using-a-console-cable/test-and-configure

Trying to debug why it's not working on the PiAno image, but it does work on the AirPi image.
https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=675569

getty version on PiAno: util-linux 2.20.1
getty version on AirPi: util-linux 2.20.1

NOTE: The reason this wasn't working was that I changed over to upstart and didn't create a
ttyAMA0 getty conf file in /etc/init.  I've added this as a step above, so this shouldn't happen
on new builds.

############## SETTING UP NETGEAR AS ROUTER ##########
Put DDWRT on the router:
 http://burnmytime.com/howto_install_dd-wrt_firmware_on_netgear-wndr3400v2/#comment-3214

login:password
pi:raspberry

############## RUNNING
Setup the settings file
```
cp config/settings.yml.sample config/settings.yml
vi config/settings.yml
```

Create a log directory
```
mkdir output
```
Run
```
cd /srv/pi_ano
python listen.py
```

############## cannot locate cpu MHz in /proc/cpuinfo

Trying out these instructions
https://gist.github.com/rogerallen/0346a1812deda2a380da
```
#Install prerequisite packages:
sudo apt-get build-dep jackd2

#Install the source package:
apt-get source jackd2
```

Got errros.


Next Attempt
```
apt-get update && apt-get install libjack-jackd2-0
```

Now I'm getting the error:
Jack server is not running or cannot be started
```
# Tried installing
sudo apt-get install jack
```

I'm getting values in the log file, so it looks like it's working regardless of this error

############### TUNING MIC GAIN
The mic gain can be tuned using the `alsamixer` command.  Make sure the gain is being increased for the mic capture, not the mic playback.

############## WORKING WITH THE TIKI MIC
The mic defaults into blue "Speech" mode, whereas I would prefer it to default into purple "Natural" mode. Think I'll come back to this issue if I have time.
