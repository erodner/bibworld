#!/bin/sh
cd ../../
killall -9 uwsgi
sleep 3
sudo -u uwsgi bin/uwsgi  -x bibworld/deploy-examples/uwsgi.xml --logto /var/log/uwsgi/details.log
sleep 3
ps aux | grep uwsgi
