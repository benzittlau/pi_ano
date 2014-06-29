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
import time
import datetime

from lib.recorder import Recorder
from subprocess import Popen
from pytz import timezone    

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
                "verbose": False,
                "timezone": "America/Edmonton",
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

        if self.verbose:
            print "Starting PiAno in Verbose Mode"
        else:
            print "Starting PiAno in Normal Mode"

        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()


        self.recorder = Recorder(self.channels, self.rate, self.input_frames_per_block)
        self.recording_filename = None
        self.recording_file = None

    def current_formatted_time(self):
        local_timezone = timezone(self.timezone)
        current_time = datetime.datetime.now(local_timezone)
        formatted_time = current_time.strftime('%l:%M:%S %p %B %d, %Y')

        return formatted_time


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
            print self.current_formatted_time() + ' :: Starting Recording'
            epoch_time = int(time.time())
            self.recording_filename = 'output/output_' + str(epoch_time) + '.wav'
            self.recording_file = self.recorder.open(self.recording_filename, 'wb')

        self.current_state = 'RECORDING'

    def close_recording(self):
        self.current_state = 'POST_RECORDING'

        if self.recording_file is not None:
            print self.current_formatted_time() + ' :: Stopping Recording'
            self.recording_file.close()

            Popen(["python", "post_recording.py", "-i", self.recording_filename, "-s", str(self.terminating_silence_in_seconds)])

            self.recording_file = None
            self.recording_filename = None

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

        if self.verbose:
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

