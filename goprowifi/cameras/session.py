"""Module for Session cameras."""


class HeroFive():
  """Class for a HERO5 Session camera."""

  CAMERA_IP = '10.5.5.9'

  MODE_VIDEO = 'VIDEO'
  MODE_PHOTO = 'PHOTO'
  MODE_BURST = 'BURST'
  CAMERA_MODES = [MODE_PHOTO, MODE_BURST, MODE_VIDEO]


  # URLs from:
  # https://github.com/KonradIT/goprowifihack/blob/master/HERO5/HERO5-Commands.md
  CAMERA_CONNECTED_URL = (
      '/gp/gpControl/command/wireless/pair/complete'
      '?success=1&deviceName=DESKTOP')

  CAMERA_SHUTTER_OFF_URL = '/gp/gpControl/command/shutter?p=0'
  CAMERA_SHUTTER_ON_URL = '/gp/gpControl/command/shutter?p=1'

  CAMERA_VIDEO_MODE_URL = '/gp/gpControl/command/mode?p=0'
  # Single photo
  CAMERA_PHOTO_MODE_URL = '/gp/gpControl/command/sub_mode?mode=1&sub_mode=1'
  CAMERA_BURST_MODE_URL = '/gp/gpControl/command/sub_mode?mode=2&sub_mode=0'
  CAMERA_MODES_URL = [
      CAMERA_PHOTO_MODE_URL,
      CAMERA_BURST_MODE_URL,
      CAMERA_VIDEO_MODE_URL,
  ]

  CAMERA_4K_RESOLUTION_URL = '/gp/gpControl/setting/2/1'

  def __init__(self, *args):
    self._current_mode = 0
    self._shutter_on = False

  def PrevCameraMode(self):
    self._current_mode = (self._current_mode + 1)%(self.CAMERA_MODES)

  def NextCameraMode(self):
    self._current_mode = (self._current_mode - 1)%(self.CAMERA_MODES)

  def GetCameraMode(self):
    """Return the name of the current camera mode."""
    return self.CAMERA_MODES[self._current_mode]

  def GetCameraModeUrl(self):
    """Returns the URL to call for the current camera mode."""
    return self.CAMERA_MODES_URL[self._current_mode]

  def IsVideoMode(self):
    """Returns whether the camera is in video mode."""
    return self.CAMERA_MODES[self._current_mode] == self.MODE_VIDEO

  def GetToggleShutterUrl(self):
    """Toggles the internal shutter state, and return the correct URL for
    it.

    Returns:
      str: the corresponding URL.
    """
    url = self.CAMERA_SHUTTER_ON_URL
    if self._shutter_on:
      url = self.CAMERA_SHUTTER_OFF_URL
    self._shutter_on = not self._shutter_on
    return url
