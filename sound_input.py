#!/usr/bin/env python3

'''
Barktracker helper class
'''

import aiy
from wavefile import WaveReader
import time
import numpy as np

streamChunk = 512  # chunk used for the analyzing input stream


def record(filepath, duration):
    try:
        recorder = aiy._drivers._recorder.Recorder()
        dumper = aiy.audio._WaveDump(filepath, duration)
        with recorder, dumper:
            recorder.add_processor(dumper)
            while not dumper.is_done():
                time.sleep(0.1)
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
