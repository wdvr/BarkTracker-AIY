#!/usr/bin/env python3

'''
The main file to run. Process that runs indefinitely, and listens for button presses to start or stop the bark tracking.
'''

import aiy.voicehat
import datetime
import time
from threading import Thread, Event, Lock

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
        self._debug = settings.DEBUG
        self._services = None
        self._lock = Lock()

    def run(self):
        self._voicehat_ui.status('power-off')
        self._ui_thread.start()

    def _button_listen(self):
        aiy.voicehat.get_button().on_press(self._toggle_button)
        print("BarkTracker is loaded. Press the button to get started.")
        if self._debug:
            self._toggle_button()
        else:
            self._voicehat_ui.status('error')
            time.sleep(10)
            self._voicehat_ui.status('power-off')
        Event().wait()

    def _toggle_button(self):
        if self._tracker_active:
            self._voicehat_ui.status('power-off')
            self._tracker_active = False

            summaries = []
            self._lock.acquire()
            for service in self._services:
                service.stop()
                summaries.append(service.generate_summary())
            self._services = None
            self._lock.release()
            if self._debug:
                print(summaries)
            else:
                aiy.audio.say(
                    "Welcome back! Here's your summary of what happened: ")
                for summary in filter(None, summaries):
                    aiy.audio.say(summary)
        else:
            self._voicehat_ui.status('listening')
            self._tracker_active = True
            if not self._debug:
                aiy.audio.say('Starting Barktracker.')
            time.sleep(2)
            self._lock.acquire()
            self._services = create_services()
            for service in self._services:
                bg_thread = Thread(target=service.start)
                bg_thread.start()
            self._lock.release()


def create_services():
    gmail_sender = Gmailsender(settings.GMAIL_USER,
                               settings.GMAIL_PASSWORD,
                               from_name=settings.FROM_NAME,
                               from_email=settings.FROM_EMAIL,
                               debug=settings.DEBUG)

    bark_tracker = Barksession(gmail_sender=gmail_sender,
                               recipients=settings.RECIPIENTS,
                               use_ai=settings.USE_AI,
                               ai_labels=settings.AI_LABELS,
                               bark_label=settings.BARK_LABEL,
                               ai_graph=settings.AI_GRAPH,
                               ambient_db=settings.AMBIENT_DB,
                               debug=settings.DEBUG)

    sonos_service = Sonosservice(debug=settings.DEBUG)

    lifx_service = Lifxservice(debug=settings.DEBUG)

    return [bark_tracker, sonos_service, lifx_service]


def main():
    ButtonListener().run()


if __name__ == '__main__':
    print("Initializing BarkTracker ...")
    main()
