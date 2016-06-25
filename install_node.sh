#!/bin/sh
# RHUM INSTALLER
# WARNING: This software makes significant changes to the system behavior
# DISCLAIMER: This software is distributed with no warranty.

INSTALL_PATH="$PWD"
CONFIG_PATH="$PWD/conf"
BUILD_PATH="$PWD/build"

# Update Apt
cp $CONFIG_PATH/sources.list /etc/apt/
apt-get update

# Update Kernel
read -p "Update kernel? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        dpkg -i $CONFIG_PATH/kernel/linux-headers-4.2.0*.deb
		dpkg -i $CONFIG_PATH/kernel/linux-image-4.2.0*.deb
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# GUI
read -p "Do you want to setup GUI? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Disabling Mouse ..."
        apt-get install unclutter
        cp $CONFIG_PATH/unclutter /etc/default/
        echo "Configuring Autostart ..."
	cp conf/RHUM.desktop /home/trevor/.config/autostart
	read -p "User: " user
	usermod -a -G dialout $user
	/usr/lib/i386-linux-gnu/lightdm/lightdm-set-defaults --autologin $user # prompt for username

fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

read -p "Setup as daemon? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Configuring daemon (will run in background without GUI) ..."
	cd $CONFIG_PATH
        cp rhum /etc/init.d/
        chmod +x /etc/init.d/rhum
        update-rc.d rhum defaults
        cd $INSTALL_PATH
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting ..."
fi

# GRUB
read -p "Enable fast GRUB? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Updating Custom Grub..."
        cp $CONFIG_PATH/grub /etc/default
        update-grub
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# Network Setup (AP)
read -p "Setup AP network (STABLE)? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Reconfiguring Network Interfaces..."
        apt-get install dnsmasq hostapd -y -qq
	apt-get install firmware-iwlwifi firmware-realtek -y -qq
        cp $CONFIG_PATH/iwlwifi-3160-14.ucode /lib/firmware/iwlwifi
        cp $CONFIG_PATH/rtl8723befw.bin /lib/firmware/rtlwifi
	apt-get install wireless-tools -y -qq
        cp $CONFIG_PATH/interfaces /etc/network/interfaces
	cp $CONFIG_PATH/hostapd.conf /etc/hostapd/
	cp $CONFIG_PATH/dnsmasq.conf /etc/
        cp $CONFIG_PATH/dhclient.conf /etc/dhcp/
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# APT Packages
read -p "Update APT dependencies? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Installing dependencies via mirror ..."
        apt-get upgrade -y -qq
        apt-get install unzip -y -qq
        apt-get install build-essential -y -qq
        apt-get install python-dev -y -qq
        apt-get install cmake -y -qq
        apt-get install python-serial -y -qq
        apt-get install python-pip -y -qq
        apt-get install python-matplotlib -y -qq
        apt-get install libgtk2.0-dev -y -qq
        apt-get install python-numpy -y -qq
        apt-get install arduino arduino-mk -qq
        apt-get install x11-xserver-utils -y -qq
        apt-get install cython -y  -qq
	apt-get install python-flask -y -qq
	apt-get install python-requests -y -qq
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# Pip Packages
read -p "Update Pip modules? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Installing Python modules..."
        pip install -r requirements.txt
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# Done Message
read -p "Installation Complete! Reboot now? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
    echo "Rebooting..."
    reboot
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

