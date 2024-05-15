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
        """Class to interface with the RTC module on the Raspberry Pis HAT
        """
        return

    def get_time(self) -> float:
        """Function to get the current time from the RTC

        Returns:
            float: Current time as a unix timestamp with decimal seconds
        """
        return 0

    def set_time(self, time: float) -> None:
        """Function to update the time on the RTC

        Args:
            time (float): Time to set the RTC to as a unix timestamp with decimal seconds
        """
        return