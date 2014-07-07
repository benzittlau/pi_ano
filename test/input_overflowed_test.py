"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import pyaudio
import yaml
import sys
from time import sleep


# Load in the config file
config = yaml.load(file("../config/settings.yml"))

def delay():
    sleep(0.025)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
RECORD_SECONDS = 5

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)

print("* recording")

frames = []
errorcount = 0

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    try:
        data = stream.read(CHUNK)
        frames.append(data)
        sys.stdout.write('.')
    except IOError, e:
        # dammit. 
        errorcount += 1
        sys.stdout.write('x')

    delay()


print("\n")
print("* done recording")
print("* error count %d"%(errorcount))

stream.stop_stream()
stream.close()
p.terminate()


