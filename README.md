# BarkTracker-AIY
A monitor for dog barking, to be used with a Google AIY


## requirements
```
apt-get install libsdl-mixer1.2
pip3 install pygame wavefile
```

## run at startup

```
cp barktracker.service /lib/systemd/system/barktracker.service
sudo chmod 644 /lib/systemd/system/barktracker.service
sudo systemctl daemon-reload
sudo systemctl enable sample.service
```
