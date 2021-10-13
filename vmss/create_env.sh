#! /bin/bash
apt update
apt install python3-pip
apt install python3.8-venv
cd ../../
python3 -m venv env
source env/bin/activate
cd hackathon2021/eventhubscore
pip install wheel
pip install -e .