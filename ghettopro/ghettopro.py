"""Module for a GhettoPro class"""
import usocket
import utime
import machine
import network

from led import LED


def Log(msg):
  """prints a message"""
  print(msg)

class GhettoPro():
  """GhettoPro class.

  This class handles the whole GhettoPro board:
      - Ensures WiFi is working
      - Configures buttons & LEDs
      - Sends HTTP requests.
  """

  MODE_BTN_INTERVAL_MS = 400
  SHUTTER_INTERVAL_MS = 1000
  MAIN_LOOP_SLEEP_INTERVAL_MS = 20

  def __init__(
      self, camera=None, wifi_essid=None, wifi_password=None, trigger_pin=None,
      next_mode_pin=None, prev_mode_pin=None, status_led_pin=None, debug=False):
    """Initializes a GhettoPro instance.

    Args:
      camera(cameras.Camera): an instance of a Camera object.
      wifi_essid(str): the WiFi ESSID.
      wifi_password(str): the WiFi password.
      trigger_pin(int): the pin number for the shutter button.
      next_mode_pin(int): the pin number for the next mode button.
      prev_mode_pin(int): the pin number for the previous mode button.
      status_led_pin(int): the pin number for the status LED.
      debug(bool): Whether to display debug messages.
    """
    self.camera = camera
    self.wifi_essid = wifi_essid
    self.wifi_password = wifi_password
    self.trigger_pin = trigger_pin
    self.next_mode_pin = next_mode_pin
    self.prev_mode_pin = prev_mode_pin
    self.debug = debug

    self._last_shutter = utime.ticks_ms()
    self._last_mode_change = utime.ticks_ms()
    self._next_mode_btn = None
    self._prev_mode_btn = None
    self._status_led = None
    self._trigger_btn = None
    self._wlan = None

  ###################
  # Button management
  ###################

  def _ModeWheelCallback(self, pin):
    """Called when one of the camera mode wheel button is pressed."""
    self.Debug('ModeWheel triggered for pin {0!s}'.format(pin))
    ticks_now = utime.ticks_ms()
    ticks_diff = utime.ticks_diff(ticks_now, self._last_mode_change)
    if ticks_diff > self.MODE_BTN_INTERVAL_MS:
      if str(pin) == 'Pin({0:d})'.format(self.prev_mode_pin):
        self.camera.PrevCameraMode()
      if str(pin) == 'Pin({0:d})'.format(self.next_mode_pin):
        self.camera.NextCameraMode()
      self._last_mode_change = utime.ticks_ms()
      self.camera.UpdateCameraMode()
    else:
      self.Debug('ModeWheel triggered too soon ({0:d})'.format(ticks_diff))

  def _TriggerCallback(self, pin):
    """Called when the board shutter button is pressed."""
    self.Debug('Trigger called for pin {0!s}'.format(pin))
    if str(pin) == 'Pin({0:d})'.format(self.trigger_pin):
      ticks_now = utime.ticks_ms()
      ticks_diff = utime.ticks_diff(ticks_now, self._last_shutter)
      if ticks_diff > self.SHUTTER_INTERVAL_MS:
        Log('Shutter!')
        if self.camera.IsVideoMode():
          # We need to either say 'Start filming' or 'Stop filming'
          self._Get(self.camera.GetToggleShutterUrl())
        else:
          self._Get(self.camera.CAMERA_SHUTTER_ON_URL)
        self._last_shutter = utime.ticks_ms()
      else:
        self.Debug('Shutter too soon ({0:d})'.format(ticks_diff))

  ###################
  # Wifi & Network
  ###################

  def _ESSIDSeen(self):
    """Return wether the required ESSID is seen from the board."""
    scan_result = self._wlan.scan()
    for t in scan_result:
      (ssid, _, _, _, _, _) = t
      if ssid.decode('ascii') == self.wifi_essid:
        self.Debug('ESSID {0} found!'.format(self.wifi_essid))
        return True
    self.Debug('ESSID {0} not found'.format(self.wifi_essid))
    return False

  def _ToStatus(self, i):
    """Converts the wlan object status into a human readable string."""
    return {
        0: 'STAT_IDLE – no connection and no activity',
        1: 'STAT_CONNECTING – connecting in progress',
        2: 'STAT_WRONG_PASSWORD – failed due to incorrect password',
        3: 'STAT_NO_AP_FOUND – failed because no access point replied',
        4: 'STAT_CONNECT_FAIL – failed due to other problems',
        5: 'STAT_GOT_IP – connection successful'
        }[i]

  def _Get(self, path, retries=5):
    """Sends a HTTP GET request"""
    if not (self._wlan and self._wlan.isconnected()):
      Log('Can not sent GET requests while wifi is not connected')
      return
    try:
      socket = usocket.socket()
      socket.connect(usocket.getaddrinfo(self.camera.CAMERA_IP, 80)[0][-1])
      http_query = 'GET {0} HTTP/1.1\r\n'.format(path)
      self.Debug('Sending '+http_query)
      http_query += 'Host: {0}\r\n\r\n'.format(self.camera.CAMERA_IP)
      socket.write(http_query)
      utime.sleep_ms(500)
      socket.close()
    except OSError as e:
      if retries == 0:
        raise e
      else:
        self._Get(path, retries-1)

  ###################
  # Board setup
  ###################

  def _ConfigureBoard(self):
    """Initializes the board."""
    Log('Configuring board')
    if self.status_led_pin:
      self._status_led = LED(self.status_led_pin)
    self._trigger_btn = machine.Pin(self.trigger_pin, machine.Pin.IN)
    self._trigger_btn.irq(
        trigger=machine.Pin.IRQ_FALLING,
        handler=self._TriggerCallback)

    if self.next_mode_pin:
      self._next_mode_btn = machine.Pin(self.next_mode_pin, machine.Pin.IN)
      self._next_mode_btn.irq(
          trigger=machine.Pin.IRQ_FALLING,
          handler=self._ModeWheelCallback)

    if self.prev_mode_pin:
      self._prev_mode_btn = machine.Pin(self.prev_mode_pin, machine.Pin.IN)
      self._prev_mode_btn.irq(
          trigger=machine.Pin.IRQ_FALLING,
          handler=self._ModeWheelCallback)

  def _ConnectWifi(self):
    """Connects the board to the WiFi."""
    Log('Setting up WiFi')
    if not self._wlan:
      self._wlan = network.WLAN(network.STA_IF)
      self._wlan.active(True)
    while not self._ESSIDSeen():
      self.Blink()
      self._wlan.disconnect()
      self._wlan.active(False)
      utime.sleep(1)
      self._wlan.active(True)
    self._wlan.connect(self.wifi_essid, self.wifi_password)
    while not self._wlan.isconnected():
      self.Blink(nb=2)
      self.Debug('Trying to connect with Auth : {0} {1}'.format(
          self.wifi_essid, self.wifi_password))
      while self._wlan.status() == network.STAT_CONNECTING:
        self.Debug('Status: '+self._ToStatus(self._wlan.status()))
        utime.sleep_ms(500)
      self.Debug('Status: '+self._ToStatus(self._wlan.status()))
      utime.sleep(1)
    Log(self._wlan.ifconfig())
    #self._wlan.ifconfig(
    #    # IP, netmask, router, DNS
    #    ('10.5.5.8', '255.255.255.0', '10.5.5.1', '8.8.8.8'))
    self.Debug('Connected to {0}'.format(self.wifi_essid))

  def _ConfigureCamera(self):
    Log('Configuring Camera')
    self.Debug('Tell the camera we are here')
    self._Get(self.camera.CAMERA_CONNECTED_URL)
    self.Debug('Set the camera in mode '+self.camera.GetCameraMode())
    self._Get(self.camera.GetCameraModeUrl())
    self.Debug('Set 4k resolution')
    self._Get(self.camera.CAMERA_4K_RESOLUTION_URL)

  def Blink(self, nb=1):
    """Blink the status led if present."""
    if self._status_led:
      self._status_led.Blink(nb=nb)

  def _Loop(self):
    Log('All done, looping...')
    while True:
      utime.sleep_ms(self.MAIN_LOOP_SLEEP_INTERVAL_MS)

  def Debug(self, msg):
    """Prints a debug message."""
    if self.debug:
      Log('DEBUG '+msg)

  def Main(self):
    """Main method/loop"""
    utime.sleep(1)
    self.Debug('Main starting')
    self._ConfigureBoard()
    self.Blink(nb=2)
    self._ConnectWifi()
    self.Blink(nb=3)
    self._ConfigureCamera()

    self._Loop()
