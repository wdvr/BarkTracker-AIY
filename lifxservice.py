#!/usr/bin/env python3

'''
Starts and stops lifx lamps
'''

from lifxlan import LifxLAN


class Lifxservice():
    def __init__(self, debug=False):
        self._debug = debug
        self._lifxlan = LifxLAN()

    def start(self):
        # make sure lights are off when leaving
        if self._debug:
            print("turning off the lights - DEBUG")
        else:
            self._lifxlan.set_power_all_lights("off", rapid=True)

    def stop(self):
        # When coming home, I don't really need to turn on all the lights
        return

    def generate_summary(self):
        # Not very interesting to show a summary for the sonos service
        return None


if __name__ == '__main__':
    print("turning lifx lamps on")
    lifxlan.set_power_all_lights("on", rapid=True)
