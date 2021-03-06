"""Module for LEDs"""

import machine
import utime


class LED():
  """Class for a LED"""

  def __init__(self, pin):
    self.led = machine.Pin(pin, machine.Pin.OUT)
    self.value = False

  def Toggle(self):
    """Toggles LED state"""
    self.value = not self.value
    self.led.value(self.value)

  def Blink(self, nb=1):
    """Blinks LED"""
    i = 0
    while i < nb:
      self.led.value(0)
      utime.sleep_ms(1)
      self.led.value(1)
      utime.sleep_ms(50)
      i += 1
