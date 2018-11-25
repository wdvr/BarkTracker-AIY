#!/usr/bin/env python3

import time

import pytest
import sound_input
import tempfile
import os
import contextlib
from wavefile import WaveReader


def test_record_200ms():
    filename = tempfile.gettempdir()+"/unittest_record.wav"
    recording_duration = 0.2
    removeFileIfItExists(filename)
    
    sound_input.record(filename, 0.2)
    
    assert os.path.isfile(filename), "Expected recording to be present at {}.".format(filename)

    with WaveReader(filename) as f:
        file_duration = f.frames/f.samplerate
    
    assert file_duration == pytest.approx(recording_duration), "Expected file recording to be of length {}s. It is {}s.".format(recording_duration, file_duration)


def test_peak_volume_for_default_wav():
    default_filename = "resources/success.wav"
    expected_peak_volume = 8.025814
    
    peak_volume = sound_input.get_peak_volume(default_filename)
    
    assert peak_volume == pytest.approx(expected_peak_volume), "Expected peak volume for {} to be {}, but was {}.".format(default_filename, expected_peak_volume, peak_volume)


def removeFileIfItExists(filename):
    with contextlib.suppress(FileNotFoundError):
        os.remove(filename)

    assert os.path.isfile(filename) == False, "Expected file at '{}' to not be there. This is not an issue with the recording library - permissions error?".format(filename)


