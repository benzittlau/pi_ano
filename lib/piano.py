import pyaudio
import struct
import math
import audioop
 
INITIAL_TRIGGER_THRESHOLD = 0.05
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100  
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if there is silence longer than this interval, close recording
MAX_IN_RECORDING_SILENCE_IN_SECONDS = 3
MAX_IN_RECORDING_SILENCE = MAX_IN_RECORDING_SILENCE_IN_SECONDS/INPUT_BLOCK_TIME

from lib.recorder import Recorder

class PiAno(object):
    def __init__(self):
        self.current_state = 'BOOTING'
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.trigger_threshold = INITIAL_TRIGGER_THRESHOLD
        self.noisycount = 0
        self.quietcount = 0 
        self.errorcount = 0
        self.current_state = 'IDLE'

        self.recorder = Recorder(CHANNELS, RATE, INPUT_FRAMES_PER_BLOCK)
        self.recording_file = None
        self.recording_index = 0

    def get_rms (self, block):
        return audioop.rms(block, 2) * SHORT_NORMALIZE

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in ["sound", "mic"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def open_mic_stream( self ):
        device_index = self.find_input_device()

        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        return stream

    def start_recording(self):
        if self.recording_file is None:
            filename = 'output/output_' + str(self.recording_index) + '.wav'
            self.recording_file = self.recorder.open(filename, 'wb')
            self.recording_index += 1

        self.current_state = 'RECORDING'

    def close_recording(self):
        if self.recording_file is not None:
            self.recording_file.close()
            self.recording_file = None

        self.current_state = 'POST_RECORDING'
        self.current_state = 'IDLE'

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError, e:
            # dammit. 
            self.errorcount += 1
            print( "(%d) Error recording: %s"%(self.errorcount,e) )
            self.noisycount = 1
            return

        amplitude = self.get_rms( block )

        print( "%s - %.2f"%(self.current_state, amplitude) )

        if amplitude > self.trigger_threshold:
            # noisy block
            self.quietcount = 0
            self.noisycount += 1
            self.start_recording()
        else:            
            # quiet block.
            self.noisycount = 0
            self.quietcount += 1
            if self.quietcount > MAX_IN_RECORDING_SILENCE:
                self.close_recording()

        if self.recording_file is not None:
            self.recording_file.write_frame(block)

