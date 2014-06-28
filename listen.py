#!/usr/bin/python

import pyaudio
import yaml


from lib.piano import PiAno

# Load in the config file
config = yaml.load(file("config/settings.yml"))

# STATES
# 'BOOTING'
# 'IDLE'
# 'RECORDING'
# 'POST_RECORDING' 


if __name__ == "__main__":
    tt = PiAno(**config['pi_ano'])

    while True:
        tt.listen()
