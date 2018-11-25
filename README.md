[![Build Status](https://dev.azure.com/ballooninc/barktracker/_apis/build/status/wdvr.BarkTracker-AIY)](https://dev.azure.com/ballooninc/barktracker/_build/latest?definitionId=1)

# BarkTracker-AIY
A monitor for dog barking, to be used with a Google AIY Voice Kit. The script is supposed to run in the background, listening for a button press to start tracking. Voice messages are played when barks are detected, and if a barksession goes on for more than 20 seconds, an e-mail is sent. 

Can be extended with other home automation services. Examples are added for sonos (sonosservice.py - play the radio when leaving - background noise for my dog), and Lifx (lifxservice.py - turn all the lights off when leaving).


## Get started

You will need a Google AIY VoiceKit to get it to work out of the box. Everything is written modularly enough though, so you can easily get some pieces out (no button press, other sound input, output, ...)

1. Install the required packages

```
apt-get install libsdl-mixer1.2
pip3 install -r requirements.txt
```

2. record your own voice, with audio messages to calm the dog down. Divide them in three categories (put them in the resources folder):
- resources/warn_short: dog starts barking for the first time. Motivate him to stop it.
- resources/warn_long: dog bark is persistent (Mor than once in 45 seconds). You might want to be a bit firmer here.
- resources/reward: reward messages if after a bark session there is a 20 seconds silence.

3. fill in settings.py. Details in the file itself.

4. run `python3 ./main.py` to start the tracker. When the loading is finished, the button will blink for a couple of seconds, to indicate it is active. Press the button to start tracking. When tracking is ongoing, the button light is on.

## run at startup

If you want to run the script when the raspberry pi starts up:

```
cp barktracker.service /etc/systemd/system/barktracker.service
sudo chmod 644 /lib/systemd/system/barktracker.service
sudo systemctl daemon-reload
sudo systemctl enable barktracker.service
```

After restart, the script should be running (you should see the blinking light). If not, errors are written to syslog (`/var/log/syslog`)

## Add a new service

A service should have three methods: `start`, `stop`, and `generate_summary`. Start is called when the button is pressed the first time (i.e. leaving the house), and stop on second press (coming back). generate summary should return a string, or None. The summary will be read out loud after disabling the tracker.