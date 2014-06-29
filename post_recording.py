#!/usr/bin/python
import yaml

import sys
import getopt
import os
import datetime
import soundcloud

from pydub import AudioSegment
from pytz import timezone    



def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hpi:s:")
    except getopt.GetoptError:
        print 'post_recording.py -i <input_file> -s <terminating_silence>'
        sys.exit(2)

    # Load in the config file
    config = yaml.load(file("config/settings.yml"))

    # Configure some defaults
    preserve_files = False
    terminating_silence = 0

    # Load in command line options
    for opt, arg in opts:
        if opt == '-h':
            print 'post_recording.py -i <input_file> -s <terminating_silence>'
            sys.exit()
        elif opt in ("-i"):
            input_file = arg
        elif opt in ("-s"):
            terminating_silence = int(arg)
        elif opt in ("-p"):
            preserve_files = True

    # Create the mp3 file
    song = AudioSegment.from_wav(input_file)
    # Slice off the ending tail out
    length_without_silence = (song.duration_seconds - terminating_silence + 1)
    song = song[:(length_without_silence * 1000)]
    # Export the MP3
    basename, ext = os.path.splitext(input_file)
    output_file = basename + '.mp3'
    song.export(output_file, format="mp3")

    # create client soundcloud object with app and user credentials
    client = soundcloud.Client(client_id=config['soundcloud']['client_id'],
            client_secret=config['soundcloud']['client_secret'],
            username=config['soundcloud']['username'],
            password=config['soundcloud']['password'])

    # Get the date for the file name
    local_timezone = timezone(config['soundcloud']['timezone'])
    current_time = datetime.datetime.now(local_timezone)
    formatted_time = current_time.strftime('%l:%M %p %B %d, %Y')
    
    # upload audio file
    track = client.post('/tracks', track={
            'title': 'PiAno Recording - ' + formatted_time,
                'asset_data': open(output_file, 'rb')
                })

    # print track link
    # print track.permalink_url

    if not preserve_files:
        # Clean up the wav
        os.remove(input_file)
        # Clean up the mp3
        os.remove(output_file)


if __name__ == "__main__":
    main(sys.argv[1:])
