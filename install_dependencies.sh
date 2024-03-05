#!/bin/bash

# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install -y python3 python3-pip

# Install Flask and Flask-CORS using pip
pip3 install flask
pip3 install flask-cors