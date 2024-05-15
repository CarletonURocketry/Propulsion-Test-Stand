def pressureConversion(x):

  minVoltage = 1
  maxVoltage = 5

  minPressure = 0
  maxPressure = 1000

  voltage = x * (6.144/(32768 >> 4))

  raw = (voltage - minVoltage) * (maxPressure - minPressure) // (maxVoltage - minVoltage) + minPressure

  corrected = raw #insert calibration code here
  return corrected

class RTC():
    """Class to interface with the RTC module
    """
    def __init__(self) -> None:
        return

    def get_time(self) -> str:
        return "12:00:00"

    def set_time(self, time: str) -> None:
        return