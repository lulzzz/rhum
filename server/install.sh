#!/bin/sh
apt-get update
apt-get install mongodb git python-pip apache2 libapache2-mod-wsgi build-essential python-dev -qq -y --fix-missing 
a2enmod wsgi
pip install flask virtualenv pymongo
cp manager/rhum.conf /etc/apache2/sites-available/
a2ensite rhum.conf
a2dissite 000-default.conf

# Update Kernel
read -p "Enter host IP address: ? " ans
echo $ans >> /etc/hosts
service apache2 restart
