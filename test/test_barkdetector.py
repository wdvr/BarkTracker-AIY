#!/usr/bin/env python3

from barkdetector import Barkdetector
import pytest

def test_loudness():
    detector = Barkdetector(None, None, None, 0.2)
    assert detector.is_loud("resources/success.wav") == True, "Expected the analysis of success.wav to be 'loud'."
    assert detector.is_loud("resources/silent.wav") == False, "Expected the analysis of success.wav to be 'loud'."
