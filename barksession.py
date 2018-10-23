#!/usr/bin/env python3

'''
A Barksession monitors for volume peaks and plays audio files as a response.
'''

import datetime
import sound_input
import soundbox
import gmailsender
from threading import Lock

class Barksession():
    def __init__(self, gmail_sender, recipients, debug=False):
        self._gmail_sender = gmail_sender
        self._recipients = recipients
        self._debug = debug
        
        self._stop_requested = False
        
        self._bark_sessions = []

        self._last_bark = datetime.datetime.min
        self._last_email = datetime.datetime.min

        self._session_email_sent = False
        self._bark_alert = False                # True when barking is ongoing

        self._stricter_timer = 40               # be stricter if re-bark within this # of sec
        self._reward_timer = 15                 # reward a silence after this # of seconds

        self._ambient_db = 0.2 if debug else 1  # the ambience noise level in db
        self._lock = Lock()
        
    def start(self):
        print("starting bark tracker")
        self._bark_sessions = []
        self._stop_requested = False
        self._detect()
    
    def stop(self):
        self._stop_requested = True
        
    def generate_summary(self):
        self._lock.acquire()
        summary = {session[0]: session[1]-session[0] for session in self._bark_sessions if session[1]}
        self._lock.release()

        if len(summary):
            total_duration = sum(summary.values(),datetime.timedelta(0))
            longest_bark = max(summary.values())
            return "Today we saw {0} bark sessions, for a total bark time of {1}. The longest bark was one of {2}.".format(len(summary), timedelta_format(total_duration), timedelta_format(longest_bark))
        else: 
            return "No barks at all today, great!"
    
    def _detect(self):
        while True:
            sound_input.record("/tmp/sound.wav",0.5)
            if self._stop_requested:
                return
            current_loudness = sound_input.get_peak_volume("/tmp/sound.wav")
            
            current_time = datetime.datetime.now()

            time_difference = current_time - self._last_bark
            if self._debug:
                print("current volume %s dB" % current_loudness)
            if current_loudness <= self._ambient_db:
                if self._bark_alert and time_difference > datetime.timedelta(seconds=self._reward_timer):
                    print("{0}: Bark stopped. Calm again.".format(current_time.strftime("%H:%M:%S")))
                    if self._session_email_sent:
                        self._gmail_sender.send_email_async("Bark alert lifted.", "All is calm again.", self._recipients)
                    self._lock.acquire()
                    self._bark_sessions[-1][1] = current_time - datetime.timedelta(seconds=self._reward_timer)
                    self._lock.release()

                    self._session_email_sent = False

                    soundbox.reward()
                    self._bark_alert = False
                continue

            self._bark_alert = True

            if(time_difference > datetime.timedelta(seconds=self._stricter_timer)):
                print("{0}: New bark detected ({1:.2f} dB). Trying the short messages."
                      .format(current_time.strftime("%H:%M:%S"),current_loudness))     
                self._lock.acquire()
                self._bark_sessions.append([current_time, None])
                self._lock.release()
                soundbox.warn_short()
            else:
                text = "Kelvin is being noisy at " + \
                    current_time.strftime("%H:%M:%S") + \
                    "\n\nHe is producing a volume of " + \
                    str(current_loudness) + "dB."

                time_since_last_email = current_time - self._last_email
                self._lock.acquire()
                time_since_start_bark = current_time - self._bark_sessions[-1][0]
                self._lock.release()

                if not self._session_email_sent and time_since_start_bark > datetime.timedelta(seconds=20):
                    print("{0}: More then 20 seconds, sending first warning ({1:.2f} dB)."
                      .format(current_time.strftime("%H:%M:%S"),current_loudness))
                    self._gmail_sender.send_email_async("New persistent bark for longer than 20 seconds.", text, self._recipients)
                    self._last_email = current_time
                    self._session_email_sent = True

                elif self._session_email_sent and (time_since_last_email > datetime.timedelta(seconds=20)) :
                    print("{0}: consecutive warning. ({1:.2f} dB). Re-sending e-mail."
                      .format(current_time.strftime("%H:%M:%S"),current_loudness))

                    self._gmail_sender.send_email_async("Still going, persistent bark for longer than 20 seconds.", text, self._recipients)
                    self._last_email = current_time
                    self._session_email_sent = True
                else:
                    print("{0}: Persistent bark detected ({1:.2f} dB). Trying the long messages."
                        .format(current_time.strftime("%H:%M:%S"),current_loudness))

                soundbox.warn_long()

            self._last_bark = datetime.datetime.now()
      

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