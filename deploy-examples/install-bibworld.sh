#!/bin/sh -x

WEBSERVERGROUP="nginx"
BIBWORLDSRC=`pwd`

mkdir -p /usr/local/virtualenvs/bibworld
useradd -r -g $WEBSERVERGROUP -s /bin/false uwsgi
pip install virtualenvwrapper

export WORKON_HOME=/usr/local/virtualenvs/
source /usr/bin/virtualenvwrapper.sh 
mkvirtualenv bibworld
workon bibworld

pip install flask uwsgi

cd /usr/local/virtualenvs/bibworld/
git clone $BIBWORLDSRC

chown uwsgi:nginx /usr/local/virtualenvs/bibworld/ -R
chmod 775 bibworld/bibworldserver.py

mkdir -p /var/log/uwsgi
touch /var/log/uwsgi/bibworld.log

/usr/local/virtualenvs/bibworld/bin/uwsgi -x $BIBWORLDSRC/deploy-examples/uwsgi.xml

tail /var/log/uwsgi/bibworld.log

echo "------- copy now the nginx site config file and reload nginx ---------"
