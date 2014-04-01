#!/bin/sh
cd ../../
sudo -u uwsgi bin/uwsgi  --log-sendfile 1 -x bibworld/deploy-examples/uwsgi-standalone.xml --show-config
