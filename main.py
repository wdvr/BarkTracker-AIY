#!/usr/bin/env python3

'''
The main file to run. Process that runs indefinitely, and listens for button presses to start or stop the bark tracking.
'''

import aiy.voicehat
import datetime
import time
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
        print("BarkTracker is loaded. Press the button to get started.")
        self._voicehat_ui.status('error')        
        time.sleep(5)
        self._voicehat_ui.status('power-off')
        Event().wait()
        
    def _toggle_button(self):
        print("button pressed")
        if self._tracker_active:
            print("will deactivate")
            self._voicehat_ui.status('power-off')
            self._tracker_active = False
            
            summaries = []
            for service in self._services:
                service.stop()
                summaries.append(service.generate_summary())
            
            aiy.audio.say("Welcome back! Here's your summary of what happened: ")
            print(summaries)
            for summary in filter(None, summaries):
                aiy.audio.say(summary)
        else:
            print("will activate")
            self._voicehat_ui.status('listening')
            self._tracker_active = True
            aiy.audio.say('Starting Barktracker.')
            for service in self._services:
                print(service)
                bg_thread = Thread(target=service.start)
                bg_thread.start()   

def main():
    ButtonListener().run()

if __name__ == '__main__':
    print("Initializing BarkTracker ...")
    main()
