#!/usr/bin/env python3

import time

import pytest
import soundbox

def test_sound_libs():
    '''
    Don't test if the sound really played, rather play an empty file and test if no exceptions are thrown and the timing is about right. silent.wav has a duration of exactly 200ms.
    '''
    start_time = time.time()
    soundbox.play_sound("resources/silent.wav")

    duration = time.time() - start_time
    assert duration > 0.19, "Playing the 200ms sound fragment should take at least 200ms, since it is a synchronous call"
    assert duration < 0.50, "Playing the 200ms took more than 500ms."
