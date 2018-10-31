"""Main module, called by MicroPython"""
import gopro

# Edit config here
ESSID = 'GP12345678'
PWD = 'cul120345'
BTN_PIN = 4

camera = gopro.GoPro(
    wifi_essid=ESSID,
    wifi_password=PWD,
    trigger_pin=BTN_PIN)

camera.Main()
