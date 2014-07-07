#!/usr/bin/python
import yaml

import sys
import getopt
import os
import datetime
import soundcloud
import requests

from lib.logger import log
from pydub import AudioSegment
from pytz import timezone    

def current_formatted_time(self, current_timezone):
    local_timezone = timezone(current_timezone)
    current_time = datetime.datetime.now(local_timezone)
    formatted_time = current_time.strftime('%l:%M:%S %p %B %d, %Y')

    return formatted_time

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hf:i:")
    except getopt.GetoptError:
        print 'post_recording.py -f <input_file> -i <recording_id>'
        sys.exit(2)

    # Load in command line options
    for opt, arg in opts:
        if opt == '-h':
            print 'post_recording.py -f <input_file> -i <recording_id>'
            sys.exit()
        elif opt in ("-f"):
            input_file = arg
        elif opt in ("-i"):
            recording_id = int(arg)

    # Load in the config file
    config = yaml.load(file("config/settings.yml"))

    # Load the config
    remove_wav_files = config['post_recording']['remove_wav_files']
    remove_mp3_files = config['post_recording']['remove_mp3_files']
    upload_enabled = config['post_recording']['upload_enabled']
    upload_target = config['post_recording']['upload_target']

    # Create the mp3 file
    log("Loading file from path %s"%(input_file), recording_id)
    song = AudioSegment.from_wav(input_file)
    #Find the length
    length = (song.duration_seconds)
    # Export the MP3
    basename, ext = os.path.splitext(input_file)
    output_file = basename + '.mp3'

    log("Exporting to mp3 at path %s"%(output_file), recording_id)
    song.export(output_file, format="mp3")

    # Get the date for the file name
    local_timezone = timezone(config['soundcloud']['timezone'])
    current_time = datetime.datetime.now(local_timezone)
    formatted_time = current_time.strftime('%l:%M %p %B %d, %Y')

    if upload_enabled:
        if upload_target == 'Soundcloud':
            # create client soundcloud object with app and user credentials
            client = soundcloud.Client(client_id=config['soundcloud']['client_id'],
                    client_secret=config['soundcloud']['client_secret'],
                    username=config['soundcloud']['username'],
                    password=config['soundcloud']['password'])
            
            title = 'PiAno Recording - ' + recording_id + ' - ' + formatted_time

            # upload audio file
            log("Attempting to upload to soundcloud with name %s"%(title))
            track = client.post('/tracks', track={
                    'title': title,
                        'asset_data': open(output_file, 'rb')
                        })

            log("Finished attempting to upload to soundcloud")

        if upload_target == 'PiAno':
            url = 'http://pi-ano.herokuapp.com/recording'
            files = {'file': open(output_file, 'rb')}
            data = {'recorded_at': recording_id, 'length': length}

            log("Attempting to upload to pi-ano with id %s and length %d"%(recording_id, length))

            r = requests.post(url, files=files, data=data)
            print r.text

            log("Finished attempting to upload to pi-ano")

    # print track link
    # print track.permalink_url

    if remove_wav_files:
        # Clean up the wav
        log("Removin the wav file at path %s"%(input_file))
        os.remove(input_file)

    if remove_mp3_files:
        # Clean up the mp3
        log("Removin the mp3 file at path %s"%(output_file))
        os.remove(output_file)


if __name__ == "__main__":
    main(sys.argv[1:])
