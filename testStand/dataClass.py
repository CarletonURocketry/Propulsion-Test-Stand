"""This module contains the data class for the testStand module."""
from pydantic import BaseModel
import json

class timeData(BaseModel):
    """This class contains the time data for the testStand module."""
    elapsedTime: float = float()
    currentTime: float = float()
    writeTime: float = float()

    def load(self, data: dict[str, float]) -> None:
        """This method deserializes the data for the testStand module."""
        self.elapsedTime = data["elapsedTime"]
        self.currentTime = data["currentTime"]
        return

class valveData(BaseModel):
    """This class contains the valve data for the testStand module."""
    xv1: bool = bool()
    xv2: bool = bool()
    xv3: bool = bool()
    xv4: bool = bool()
    xv5: bool = bool()
    xv6: bool = bool()

    def load(self, data: dict[str, bool]) -> None:
        """This method deserializes the data for the testStand module."""
        self.xv1 = data["xv1"]
        self.xv2 = data["xv2"]
        self.xv3 = data["xv3"]
        self.xv4 = data["xv4"]
        self.xv5 = data["xv5"]
        self.xv6 = data["xv6"]
        return

class pressureData(BaseModel):
    """This class contains the pressure data for the testStand module."""
    pi1: float = float()
    pi2: float = float()

    def load(self, data: dict[str, float]) -> None:
        """This method deserializes the data for the testStand module."""
        self.pi1 = data["pi1"]
        self.pi2 = data["pi2"]
        return

class tempData(BaseModel):
    """This class contains the temperature data for the testStand module."""
    t1: float = float()
    t2: float = float()

    def load(self, data: dict[str, float]) -> None:
        """This method deserializes the data for the testStand module."""
        self.t1 = data["t1"]
        self.t2 = data["t2"]
        return

class loadsData(BaseModel):
    """This class contains the load data for the testStand module."""
    tankMass: float = float()
    thrust: float = float()

    def load(self, data: dict[str, float]) -> None:
        """This method deserializes the data for the testStand module."""
        self.tankMass = data["tankMass"]
        self.thrust = data["thrust"]
        return


class testData(BaseModel):
    """This class contains the data for the testStand module."""
    time: timeData = timeData()
    valves: valveData = valveData()
    pressures: pressureData = pressureData()
    temps: tempData = tempData()
    loads: loadsData = loadsData()
    

    def load(self, data: dict[str, dict[str, float | bool]]) -> None:
        """This method deserializes the data for the testStand module."""
        self.time.load(data["time"])
        self.valves.load(data["valves"])
        self.pressures.load(["pressures"])
        self.temps.load(data["temps"])
        self.loads.load(data["loads"])
        return
    
    def clear(self) -> None:
        """This method clears the data for the testStand module."""
        self.time = timeData()
        self.valves = valveData()
        self.pressures = pressureData()
        self.temps = tempData()
        self.loads = loadsData()
        return
    
class data(BaseModel):
    """This class contains the data for the testStand module."""
    type: str = str()
    content: testData = testData()

    def clear(self) -> None:
        """This method clears the data for the testStand module."""
        self.type = str()
        self.content = testData()
        return

    def load(self, data: str) -> None:
        """This method deserializes the data for the testStand module."""
        dataDict = json.loads(data)
        self.type = dataDict.get("type")
        self.content.load(dataDict.get("content"))
        return