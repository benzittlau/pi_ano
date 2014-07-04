import time
import datetime
import inspect

from pytz import timezone    
from sys import stdout

local_timezone = timezone('America/Edmonton')
log_level_stream = None

def log(string, id = None):
    epoch_time = int(time.time())

    filename = inspect.stack()[1][1]
    line = inspect.stack()[1][2]

    prefix = "%s (%d) :: "%(current_formatted_time(), epoch_time)
    if id is not None:
        prefix += "ID_%d :: "%(id)

    suffix = " :: %s:%d"%(filename, line)

    print "%s%s%s"%(prefix, string, suffix)

def log_levels(log_level_outputs):
    raw_text = "\t".join(log_level_outputs)
    if log_level_stream is None:
        log(raw_text)
    else:
        log_level_stream.write(raw_text + "\n")

def set_log_level_stream(stream):
    global log_level_stream
    log_level_stream = stream
    
def current_formatted_time():
    global local_timezone
    current_time = datetime.datetime.now(local_timezone)
    formatted_time = current_time.strftime('%l:%M:%S %p %B %d, %Y')

    return formatted_time
