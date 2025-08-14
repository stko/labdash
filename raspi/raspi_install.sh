
##### To install, follow the instructions in README.md
APPLICATION=labdash
USER=pi

echo "The ${APPLICATION} Installer starts"
cd


mkdir -p ${APPLICATION}
cd ${APPLICATION}

echo update packages
sudo apt-get update --assume-yes
## install some basic packages
sudo apt-get install --assume-yes \
nano \
htop \
net-tools \
network-manager \
python3-pip \
can-utils \
mosquitto-clients # \
#tofrodos \
#hostapd \
#isc-dhcp-server


echo add usb to fstab and mount it
sudo mkdir -p /media/usb
# https://forums.raspberrypi.com/viewtopic.php?t=347609#p2082555
grep -q /dev/sda1 /etc/fstab || cat << 'EOF' | sudo tee --append /etc/fstab
/dev/sda1	/media/usb	auto	defaults,noauto,sync,noatime,x-systemd.automount,x-systemd.idle-timeout=10,users,rw,umask=000	0	0
EOF
sudo systemctl daemon-reload # make systemd aware about new fstab
# sudo mount -a
# if [[ ! -d "/media/usb" ]]
# then
# 	echo "USB Disk couldn't be mounted - Exiting.."
# 	exit 1
# fi



# automatically connect to known hotspots, if around
#wpa_passphrase "${APPLICATION}" "${APPLICATION}${APPLICATION}" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null
#wpa_passphrase "canspy" "canspycanspy" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null


# setting up the systemd services
# very helpful source : http://patrakov.blogspot.de/2011/01/writing-systemd-service-files.html


echo create system services

cat << EOF | sudo tee /etc/systemd/system/${APPLICATION}.service
[Unit]
Description=${APPLICATION} Main Server

[Service]
ExecStart=/home/$USER/init${APPLICATION}.sh final
Restart=on-abort

[Install]
WantedBy=default.target


EOF

# # create the network configuration for can bus
# # this is needed to make the can bus work with systemd-networkd
# # see https://askubuntu.com/a/1376096
cat << EOF | sudo tee /etc/systemd/network/80-can.network
[Match]
Name=can*

[CAN]
BitRate=500K

EOF


cat << EOF | sed 's/<1>/\$1/g' | tee /home/$USER/init${APPLICATION}.sh
#!/bin/bash

if [[ -x "/media/usb/${APPLICATION}/autorun.sh" ]]
then
	/media/usb/${APPLICATION}/autorun.sh <1>
fi
if [[ -f "/media/usb/${APPLICATION}/autorun.py" ]]
then
	cd /media/usb/${APPLICATION}/
	/home/$USER/${APPLICATION}/.venv/bin/python "/media/usb/${APPLICATION}/autorun.py" <1>
fi
cd /home/$USER
/home/$USER/${APPLICATION}/.venv/bin/python "/media/usb/${APPLICATION}/autorun.py" <1>


EOF
chmod a+x /home/$USER/init${APPLICATION}.sh


exit 0


sudo systemctl enable ${APPLICATION} 
sudo systemctl enable systemd-networkd

cat << EOF
as next raspi-config will be started.

Goto "Performance Options" 

Select "Overlay File System" 

Select both "Overlay File System" and "Write protected boot disk"

EOF


read  -n 1 -p "press key to continue" mainmenuinput

sudo raspi-config

cat << EOF
Installation finished

SSH is enabled and the default password for the 'pi' user has not been changed.
This is a security risk - please login as the 'pi' user and type 'passwd' to set a new password."

Also this is the best chance now if you want to do some own modifications,
as with the next reboot the image will be write protected

if done, end this session with
 
     sudo halt

and your ${APPLICATION} all-in-one is ready to use

have fun :-)

the ${APPLICATION} team
EOF

