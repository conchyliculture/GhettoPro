# Cheapo GoPro Remote

~~inspired by~~ stolen from [http://euerdesign.de/2015/12/28/ultralowcost-diy-gopro-remote/](http://euerdesign.de/2015/12/28/ultralowcost-diy-gopro-remote/).   

Basically the same thing except I wanted to use MicroPython already installed on the chip's firmware.
And also a code a bit cleaner, easier to extend.

Partlist:

* [LOLIN ESP8266 with integrated battery charging thing](https://www.aliexpress.com/item/WEMOS-D1-mini-Pro-16M-bytes-external-antenna-connector-ESP8266-WIFI-Internet-of-Things-development-board/32724692514.html)
* [LiPo battery](https://www.aliexpress.com/item/2pcs-lot-Lithium-Lipo-Battery-3-7V-300mAh-With-Protective-Board-for-Bluetooth-Speaker-Digital-Products/32613895675.html) (wrong connector, though)
* Some buttons

## Installation

Connect the buttons to the Pins you want on your ESP8266. The "Camera mode" buttons are not mandatory.

```
virtualenv -p /usr/bin/python3 somewhere
cd somwhere
git clone 
```

Look at your camera's manual about how to setup wifi, and get the ESSID and password. Write those in `main.py`
Also use your camera model (currently only Hero Session 5 supported).

```
source bin/activate
pip install rshell
rshell --port /dev/ttyUSB0 rsync -m  goprowifi /pyboard
```

And voila!

## Usage

Once your camera is ready for WiFi connections, power up your ESP8266, either from USB or from the battery. Wait for a bit
and your camera should beep, which says GhettoPro was able to connect successfully.

Be careful not to change the mode of your camera into something else (ie: Video mode), otherwise GhettoPro will be confused.

Press the shutter button to take a picture!
