"""
This module contains the functions and classes to interface with the IO and sensors of the control and test sides of the system
"""

from raspi_gpio import GPIO # This is a mock library for the GPIO pins
# import RPi.GPIO as GPIO # This is the actual library for the GPIO pins

class Control():
    """Class to manage the IO of the control side of the system
    """
    def __init__(self, switchMap: dict["switchID": "pinID"]) -> None:
        """_summary_

        Args:
            switchMap (dict): Switch ID (xv1) : Pin ID (A.1)
        """
        self.switchMap: dict = switchMap # Switch ID (xv1) : Pin ID (A.1)
        self.pinMap: dict = dict([(value, key) for key, value in switchMap.items()]) # Pin ID (A.1) : Switch ID (xv1)
        self.switchStatus: dict = dict([(key, False) for key in switchMap.keys()]) # Switch ID (xv1) : Status (False)
        self.pinConfig: dict = {"A.1": 22, "A.2": 27, "A.3": 17, "A.4": 4, "B.1": 5, "B.2": 11, "B.3": 9, "B.4": 10, "C.1": 26, "C.2": 19, "C.3": 13, "C.4": 6, "D.1": 12, "D.2": 16, "D.3": 20, "D.4": 21}

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for switchID in self.switchMap.keys():
            pinID: str = self.switchMap[switchID]
            pinNum: int = self.pinConfig[pinID]
            GPIO.setup(pinNum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.switchMap[switchID] = pinNum # Switch ID (xv1) : Pin Number (22)

        print(self.switchMap)
        return
    
    def updateStatus(self) -> dict["switchID": bool]:
        for switchID in self.switchMap.keys():
            pinNum: int = self.switchMap[switchID]
            self.switchStatus[switchID] = GPIO.input(pinNum)
        
        return self.switchStatus

class LEDs():
    """Class to control the LEDs connected to the GPIO expander
    """
    def __init__(self) -> None:
        """_summary_

        Args:
            
        """

        return
    
class Test():
    """Class to manage the IO and sensors of the test side of the system
    """
    def __init__(self) -> None:
        """_summary_

        Args:
            
        """

        return
    