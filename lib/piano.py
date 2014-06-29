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
import itertools

from lib.recorder import Recorder
from subprocess import Popen
from pytz import timezone    
from collections import deque

class PiAno(object):
    SHORT_NORMALIZE = (1.0/32768.0)

    def __init__(self, **kwargs):
        property_defaults = {
                "channels": 1,
                "device_index": 1,
                "format": pyaudio.paInt16,
                "rate": 44100,
                "input_frames_per_block": 1024,
                "trigger_threshold": 0.05,
                "start_trigger_time": 3,
                "stop_trigger_time": 7,
                "start_trigger_threshold": 0.04,
                "stop_trigger_threshold": 0.01,
                "stopping_tail_time": 3,
                "verbose": False,
                "verbose_frame_resolution": 1,
                "timezone": "America/Edmonton",
                "terminating_silence_in_seconds": 3
                }

        for (prop, default) in property_defaults.iteritems():
            setattr(self, prop, kwargs.get(prop, default))

        self.input_block_time = float(self.input_frames_per_block) / self.rate

        # Figure out how many frames we'll be using for start and stop triggers
        # against the rolling buffer
        self.start_trigger_frames = int(self.start_trigger_time / self.input_block_time)
        self.stop_trigger_frames = int(self.stop_trigger_time / self.input_block_time)
        self.stopping_trail_frames = int(self.stopping_tail_time / self.input_block_time)
        self.rolling_buffer_frames = max(self.start_trigger_frames, self.stop_trigger_frames)

        self.initialize_rolling_buffer()

        self.terminating_silence = self.terminating_silence_in_seconds / self.input_block_time

        self.current_state = 'BOOTING'
        self.noisycount = 0
        self.quietcount = 0 
        self.errorcount = 0
        self.current_state = 'IDLE'
        self.verbose_frame_count = 0

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

    def get_empty_block(self):
        return ''.join([chr(0) for x in range(self.input_frames_per_block)])

    def initialize_rolling_buffer(self):
        self.rolling_buffer = deque()
        for x in range(self.rolling_buffer_frames):
            self.rolling_buffer.append(self.get_empty_block())


    def get_rms (self, block):
        return audioop.rms(block, 2) * self.SHORT_NORMALIZE

    def get_buffer_rms (self, length=None):
        if length is None:
            length = self.rolling_buffer_frames
            
        flattened_buffer = ''
        for x in xrange(length):
            flattened_buffer += self.rolling_buffer[x]

        return self.get_rms(flattened_buffer)

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
        print self.current_formatted_time() + ' :: Starting Recording'
        self.current_state = 'RECORDING'
        epoch_time = int(time.time())
        self.recording_filename = 'output/output_' + str(epoch_time) + '.wav'
        self.recording_file = self.recorder.open(self.recording_filename, 'wb')

    def close_recording(self):
        self.current_state = 'POST_RECORDING'

        if self.recording_file is not None:
            print self.current_formatted_time() + ' :: Stopping Recording'

            #Handle the stopping_trail frames
            # This loops through the early portion of the buffer
            # appending the defined number of frames to our
            # recording.
            start  = self.stop_trigger_frames - 1
            stop = self.stop_trigger_frames - self.stopping_trail_frames - 1
            for i in xrange(start, stop, -1):
                self.recording_file.write_frame(self.rolling_buffer[i])

            self.recording_file.close()

            #Popen(["python", "post_recording.py", "-i", self.recording_filename, "-s", str(self.terminating_silence_in_seconds)])

            self.recording_file = None
            self.recording_filename = None

        self.current_state = 'IDLE'

    def start_buffer_amplitude(self):
        return self.get_buffer_rms(self.start_trigger_frames)

    def stop_buffer_amplitude(self):
        return self.get_buffer_rms(self.stop_trigger_frames)

    def handle_state_machine(self):
        if self.current_state == 'IDLE':
            if self.start_buffer_amplitude() > self.start_trigger_threshold:
                self.start_recording()
        elif self.current_state == 'RECORDING':
            if self.stop_buffer_amplitude() < self.stop_trigger_threshold:
                self.close_recording()

    def handle_popped_block(self, block):
        if self.current_state == 'RECORDING':
            self.recording_file.write_frame(block)

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

        # Rotate the buffer
        popped_block = self.rolling_buffer.pop()
        self.rolling_buffer.appendleft(block)

        if self.verbose:
            if self.verbose_frame_count > self.verbose_frame_resolution:
                print( '%s\t%.4f\t%.4f\t%.4f'%(self.current_state, amplitude, self.start_buffer_amplitude(), self.stop_buffer_amplitude()) )
                self.verbose_frame_count = 1
            else:
                self.verbose_frame_count += 1


        self.handle_state_machine()
        self.handle_popped_block(popped_block)

