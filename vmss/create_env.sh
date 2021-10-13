#! /bin/bash
sudo apt update
sudo apt install python3-pip
sudo apt install python3-venv
cd ../../
sudo python3 -m venv env
source env/bin/activate
cd hackathon2021/eventhubscore
sudo pip install wheel
sudo pip install -e .