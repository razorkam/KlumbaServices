#!/usr/bin/env bash

pip install Shapely

systemctl stop klumba_services
rm -f  /etc/systemd/system/klumba_services.service
cp -f ./klumba_services.service /etc/systemd/system/
systemctl start klumba_services
systemctl enable klumba_services
systemctl daemon-reload