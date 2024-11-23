#!/bin/bash

# Start both the application and simulation stacks
docker compose -f docker-compose-app.yml up -d
docker compose -f docker-compose-simulation.yml up -d

echo "All services started. Use 'docker compose down' to stop them."