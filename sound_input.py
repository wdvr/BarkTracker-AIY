#!/usr/bin/env python3

'''
Barktracker helper class
'''

from aiy.voice.audio import AudioFormat, record_file, Recorder

from wavefile import WaveReader
import time
import numpy as np
import logging

streamChunk = 512  # chunk used for the analyzing input stream

def record(filepath, duration):
    try:
        start=time.time()
        record_file(AudioFormat.CD, filename=filepath, wait=lambda: time.sleep(duration), filetype='wav')

    except Exception as e:
        logging.error("Error while recording to file {}: {}".format(filepath, e))

def get_peak_volume(filepath):
    max_volume = 0.0
    try:
        with WaveReader(filepath) as r:
            for data in r.read_iter(size=streamChunk):
                left_channel = data[0]
                volume = np.linalg.norm(left_channel)
                if volume > max_volume:
                    max_volume = volume
    except Exception as e:
        logging.error("could not get peak volume, assuming 0. Exception: ", e)

    return max_volume
