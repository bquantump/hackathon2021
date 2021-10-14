import os
import subprocess
subprocess.check_call("cd gr-eventhubs && rm -rf build; mkdir build; cd build; cmake ..; make -j; sudo make install", shell=True)
subprocess.check_call("cd eventhubscore && pip3 install -e .", shell=True)
subprocess.check_call("cd dsp; pip3 install -e .", shell=True)
rez = subprocess.check_output("hostname", shell=True)
rez = rez.decode('utf-8').strip()

subprocess.check_call('python3 launch.py ' + rez, shell=True)