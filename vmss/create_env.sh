#! /bin/bash
cd ../../
python3 -m venv env
source env/bin/activate
cd hackathon2021/eventhubscore
pip install wheel
pip install -e .