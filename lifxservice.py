#!/usr/bin/env python3

'''
Starts and stops lifx lamps
'''

import logging
from lifxlan import LifxLAN
from daytime import Daytime

class Lifxservice():
    def __init__(self, location, debug=False):
        self._debug = debug
        self._lifxlan = LifxLAN()

        self._daytime = Daytime(location)

    def start(self):
        self._lifxlan.set_power_all_lights("off", rapid=False)

    def stop(self):
        # When coming home, turn on the lights if the sun has set
        if self._daytime.dark_outside():
            self._lifxlan.set_power_all_lights("on", rapid=False)            

    def generate_summary(self):
        # Not very interesting to show a summary for the sonos service
        return None
    
if __name__ == '__main__':    
    print("turning lifx lamps on")
    LifxLAN().set_power_all_lights("on", rapid=False)