#!/usr/bin/env python3

'''
A Barksession monitors for volume peaks and plays audio files as a response.
'''

import logging
import datetime
import time
from threading import Lock

import datetime_ext
import sound_input
import soundbox
import gmailsender
from barkdetector import Barkdetector

NOISY_EMAIL_CONTENT = "{} is being noisy at {}"
FIRST_OFFENSE_EMAIL_TITLE = "New persistent bark for longer than 20 seconds."
CONSECUTIVE_BARK_EMAIL_TITLE = "Still going, persistent bark for longer than 20 seconds."
CALM_AGAIN_EMAIL_TITLE = "Bark alert lifted."
CALM_AGAIN_EMAIL_CONTENT = "All is calm again."

SUMMARY_BARKED = "Today {} barked {} times, for a total bark time of {}. The longest bark was one of {}."
SUMMARY_NO_BARK = "{} didn't bark at all today, good dog!"

class Barksession():
    def __init__(
            self,
            dog,
            gmail_sender,
            recipients,
            use_ai,
            ai_labels=None,
            bark_label=None,
            ai_graph=None,
            ambient_db=None,
            debug=False):
        self._dog = dog
        self._gmail_sender = gmail_sender
        self._recipients = recipients

        self._use_ai = use_ai
        self._barkdetector = Barkdetector(
            ai_labels, bark_label, ai_graph, ambient_db)

        self._debug = debug
        self._stop_requested = False

        self._bark_sessions = []

        self._last_bark = datetime.datetime.min
        self._last_email = datetime.datetime.min

        self._session_email_sent = False
        # True when barking is ongoing
        self._bark_alert = False                

        # be stricter if re-bark within this # of sec
        self._stricter_timer = 5 if debug else 40
        # reward a silence after this # of seconds
        self._reward_timer = 7 if debug else 15

        self._lock = Lock()

    def start(self):
        self._lock.acquire()
        self._bark_sessions = []
        self._lock.release()

        self._stop_requested = False
        self._last_bark = datetime.datetime.min
        self._last_email = datetime.datetime.min
        self._session_email_sent = False
        self._bark_alert = False

        self._detect()

    def stop(self):
        self._stop_requested = True

    def generate_summary(self):
        self._lock.acquire()
        summary = {session[0]: session[1] - session[0]
                   for session in self._bark_sessions if session[1]}
        self._lock.release()

        if len(summary):
            total_duration = sum(summary.values(), datetime.timedelta(0))
            longest_bark = max(summary.values())
            return SUMMARY_BARKED.format(
                self._dog, len(summary), datetime_ext.timedelta_format(total_duration), datetime_ext.timedelta_format(longest_bark))
        else:
            return SUMMARY_NO_BARK.format(self._dog)

    def _detect(self):
        tmp_file = "/tmp/sound.wav"
        while True:
            sound_input.record(tmp_file, 0.5)
            
            is_bark = self._barkdetector.is_bark(
                tmp_file) if self._use_ai else self._barkdetector.is_loud(tmp_file)

            if self._stop_requested:
                return

            current_time = datetime.datetime.now()
            time_difference = current_time - self._last_bark

            if not is_bark:
                if self._bark_alert and time_difference > datetime.timedelta(
                                            seconds=self._reward_timer):
                    self._became_quiet(current_time)
                continue

            self._bark_alert = True

            if(not len(self._bark_sessions) or time_difference > datetime.timedelta(seconds=self._stricter_timer)):
                self._new_bark_detected(current_time)
            else:
                self._continued_bark_detected(current_time)

            self._last_bark = current_time

    def _became_quiet(self, current_time):
        logging.info("Bark stopped. Calm again.")
        if self._session_email_sent:
            self._gmail_sender.send_email_async(
                CALM_AGAIN_EMAIL_TITLE, CALM_AGAIN_EMAIL_CONTENT, self._recipients)
        self._lock.acquire()
        self._bark_sessions[-1][1] = current_time - \
            datetime.timedelta(seconds=self._reward_timer-1)
        self._lock.release()

        self._session_email_sent = False
        self._bark_alert = False

        soundbox.reward()
        
    def _new_bark_detected(self, current_time):
        logging.info("New bark detected. Trying the short messages.")
        self._lock.acquire()
        self._bark_sessions.append([current_time, None])
        self._lock.release()
        soundbox.warn_short()
        time.sleep(0.5)

    def _continued_bark_detected(self,current_time):
        time_since_last_email = current_time - self._last_email
        self._lock.acquire()
        time_since_start_bark = current_time - \
            self._bark_sessions[-1][0]
        self._lock.release()

        if not self._session_email_sent and time_since_start_bark > datetime.timedelta(
                seconds=20):
            self._first_extended_bark_detected(text)

        elif self._session_email_sent and (time_since_last_email > datetime.timedelta(seconds=20)):
            self._consecutive_extended_bark_detected(text)
        else:
            logging.info(
                "Persistent bark detected. Trying the long messages.")

        soundbox.warn_long()
        time.sleep(0.5)

    def _first_extended_bark_detected(self, current_time):
        logging.info("More then 20 seconds, sending first warning.")
        text = NOISY_EMAIL_CONTENT.format(self._dog, current_time.strftime("%H:%M:%S"))

        self._gmail_sender.send_email_async(
            FIRST_OFFENSE_EMAIL_TITLE, text, self._recipients)
        self._last_email = current_time
        self._session_email_sent = True

    def _consecutive_extended_bark_detected(self, current_time):
        logging.info("consecutive warning. Re-sending e-mail.")
        text = NOISY_EMAIL_CONTENT.format(self._dog, current_time.strftime("%H:%M:%S"))

        self._gmail_sender.send_email_async(
            CONSECUTIVE_BARK_EMAIL_TITLE,
            text,
            self._recipients)
        self._last_email = current_time
        self._session_email_sent = True
