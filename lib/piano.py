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

from lib.logger import log, log_levels, set_log_level_stream
from lib.recorder import Recorder
from subprocess import Popen
from pytz import timezone    
from collections import deque

class PiAno(object):
    SHORT_NORMALIZE = (1.0/32768.0)

    def __init__(self, **kwargs):
        self.current_state = 'BOOTING'

        property_defaults = {
                "channels": 1,
                "device_index": 1,
                "format": pyaudio.paInt16,
                "rate": 44100,
                "input_frames_per_block": 1024,
                "start_trigger_time": 2,
                "stop_trigger_time": 7,
                "start_trigger_threshold": 0.02,
                "stop_trigger_threshold": 0.005,
                "start_trigger_percentage": 0.5,
                "stop_trigger_percentage": 0.5,
                "log_level_enabled": False,
                "log_level_frame_resolution": 10,
                "log_level_file": None,
                "log_level_file_mode": 'a',
                "timezone": "America/Edmonton"
                }

        for (prop, default) in property_defaults.iteritems():
            setattr(self, prop, kwargs.get(prop, default))

        self.input_block_time = float(self.input_frames_per_block) / self.rate

        # Figure out how many frames we'll be using for start and stop triggers
        # against the rolling buffer
        self.start_trigger_frames = int(self.start_trigger_time / self.input_block_time)
        self.stop_trigger_frames = int(self.stop_trigger_time / self.input_block_time)
        self.rolling_buffer_frames = max(self.start_trigger_frames, self.stop_trigger_frames)

        self.initialize_rolling_buffer()
        self.reset_start_trigger_buffer()
        self.reset_stop_trigger_buffer()

        self.errorcount = 0
        self.log_level_frame_count = 0

        if self.log_level_enabled:
            print "Starting PiAno in With Level Logging Enabled"
            # Set the log level file if provided
            if self.log_level_file is not None:
                set_log_level_stream(open(self.log_level_file, self.log_level_file_mode, 0))
        else:
            print "Starting PiAno in WIth Level Logging Disabled"

        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()

        self.recorder = Recorder(self.channels, self.rate, self.input_frames_per_block)
        self.recording_filename = None
        self.recording_file = None

        self.current_state = 'IDLE'


    def get_empty_block(self):
        return ''.join([chr(0) for x in range(self.input_frames_per_block)])

    def initialize_rolling_buffer(self):
        self.rolling_buffer = deque()
        for x in range(self.rolling_buffer_frames):
            self.rolling_buffer.append(self.get_empty_block())

    def reset_start_trigger_buffer(self):
        self.start_trigger_buffer = deque(maxlen = self.start_trigger_frames)
        for x in range(self.start_trigger_frames):
            self.start_trigger_buffer.append(0)

    def reset_stop_trigger_buffer(self):
        self.stop_trigger_buffer = deque(maxlen = self.stop_trigger_frames)
        for x in range(self.stop_trigger_frames):
            self.stop_trigger_buffer.append(1)


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
        self.current_state = 'RECORDING'
        epoch_time = int(time.time())

        self.recording_time = epoch_time
        self.recording_filename = 'output/output_' + str(epoch_time) + '.wav'
        self.recording_file = self.recorder.open(self.recording_filename, 'wb')

        log("Started Recording", self.recording_time)

    def close_recording(self):
        log("Stopped Recording", self.recording_time)

        self.current_state = 'POST_RECORDING'

        if self.recording_file is not None:

            # This basically makes sure we're not truncating
            # the recording at the end due to the buffering
            # appending the defined number of frames to our
            # recording.  It basically loops backwards through
            # the rolling buffer.
            for x in reversed(self.rolling_buffer):
                self.recording_file.write_frame(x)


            self.recording_file.close()

            Popen(["python", "post_recording.py", "-f", self.recording_filename, "-i", str(self.recording_time) ])

            self.recording_time = None
            self.recording_file = None
            self.recording_filename = None

        self.current_state = 'IDLE'

    def current_start_trigger_percentage(self):
        passing_frames = filter(lambda frame_rms: frame_rms > self.start_trigger_threshold, self.start_trigger_buffer)
        return float(len(passing_frames)) / self.start_trigger_frames

    def current_stop_trigger_percentage(self):
        passing_frames = filter(lambda frame_rms: frame_rms < self.stop_trigger_threshold, self.stop_trigger_buffer)
        return float(len(passing_frames)) / self.stop_trigger_frames


    def handle_state_machine(self):
        if self.current_state == 'IDLE':
            if self.current_start_trigger_percentage() > self.start_trigger_percentage:
                self.reset_stop_trigger_buffer()
                self.start_recording()
        elif self.current_state == 'RECORDING':
            if self.current_stop_trigger_percentage() > self.stop_trigger_percentage:
                self.reset_start_trigger_buffer()
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
            return

        amplitude = self.get_rms( block )

        # Rotate the buffers
        popped_block = self.rolling_buffer.pop()
        self.rolling_buffer.appendleft(block)

        self.start_trigger_buffer.appendleft(amplitude)
        self.stop_trigger_buffer.appendleft(amplitude)

        if self.log_level_enabled:
            if self.log_level_frame_count > self.log_level_frame_resolution:
                log_level_outputs = []
                log_level_outputs.append( "%s"%(self.current_state) )
                log_level_outputs.append( "%.4f"%(amplitude) )
                log_level_outputs.append( "%.4f"%(self.current_start_trigger_percentage()) )
                log_level_outputs.append( "%.4f"%(self.current_stop_trigger_percentage()) )

                if self.current_state == 'RECORDING':
                    log_level_outputs.append( "%d"%(self.recording_time) )

                self.log_level_frame_count = 1
                log_levels(log_level_outputs)
            else:
                self.log_level_frame_count += 1


        self.handle_state_machine()
        self.handle_popped_block(popped_block)

