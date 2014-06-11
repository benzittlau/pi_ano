from recorder import Recorder
from time import sleep

RATE = 44100  
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)

recorder = Recorder(2, RATE, INPUT_FRAMES_PER_BLOCK)
recording_file = recorder.open('output/output.wav', 'wb')

recording_file.start_recording()
sleep(7)
recording_file.stop_recording()
