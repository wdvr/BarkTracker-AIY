'''
A Barksession monitors for volume peaks and plays audio files as a response.
'''

import datetime

streamChunk = 1024               # chunk used for the audio input stream
sampleRate = 48000               # the sample rate of the user's mic
input_device_index = 0           # device index for the user's mic
numChannels = 2                  # number of channels for the user's mic
# audio_format = pyaudio.paInt16   # the audio format
ambient_db = -4                  # the ambience noise level in db

stricter_timer = 40             # be stricter if re-bark within this # of sec
reward_timer = 15               # reward a silence after this # of seconds
bark_alert = False              # True when barking is ongoing


class Barksession():
    def __init__(self, gmail_user, gmail_password, recipients, debug=False):
        self._gmail_user = gmail_user
        self._gmail_password = gmail_password
        self._recipients = recipients
        self._debug = debug
        
        self._bark_sessions = []

        self._last_bark = datetime.datetime.min
        self._last_email = datetime.datetime.min

        self._session_email_sent = False


        if debug:
            ambient_db = -18
        
    def start(self):
        print("STUB: starting bark tracker")
    
    def stop(self):
        print("STUB: stopping bark tracker")
