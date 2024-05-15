"""This module contains utility functions for the test stand and control system
"""

def pressureConversion(x: float, voltageRange: tuple[float,float] = (0, 5), pressureRange: tuple[float,float] = (0, 1000)) -> float:
    """Function to convert pressure from ADC reading to UNITS

    Args:
        x (float): input ADC reading
        voltageRange (tuple[min,max], optional): Tuple containing the voltage range of the ADC. Defaults to (0, 5).
        pressureRange (tuple[min,max], optional): Tuple Containing the pressure range of the sensor. Defaults to (0, 1000).

    Returns:
        float: Pressure Value in UNITS
    """
    voltage: float = x * (6.144/(32768 >> 4))

    raw: float = (voltage - voltageRange[0]) * (pressureRange[1] - pressureRange[0]) // (voltageRange[1] - voltageRange[0]) + pressureRange[0]

    corrected: float = raw #insert calibration code here
    return corrected

class RTC():
    def __init__(self) -> None:
        """Class to interface with the RTC module
        """
        return

    def get_time(self) -> str:
        return "12:00:00"

    def set_time(self, time: str) -> None:
        return