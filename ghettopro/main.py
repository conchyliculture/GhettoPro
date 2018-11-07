"""Main module, called by MicroPython"""
from ghettopro import GhettoPro
from cameras.session import HeroFive

# Edit config here
CAMERA_MODEL = HeroFive()
ESSID = 'GP12345678' # Wifi name
PWD = 'cul120345' # Wifi Password
SHUTTER_PIN = 4 # The pin number for the shutter switch
NEXT_MODE_PIN = None # (Optional) The pin number for the 'Next mode' switch
PREV_MODE_PIN = None # (Optional) The pin number for the 'Previous mode' switch
STATUS_LED_PIN = 2 # (Optional) The pin number for the status LED
DEBUG = True # Whether to display debug messages
# End config

gp = GhettoPro(
    camera=CAMERA_MODEL,
    wifi_essid=ESSID,
    wifi_password=PWD,
    shutter_pin=SHUTTER_PIN,
    next_mode_pin=NEXT_MODE_PIN,
    prev_mode_pin=PREV_MODE_PIN,
    status_led_pin=STATUS_LED_PIN,
    debug=DEBUG)

while True:
  try:
    gp.Main()
  except OSError as e:
    print(e)
