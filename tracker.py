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
        Event().wait()
        
    def _toggle_button(self):
        if self._tracker_active:
            self._status_ui.status('power-off')
            self._bark_tracker.stop()            
            
            output = "Thanks for using bark tracker! Here's your summary: "
            summary = self._bark_tracker.generate_summary()

            if self._debug:
                print("tracker stopped")
                print(summary)
            else:
                aiy.audio.say(output)
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

def main():
    ButtonListener().start()

if __name__ == '__main__':
    main()
