#!/usr/bin/env python3

'''
The main file to run. Process that runs indefinitely, and listens for button presses to start or stop the bark tracking.
'''

import aiy.voicehat
import datetime
from threading import Thread, Event

import settings
from barkservice import Barksession
from sonosservice import Sonosservice
from lifxservice import Lifxservice
from gmailsender import Gmailsender

class ButtonListener(object):
    def __init__(self):
        self._voicehat_ui = aiy.voicehat.get_status_ui()
        self._tracker_active = False
        self._ui_thread = Thread(target=self._button_listen)
        
        gmail_sender = Gmailsender(settings.GMAIL_USER, settings.GMAIL_PASSWORD, from_name=settings.FROM_NAME, from_email=settings.FROM_EMAIL, debug=settings.DEBUG)
        bark_tracker = Barksession(gmail_sender, settings.RECIPIENTS, settings.DEBUG)
        sonos_service = Sonosservice(debug=settings.DEBUG)
        lifx_service = Lifxservice(debug=settings.DEBUG)
        self._services= [bark_tracker, sonos_service, lifx_service]

    def run(self):
        self._voicehat_ui.status('power-off')
        self._ui_thread.start()

    def _button_listen(self):
        aiy.voicehat.get_button().on_press(self._toggle_button)
        Event().wait()
        
    def _toggle_button(self):
        if self._tracker_active:
            self._voicehat_ui.status('power-off')
            self._tracker_active = False
            aiy.audio.say("Welcome back! Here's your summary of what happened: ")

            # Let's shut down in the opposite order
            for service in self._services[::-1]:
                service.stop()                        
                aiy.audio.say(service.generate_summary())
            
        else:
            self._voicehat_ui.status('listening')
            self._tracker_active = True
            aiy.audio.say('Starting Barktracker.')
            for service in self._services:
                bg_thread = Thread(target=service.start)
                bg_thread.start()   

def main():
    ButtonListener().run()

if __name__ == '__main__':
    print("Initializing BarkTracker ...")
    main()
