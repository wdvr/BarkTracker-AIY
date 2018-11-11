#!/usr/bin/env python3

'''
A Barksession monitors for volume peaks and plays audio files as a response.
'''

import logging
import datetime
import time
from threading import Lock

import sound_input
import soundbox
import gmailsender
from barkdetector import Barkdetector


class Barksession():
    def __init__(
            self,
            gmail_sender,
            recipients,
            use_ai,
            ai_labels=None,
            bark_label=None,
            ai_graph=None,
            ambient_db=None,
            debug=False):
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
        self._bark_alert = False                # True when barking is ongoing

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
            return "Today we saw {0} bark sessions, for a total bark time of {1}. The longest bark was one of {2}.".format(
                len(summary), timedelta_format(total_duration), timedelta_format(longest_bark))
        else:
            return "No barks at all today, great!"

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
                    
                    logging.info("{0}: Bark stopped. Calm again.".format(
                        current_time.strftime("%H:%M:%S")))
                    if self._session_email_sent:
                        self._gmail_sender.send_email_async(
                            "Bark alert lifted.", "All is calm again.", self._recipients)
                    self._lock.acquire()
                    self._bark_sessions[-1][1] = current_time - \
                        datetime.timedelta(seconds=self._reward_timer)
                    self._lock.release()

                    self._session_email_sent = False

                    soundbox.reward()
                    self._bark_alert = False
                continue

            self._bark_alert = True

            if(not len(self._bark_sessions) or time_difference > datetime.timedelta(seconds=self._stricter_timer)):
                logging.info("{0}: New bark detected. Trying the short messages."
                      .format(current_time.strftime("%H:%M:%S")))
                self._lock.acquire()
                self._bark_sessions.append([current_time, None])
                self._lock.release()
                soundbox.warn_short()
                time.sleep(0.5)
            else:
                text = "Kelvin is being noisy at " + \
                    current_time.strftime("%H:%M:%S")

                time_since_last_email = current_time - self._last_email
                self._lock.acquire()
                time_since_start_bark = current_time - \
                    self._bark_sessions[-1][0]
                self._lock.release()

                if not self._session_email_sent and time_since_start_bark > datetime.timedelta(
                        seconds=20):
                    logging.info("{0}: More then 20 seconds, sending first warning."
                          .format(current_time.strftime("%H:%M:%S")))
                    self._gmail_sender.send_email_async(
                        "New persistent bark for longer than 20 seconds.", text, self._recipients)
                    self._last_email = current_time
                    self._session_email_sent = True

                elif self._session_email_sent and (time_since_last_email > datetime.timedelta(seconds=20)):
                    print("{0}: consecutive warning. Re-sending e-mail."
                          .format(current_time.strftime("%H:%M:%S")))

                    self._gmail_sender.send_email_async(
                        "Still going, persistent bark for longer than 20 seconds.",
                        text,
                        self._recipients)
                    self._last_email = current_time
                    self._session_email_sent = True
                else:
                    logging.info(
                        "{0}: Persistent bark detected. Trying the long messages." .format(
                            current_time.strftime("%H:%M:%S")))

                soundbox.warn_long()
                time.sleep(0.5)

            self._last_bark = datetime.datetime.now()


def timedelta_format(time_delta):
    seconds = int(time_delta.total_seconds())
    periods = [
        ('year', 60 * 60 * 24 * 365),
        ('month', 60 * 60 * 24 * 30),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('minute', 60),
        ('second', 1)
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return " ".join(strings)
