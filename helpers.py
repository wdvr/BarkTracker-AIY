#!/usr/bin/env python3

'''
Barktracker helper class
'''

import aiy
from wavefile import WaveReader
import time
import numpy as np

streamChunk = 512               # chunk used for the analyzing input stream


def timedelta_format(time_delta):
    seconds = int(time_delta.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    strings=[]
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return " ".join(strings)


def record(filepath, duration):
    recorder = aiy._drivers._recorder.Recorder()
    dumper = aiy.audio._WaveDump(filepath, duration)
    with recorder, dumper:
        recorder.add_processor(dumper)
        while not dumper.is_done():
            time.sleep(0.1)

            
def get_peak_volume(filepath):
    max_volume = 0.0
    with WaveReader(filepath) as r:
        for data in r.read_iter(size=streamChunk):
            left_channel = data[0]
            volume = np.linalg.norm(left_channel)
            if volume > max_volume:
                max_volume = volume
    return max_volume


