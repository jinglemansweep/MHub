#!/bin/bash

echo "Resetting RabbitMQ..."
sudo rabbitmqctl stop_app
sudo rabbitmqctl reset
sudo rabbitmqctl start_app

echo "Done."


