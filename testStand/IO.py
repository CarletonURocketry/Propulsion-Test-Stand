"""
This module contains the functions and classes to interface with the IO and sensors of the control and test sides of the system
"""

from raspi_gpio import GPIO # type: ignore # This is a mock library for the GPIO pins
# import RPi.GPIO as GPIO # This is the actual library for the GPIO pins
from typing import Any
class Control():
    def __init__(self, inputMap: dict[str, str], ledMap: dict[str, int] = {}) -> None:
        """Class to manage the IO of the control side of the system

        Args:
            inputMap (dict): Input ID (xv1) : Pin ID (A.1)
            ledMap (dict): LED ID : Pin ID (On the GPIO multiplexer)
        """
        self.inputMap = inputMap # Switch ID (xv1) : Pin ID (A.1)
        self.pinMap: dict[str, str] = dict([(value, key) for key, value in inputMap.items()]) # Pin ID (A.1) : Switch ID (xv1)
        self.pinConfig: dict[str, int] = {"A.1": 22, "A.2": 27, "A.3": 17, "A.4": 4, "B.1": 5, "B.2": 11, "B.3": 9, "B.4": 10, "C.1": 26, "C.2": 19, "C.3": 13, "C.4": 6, "D.1": 12, "D.2": 16, "D.3": 20, "D.4": 21}
        self.gpioMap: dict[str, int] = dict() # Switch ID (xv1) : Pin Number (22)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for inputID in self.inputMap.keys():
            pinID = self.inputMap[inputID]
            pinNum = self.pinConfig.get(pinID, -1)
            GPIO.setup(pinNum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.gpioMap[inputID] = pinNum # Switch ID (xv1) : Pin Number (22)

        return
    
    def updateStatus(self) -> dict[str, bool]:
        inputStatus: dict[str, bool] = dict() # Input ID (xv1) : Status (False)
        for inputID in self.inputMap.keys():
            pinNum: int = self.gpioMap[inputID]
            inputStatus[inputID] = GPIO.input(pinNum)
        
        return inputStatus

    
class Test():
    def __init__(self) -> None:
        """Class to manage the IO and sensors of the test side of the system

        Args:
            
        """

        return
    
    def updateSensorData(self) -> dict[str, dict[str, Any]]:
        """Function to get updated sensor data

        Returns:
            dict: dictionary of the sensor data, each category is a key with a dictionary of the measurents for that category as the value
        """
        sensorData: dict[str, dict[str, Any]] = dict()
        return sensorData
    
    def updateOutput(self, output: dict[str, dict[str, Any]]) -> dict[str, dict[str, bool]]:
        """Function to update the outputs (relays) of the system.

        Args:
            output (dict): Dictionary of the outputs and the values to set

        Returns:
            dict: Dictionary with the current states of the outputs
        """
        return output