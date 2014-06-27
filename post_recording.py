#!/usr/bin/python

from pydub import AudioSegment
import sys
import getopt
import os

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:s:")
    except getopt.GetoptError:
        print 'post_recording.py -i <input_file> -s <terminating_silence>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'post_recording.py -i <input_file> -s <terminating_silence>'
            sys.exit()
        elif opt in ("-i"):
            input_file = arg
        elif opt in ("-s"):
            terminating_silence = int(arg)

    # Create the mp3 file
    song = AudioSegment.from_wav(input_file)
    # Slice off the ending tail out
    length_without_silence = (song.duration_seconds - terminating_silence + 1)
    song = song[:(length_without_silence * 1000)]
    # Export the MP3
    basename, ext = os.path.splitext(input_file)
    output_file = basename + '.mp3'
    song.export(output_file, format="mp3")
    # Clean up the wav
    os.remove(input_file)


if __name__ == "__main__":
    main(sys.argv[1:])
