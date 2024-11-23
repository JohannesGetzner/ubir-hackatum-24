#!/bin/bash

docker compose -f docker-compose-app.yml up --build
docker compose -f docker-compose-simulation.yaml pull
docker compose -f docker-compose-simulation.yaml up

echo "All services started. Use 'docker compose down' to stop them."