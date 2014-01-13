#!/bin/sh
cd ../../
killall uwsgi
bin/uwsgi  -x fapuli/deploy-examples/uwsgi.xml
sleep 3
ps aux | grep uwsgi
