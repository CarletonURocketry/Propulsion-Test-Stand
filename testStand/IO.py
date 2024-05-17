"""
This module contains the functions and classes to interface with the IO and sensors of the control and test sides of the system
"""


from typing import Any, Callable


try:
    import RPi.GPIO as GPIO # type: ignore
    import cedargrove_nau7802 as NAU7802
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    import board
    import busio
except ImportError:
    print("RPi.GPIO not found, using mock GPIO")
    from testModules import fake_GPIO as GPIO
    #from testModules import fake_nau7802 as NAU7802
    #from testModules import fake_ads1x15 as ADS
    #from testModules.fake_analog_in import AnalogIn
    #from testModules.fake_adafruit_blinka import board
    #from testModules.fake_adafruit_blinka import busio

class Control():
    def __init__(self, inputMap: dict[str, str], ledMap: dict[str, int] | None) -> None:
        """Class to manage the IO of the control side of the system

        Args:
            inputMap (dict): Input ID (xv1) : Pin ID (A.1)
            ledMap (dict): LED ID : Pin ID (On the GPIO multiplexer)
        """
        self.inputMap = inputMap # Input ID (xv1) : Pin ID (A.1)
        self.pinMap: dict[str, str] = dict([(value, key) for key, value in inputMap.items()]) # Pin ID (A.1) : Input ID (xv1)
        self.pinConfig: dict[str, int] = {"A.1": 22, "A.2": 27, "A.3": 17, "A.4": 4, "B.1": 5, "B.2": 11, "B.3": 9, "B.4": 10, "C.1": 26, "C.2": 19, "C.3": 13, "C.4": 6, "D.1": 12, "D.2": 16, "D.3": 20, "D.4": 21}
        self.gpioMap: dict[str, int] = dict() # Input ID (xv1) : Pin Number (22)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for inputID in self.inputMap.keys():
            pinID = self.inputMap[inputID]
            pinNum = self.pinConfig.get(pinID, -1)
            GPIO.setup(pinNum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.gpioMap[inputID] = pinNum # Input ID (xv1) : Pin Number (22)

        return
    
    def updateStatus(self) -> dict[str, bool]:
        inputStatus: dict[str, bool] = dict() # Input ID (xv1) : Status (False)
        for inputID in self.inputMap.keys():
            pinNum: int = self.gpioMap[inputID]
            inputStatus[inputID] = bool(GPIO.input(pinNum))
        
        return inputStatus

    
class Test():
    def __init__(self, outputMap: dict[str, str]) -> None:
        """Class to manage the IO and sensors of the test side of the system

        Args:
            
        """
        self.outputMap = outputMap # Output ID (xv1) : Pin ID (A.1)
        self.pinMap: dict[str, str] = dict([(value, key) for key, value in outputMap.items()]) # Pin ID (A.1) : Switch ID (xv1)
        self.pinConfig: dict[str, int] = {"A.1": 22, "A.2": 27, "A.3": 17, "A.4": 4, "B.1": 5, "B.2": 11, "B.3": 9, "B.4": 10, "C.1": 26, "C.2": 19, "C.3": 13, "C.4": 6, "D.1": 12, "D.2": 16, "D.3": 20, "D.4": 21}
        self.gpioMap: dict[str, int] = dict() # Output ID (xv1) : Pin Number (22)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        #self.strainGauge = NAU7802.NAU7802(board.I2C())
        #self.strainGauge.channel = 1

        #i2c = busio.I2C(board.SCL, board.SDA)
        #ads = ADS.ADS1115(i2c)

        #self.loadCell = AnalogIn(ads, ADS.P0)
        #self.continuity = AnalogIn(ads, ADS.P3)

        self.ignitorFired = False

        #self.sensorLookup: dict[str, Callable[None, None]] = dict()

        for outputID in self.outputMap.keys():
            pinID = self.outputMap[outputID]
            pinNum = self.pinConfig.get(pinID, -1)
            GPIO.setup(pinNum, GPIO.OUT)
            self.gpioMap[outputID] = bool(GPIO.input(pinNum)) # Output ID (xv1) : Pin Number (22)

        return
    
    def updateOutput(self, outputValues: dict[str, str]) -> dict[str, bool]:
        """Function to update the outputs controlling the relays

        Args:
            outputValues (dict[str, bool]): Dictionary containing the output ID and the value to set that output to

        Returns:
            dict[str, bool]: Dictionary containing the output ID and the current state of that output
        """
        outputStatus: dict[str, bool] = dict() # Input ID (xv1) : Status (False)
        for outputID in self.outputMap.keys():
            pinNum: int = self.gpioMap[outputID]
            GPIO.output(pinNum, bool(outputValues.get(outputID, "False")))
            outputStatus[outputID] = bool(outputValues.get(outputID, False))

        return outputStatus
    
    def updateSensorData(self) -> dict[str, dict[str, Any]]:
        """Function to get updated sensor data

        Returns:
            dict: dictionary of the sensor data, each category is a key with a dictionary of the measurents for that category as the value
        """
        sensorData: dict[str, dict[str, Any]] = dict()

        sensorData.update({"loads": {"l1": self.loadCell.value}})
        sensorData.update({"loads": {"l2": self.readStrainGauge()}})


        return sensorData

    def zeroStrainGauge(self):
        """Initiate internal calibration for current channel.Use when scale is started,
        a new channel is selected, or to adjust for measurement drift. Remove weight
        and tare from load cell before executing."""
        print(f"channel {self.strainGauge.channel} calibrate.INTERNAL: {self.strainGauge.calibrate("INTERNAL")}")
        print(f"channel {self.strainGauge.channel} calibrate.OFFSET: {self.strainGauge.calibrate("OFFSET")}")
        print(f"...channel {self.strainGauge.channel} zeroed")

    def readStrainGauge(self, samples: int =2) -> float:
        """Read and average consecutive raw sample values. Return average raw value.

        Args:
            samples (int, optional): Number of samples to average. Defaults to 2.

        Returns:
            float: Averaged raw value
        """
    
        sample_sum = 0
        sample_count = samples
        while sample_count > 0:
            while not self.strainGauge.available():
                pass
            sample_sum = sample_sum + self.strainGauge.read()
        sample_count -= 1
        return float(sample_sum / samples)
    
    def readRTD(self) -> dict[str, float]:
        """Function to read the temperature sensors

        Returns:
            dict[str, float]: Dictionary containing the temperature sensor ID and the current temperature
        """
        tempData: dict[str, float] = dict()
        return tempData
    
    def readThermocouple(self) -> dict[str, float]:
        """Function to read the thermocouples

        Returns:
            dict[str, float]: Dictionary containing the data and the current temperature
        """
        thermocoupleData: dict[str, float] = dict()
        return thermocoupleData
    
    def readPressure(self) -> dict[str, float]:
        """Function to read the pressure sensors

        Returns:
            dict[str, float]: Dictionary containing the pressure sensor ID and the current pressure
        """
        pressureData: dict[str, float] = dict()
        return pressureData
    
    def readLoadCell(self) -> dict[str, float]:
        """Function to read the load cells

        Returns:
            dict[str, float]: Dictionary containing the load cell ID and the current load
        """
        loadCellData: dict[str, float] = dict()
        return loadCellData
    
    def readIgnitor(self) -> bool:
        """Function to get the ignitor status

        Returns:
            bool: Ignitor status
        """
        return self.ignitorFired
    
    def readContinuity(self) -> bool:
        """Function to read the voltage on the continuity circuit

        Returns:
            bool: Continuity status
        """
        return bool(self.continuity.value)
    
    def readStrainGauge(self) -> float:
        """Function to read the strain gauge

        Returns:
            float: Strain Gauge reading
        """
        return 0.0
    

    
