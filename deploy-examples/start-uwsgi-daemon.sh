#!/bin/sh
cd ../../
killall -9 uwsgi
sleep 3
sudo -u uwsgi bin/uwsgi  --log-sendfile -x bibworld/deploy-examples/uwsgi.xml
sleep 3
ps aux | grep uwsgi
