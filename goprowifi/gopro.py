"""Main loop"""
import usocket
import utime
import machine
import network


class LED():
  """Class for a LED"""

  def __init__(self, pin):
    self.led = machine.Pin(pin, machine.Pin.OUT)
    self.value = False

  def Toggle(self):
    """Toggles LED state"""
    self.value = not self.value
    self.led.value(self.value)

  def Blink(self):
    """Blinks LED"""
    self.led.value(1)
    utime.sleep_us(100)
    self.led.value(0)


class GoPro():
  """Main woker class"""

  GOPRO_IP = '10.5.5.9'

  SHUTTER_INTERVAL_MS = 1000
  SLEEP_INTERVAL_MS = 20

  def __init__(self, wifi_essid=None, wifi_password=None, trigger_pin=None):
    self.wifi_essid = wifi_essid
    self.wifi_password = wifi_password
    self.trigger_pin = trigger_pin

    self.status_led = None
    self._trigger_btn = None
    self.wlan = None
    self._socket = None
    self._last_shutter = utime.ticks_ms()

  def _TriggerCallback(self, pin):
    self.Debug('Trigger called for pin {0!s}'.format(pin))
    if str(pin) == 'Pin({0:d})'.format(self.trigger_pin):
      ticks_now = utime.ticks_ms()
      ticks_diff = utime.ticks_diff(ticks_now, self._last_shutter)
      if ticks_diff > self.SHUTTER_INTERVAL_MS:
        self._Shutter()
      else:
        self.Debug('Shutter too soon ({0:d})'.format(ticks_diff))

  def _ConfigureBoard(self):
    self.Log('Configuring board')
    self.status_led = LED(15)
    self._trigger_btn = machine.Pin(self.trigger_pin, machine.Pin.IN)
    self._trigger_btn.irq(
        trigger=machine.Pin.IRQ_FALLING,
        handler=self._TriggerCallback)

  def _ESSIDSeen(self):
    scan_result = self.wlan.scan()
    for t in scan_result:
      (ssid, _, _, _, _, _) = t
      if ssid.decode('ascii') == self.wifi_essid:
        self.Debug('Found essid {0}'.format(ssid))
        return True
    return False

  def _ToStatus(self, i):
    return {
        0: 'STAT_IDLE – no connection and no activity',
        1: 'STAT_CONNECTING – connecting in progress',
        2: 'STAT_WRONG_PASSWORD – failed due to incorrect password',
        3: 'STAT_NO_AP_FOUND – failed because no access point replied',
        4: 'STAT_CONNECT_FAIL – failed due to other problems',
        5: 'STAT_GOT_IP – connection successful'
        }[i]

  def _ConnectWifi(self):
    self.Log('Setting up WiFi to GoPro')
    if not self.wlan:
      self.wlan = network.WLAN(network.STA_IF)
      self.wlan.active(True)
    while not self._ESSIDSeen():
      self.Debug('I do not see {0}, sleeping\n\n'.format(self.wifi_essid))
      self.wlan.disconnect()
      self.wlan.active(False)
      utime.sleep(1)
      self.wlan.active(True)
    self.wlan.connect(self.wifi_essid, self.wifi_password)
    while not self.wlan.isconnected():
      self.Debug('Trying to connect with Auth : {0} {1}'.format(
          self.wifi_essid, self.wifi_password))
      while self.wlan.status() == network.STAT_CONNECTING:
        print('Status: '+self._ToStatus(self.wlan.status()))
        utime.sleep_ms(500)
        self.status_led.Blink()
      self.Debug('Status: '+self._ToStatus(self.wlan.status()))
      utime.sleep(1)
    self.wlan.ifconfig(
        # IP, netmask, router, DNS
        ('10.5.5.8', '255.255.255.0', '10.5.5.1', '8.8.8.8'))
    self.Debug('Connected to {0}'.format(self.wifi_essid))

  def _Get(self, path, retries=5):
    """Sends a HTTP GET request"""
    if not (self.wlan and self.wlan.isconnected()):
      self.Debug('Can not sent GET requests while wifi is not connected')
      return
    try:
      socket = usocket.socket()
      socket.connect(usocket.getaddrinfo(self.GOPRO_IP, 80)[0][-1])
      http_query = 'GET {0} HTTP/1.1\r\n'.format(path)
      self.Debug('Sending '+http_query)
      http_query += 'Host: {0}\r\n\r\n'.format(self.GOPRO_IP)
      socket.write(http_query)
      utime.sleep_ms(500)
      socket.close()
    except OSError as e:
      if retries == 0:
        raise e
      else:
        self._Get(path, retries-1)

  # URLs from:
  # https://github.com/KonradIT/goprowifihack/blob/master/HERO5/HERO5-Commands.md
  def _Connected(self):
    self._Get('/gp/gpControl/command/wireless/pair/complete?success=1'
              '&deviceName=DESKTOP')

  def _Shutter(self):
    self.Log('Shutter!')
    self._Get('/gp/gpControl/command/shutter?p=1')
    self._last_shutter = utime.ticks_ms()

  def _SetPhotoMode(self):
    self._Get('/gp/gpControl/command/mode?p=1')

  def _Set4KResolution(self):
    self._Get('/gp/gpControl/setting/2/1')

  def _ConfigureCamera(self):
    self.Log('Configuring Camera : Photo mode & 4k')
    self._Connected()
    self._SetPhotoMode()
    self._Set4KResolution()

  def _Loop(self):
    self.Log('Looping')
    while True:
      utime.sleep_ms(self.SLEEP_INTERVAL_MS)

  def Debug(self, msg):
    """Prints a debug message."""
    self.Log('DEBUG '+msg)

  def Log(self, msg):
    """prints a message"""
    print(msg)

  def Main(self):
    """Main method/loop"""
    utime.sleep(1)
    self.Log('Main starting')
    self._ConfigureBoard()
    self._ConnectWifi()
    self._ConfigureCamera()

    self._Loop()
