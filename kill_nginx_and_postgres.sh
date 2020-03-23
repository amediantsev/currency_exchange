#!/bin/bash

sudo service postgresql stop
sudo service nginx stop
docker restart postgres
docker restart nginx