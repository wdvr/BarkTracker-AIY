#!/usr/bin/env python3

'''
A Barksession monitors for volume peaks and plays audio files as a response.
'''

import datetime
import helpers
import soundbox
import gmailsender

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
        
    def start(self):
        print("starting bark tracker")
        self._stop_requested = False
        self._detect()

    
    def stop(self):
        print("stopping bark tracker")
        self._stop_requested = True

        
    def _detect(self):
        while not self._stop_requested:
            helpers.record("/tmp/sound.wav",0.5)
            current_loudness = helpers.get_peak_volume("/tmp/sound.wav")
            
            currentTime = datetime.datetime.now()

            timeDifference = currentTime - self._last_bark

            if current_loudness <= self._ambient_db:
                if self._bark_alert and timeDifference > datetime.timedelta(seconds=self._reward_timer):
                    print("{0}: Bark stopped. Calm again.".format(currentTime.strftime("%H:%M:%S")))
                    if self._session_email_sent:
                        self._gmail_sender.send_email_async("Bark alert lifted.", "All is calm again.", self._recipients)
                    self._bark_sessions[-1][1] = currentTime - datetime.timedelta(seconds=reward_timer)
                    session_email_sent = False

                    soundbox.reward()
                    self._bark_alert = False
                continue

            bark_alert = True

            if(timeDifference > datetime.timedelta(seconds=self._stricter_timer)):
                print("{0}: New bark detected ({1:.2f} dB). Trying the short messages."
                      .format(currentTime.strftime("%H:%M:%S"),current_loudness))     

                self._bark_sessions.append([currentTime, -1])
                soundbox.warn_short()

            else:
                text = "Kelvin is being noisy at " + \
                    currentTime.strftime("%H:%M:%S") + \
                    "\n\nHe is producing a volume of " + \
                    str(current_loudness) + "dB."

                time_since_last_email = currentTime - self._last_email
                time_since_start_bark = currentTime - self._bark_sessions[-1][0]


                if not self._session_email_sent and time_since_start_bark > datetime.timedelta(seconds=20):
                    print("{0}: More then 20 seconds, sending first warning ({1:.2f} dB)."
                      .format(currentTime.strftime("%H:%M:%S"),current_loudness))
                    self._gmail_sender.send_email_async("New persistent bark for longer than 20 seconds.", text, self._recipients)
                    self._last_email = currentTime
                    self._session_email_sent = True

                elif self._session_email_sent and (time_since_last_email > datetime.timedelta(seconds=20)) :
                    print("{0}: consecutive warning. ({1:.2f} dB). Re-sending e-mail."
                      .format(currentTime.strftime("%H:%M:%S"),current_loudness))

                    self._gmail_sender.send_email_async("Still going, persistent bark for longer than 20 seconds.", text, self._recipients)
                    self._last_email = currentTime
                    self._session_email_sent = True
                else:
                    print("{0}: Persistent bark detected ({1:.2f} dB). Trying the long messages."
                        .format(currentTime.strftime("%H:%M:%S"),current_loudness))

                soundbox.warn_long()

            self._last_bark = datetime.datetime.now()
        return self._bark_sessions

    
