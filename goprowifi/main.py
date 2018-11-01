"""Main module, called by MicroPython"""
from ghettopro import GhettoPro

# Edit config here
ESSID = 'GP12345678' # Wifi name
PWD = 'cul120345' # Wifi Password
TRIGGER_PIN = 4 # The pin number for the trigger switch
NEXT_MODE_PIN = None # The pin number for the 'Next mode' switch
PREV_MODE_PIN = None # The pin number for the 'Previous mode' switch
# End config

gp = GhettoPro(
    wifi_essid=ESSID,
    wifi_password=PWD,
    trigger_pin=TRIGGER_PIN,
    next_mode_pin=NEXT_MODE_PIN,
    prev_mode_pin=PREV_MODE_PIN)

gp.Main()
