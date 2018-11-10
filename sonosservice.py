#!/usr/bin/env python3

'''
Starts and stops sonos speakers
'''

import sys
import time
import datetime

from soco import SoCo, discover
from soco.data_structures import DidlItem, to_didl_string

import settings


DUMMY_META = to_didl_string(
    DidlItem(title="DUMMY", parent_id="DUMMY", item_id="DUMMY", desc='DUMMY'))


class Sonosservice():
    def __init__(self, debug=False):
        self._debug = debug
        self._speakers = [SoCo(ip) for ip in settings.SONOS_SPEAKER_IPS]
        self._uri = settings.SONOS_CHANNEL_URI

    def start(self):
        if self._debug:
            print("Turning on the radio - DEBUG")
        else:
            for speaker in self._speakers:
                speaker.play_uri(uri=self._uri, meta=DUMMY_META)

    def stop(self):
        for speaker in self._speakers:
            speaker.pause()

    def generate_summary(self):
        # Not very interesting to show a summary for the sonos service
        return None


if __name__ == '__main__':

    speakers = discover()
    if not speakers:
        print("No speakers found on the network. Ensure your Sonos speakers are turned on and connected to the same network as me, and try again")
        sys.exit(-1)

    for speaker in speakers:
        speaker_ip = speaker.ip_address
        print("Found Sonos device on IP {0}, with name {1}. ".format(
            speaker.ip_address, speaker.player_name))
    first_speaker = next(iter(speakers))
    favorites = first_speaker.music_library.get_sonos_favorites()
    if not favorites:
        "You have no favorites. Either add one or find your URI another way. Exiting."
        sys.exit(-1)

    print("Here's a list of URI's for your favorites:")
    for f in favorites:
        print(f.title + ": " + f.get_uri())

    response = ""
    while response.lower() not in ["y", "yes", "n", "no"]:
        response = input(
            "Play a short sample of your first favorite ({0}) on {1}?".format(
                favorites[0].title,
                first_speaker.player_name))

    if response in ["y", "yes"]:
        first_speaker.play_uri(uri=favorites[0].get_uri(), meta=DUMMY_META)
        time.sleep(5)
        first_speaker.pause()
