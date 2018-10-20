#!/usr/bin/env python3

'''
The main file to run. Process that runs indefinitely, and listens for button presses to start or stop the bark tracking.
'''

import aiy.voicehat
import datetime
from threading import Thread, Event

import settings
from barksession import Barksession
from gmailsender import Gmailsender

class ButtonListener(object):
    def __init__(self):
        self._status_ui = aiy.voicehat.get_status_ui()
        self._tracker_active = False
        self._ui_thread = Thread(target=self._run_task)
        self._gmail_sender = Gmailsender(settings.GMAIL_USER, settings.GMAIL_PASSWORD, from_name=settings.FROM_NAME, from_email=settings.FROM_EMAIL, debug=settings.DEBUG)
        self._bark_tracker = Barksession(self._gmail_sender, settings.RECIPIENTS, settings.DEBUG)
        self._debug = settings.DEBUG
        self._last_bark_summary = None

    def start(self):
        self._status_ui.status('power-off')
        self._ui_thread.start()

        
    def _run_task(self):
        aiy.voicehat.get_button().on_press(self._toggle_button)
        print("starting")
        Event().wait()
        
        
    def _toggle_button(self):
        if self._tracker_active:
            self._status_ui.status('power-off')
            self._bark_tracker.stop()
            summary = generate_summary(self._bark_tracker.get_sessions())
            if self._debug:
                print("tracker stopped")
                print(summary)
#             else:
                aiy.audio.say(summary)
            self._tracker_active = False
        else:
            self._status_ui.status('listening')
            if self._debug:
                print("starting tracker")
            else:
                aiy.audio.say('Starting Barktracker')
            self._tracker_active = True
            barksession_thread = Thread(target=self._bark_tracker.start)
            barksession_thread.start()
            
            
def generate_summary(bark_sessions):
        output = "Thanks for using bark tracker! Here's your summary: "
        summary = {session[0]: session[1]-session[0] for session in bark_sessions}
        total_duration = sum(summary.values(),datetime.timedelta(0))
        
        output += "Today we saw {0} bark sessions, for a total bark time of {1}. ".format(len(bark_sessions), timedelta_format(total_duration))

        longest_bark = max(summary.values())
        print(longest_bark)
        output += "The longest bark was one of {0}.".format(timedelta_format(longest_bark))
        return output
            
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


def main():
    ButtonListener().start()

    
if __name__ == '__main__':
    main()
