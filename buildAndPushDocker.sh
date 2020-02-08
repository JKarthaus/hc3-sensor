#!/bin/bash

echo "Build and Push Docker"

git pull

docker build -t $DOCKERHUB_USERNAME/hc3-sensor:latest .

docker login --username $DOCKERHUB_USERNAME --password $DOCKERHUB_PASSWORD

docker push $DOCKERHUB_USERNAME/hc3-sensor:latest


