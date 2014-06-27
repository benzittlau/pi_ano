#!/usr/bin/python

import pyaudio


from lib.piano import PiAno

# STATES
# 'BOOTING'
# 'IDLE'
# 'RECORDING'
# 'POST_RECORDING' 


if __name__ == "__main__":
    tt = PiAno()

    while True:
        tt.listen()
