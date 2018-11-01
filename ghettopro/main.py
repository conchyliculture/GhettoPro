"""Main module, called by MicroPython"""
from ghettopro import GhettoPro
from cameras.session import HeroFive

# Edit config here
CAMERA_MODEL = HeroFive()
ESSID = 'GP12345678' # Wifi name
PWD = 'cul120345' # Wifi Password
TRIGGER_PIN = 4 # The pin number for the trigger switch
NEXT_MODE_PIN = None # (Optional) The pin number for the 'Next mode' switch
PREV_MODE_PIN = None # (Optional) The pin number for the 'Previous mode' switch
DEBUG = True # Whether to display debug messages
# End config

gp = GhettoPro(
    camera=CAMERA_MODEL,
    wifi_essid=ESSID,
    wifi_password=PWD,
    trigger_pin=TRIGGER_PIN,
    next_mode_pin=NEXT_MODE_PIN,
    prev_mode_pin=PREV_MODE_PIN,
    debug=DEBUG)

gp.Main()
