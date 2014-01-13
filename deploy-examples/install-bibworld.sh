#!/bin/sh -x

WEBSERVERGROUPS="nginx"
BIBWORLDSRC=`pwd`/../

sudo mkdir -p /usr/local/virtualenvs/bibworld
sudo useradd -r -g $WEBSERVERGROUP -s /bin/false uwsgi
sudo pip install virtualenvwrapper

export WORKON_HOME=/usr/local/virtualenvs/
source /usr/bin/virtualenvwrapper.sh 
mkvirtualenv bibworld
workon bibworld

sudo pip install flask uwsgi

cd /usr/local/virtualenvs/bibworld/
git clone $BIBWORLDSRC

sudo chown uwsgi:nginx /usr/local/virtualenvs/bibworld/ -R
sudo chmod 775 fapuli/fapuliserver.py

sudo mkdir -p /var/log/uwsgi
sudo touch /var/log/uwsgi/bibworld.log

sudo /usr/local/virtualenvs/bibworld/bin/uwsgi -x $BIBWORLDSRC/deploy-examples/uwsgi.xml

tail /var/log/uwsgi/bibworld.log

echo "------- copy now the nginx site config file and reload nginx ---------"
