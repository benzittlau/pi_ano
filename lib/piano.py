"""
Module for passively triggered music recordings

This module contains a class which has been designed to
handle processing an incoming audio stream and based
on that stream triggering the start and stop of a 
recording.  It currently only supports outputting
that recording to an MP3 file.
"""
import pyaudio
import struct
import math
import audioop
import os

from pydub import AudioSegment
from lib.recorder import Recorder
 
#INITIAL_TRIGGER_THRESHOLD = 0.05
#FORMAT = pyaudio.paInt16 
#CHANNELS = 1
#RATE = 44100  
#INPUT_BLOCK_TIME = 0.05
#INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
## if there is silence longer than this interval, close recording
#TERMINATING_SILENCE_IN_SECONDS = 3
#TERMINATING_SILENCE = TERMINATING_SILENCE_IN_SECONDS/INPUT_BLOCK_TIME


class PiAno(object):
    SHORT_NORMALIZE = (1.0/32768.0)

    def __init__(self, **kwargs):
        property_defaults = {
                "channels": 1,
                "device_index": 1,
                "format": pyaudio.paInt16,
                "rate": 44100,
                "input_block_time": 0.05,
                "trigger_threshold": 0.05,
                "terminating_silence_in_seconds": 3
                }

        for (prop, default) in property_defaults.iteritems():
            setattr(self, prop, kwargs.get(prop, default))

        self.input_frames_per_block = int(self.rate * self.input_block_time)
        self.terminating_silence = self.terminating_silence_in_seconds / self.input_block_time

        self.current_state = 'BOOTING'
        self.noisycount = 0
        self.quietcount = 0 
        self.errorcount = 0
        self.current_state = 'IDLE'

        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()


        self.recorder = Recorder(self.channels, self.rate, self.input_frames_per_block)
        self.recording_filename = None
        self.recording_file = None
        self.recording_index = 0

    def get_rms (self, block):
        return audioop.rms(block, 2) * self.SHORT_NORMALIZE

    def stop(self):
        self.stream.close()

    def open_mic_stream( self ):
        stream = self.pa.open(   format = self.format,
                                 channels = self.channels,
                                 rate = self.rate,
                                 input = True,
                                 input_device_index = self.device_index,
                                 frames_per_buffer = self.input_frames_per_block)

        return stream

    def start_recording(self):
        if self.recording_file is None:
            self.recording_filename = 'output/output_' + str(self.recording_index)
            self.recording_file = self.recorder.open(self.recording_filename + '.wav', 'wb')
            self.recording_index += 1

        self.current_state = 'RECORDING'

    def close_recording(self):
        if self.recording_file is not None:
            self.recording_file.close()

            # Create the mp3 file
            song = AudioSegment.from_wav(self.recording_filename + '.wav')
            # Slice off the ending tail out
            length_without_silence = (song.duration_seconds - self.terminating_silence_in_seconds + 1)
            song = song[:(length_without_silence * 1000)]
            # Export the MP3
            song.export(self.recording_filename + '.mp3', format="mp3")
            # Clean up the wav
            os.remove(self.recording_filename + '.wav')

            self.recording_file = None
            self.recording_filename = None

        self.current_state = 'POST_RECORDING'
        self.current_state = 'IDLE'

    def listen(self):
        try:
            block = self.stream.read(self.input_frames_per_block)
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
            if self.quietcount > self.terminating_silence:
                self.close_recording()

        if self.recording_file is not None:
            self.recording_file.write_frame(block)

