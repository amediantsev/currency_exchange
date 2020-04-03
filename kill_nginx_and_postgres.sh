#!/bin/bash

sudo service postgresql stop
sudo service nginx stop
docker-compose restart postgres nginx
