"""Contains the class to write data to a log TOML file
"""
import datetime
import sys
from testStand import dataClass
import tomli_w

class LogFile():
    def __init__(self, config: dict[str, list[str]], logName: str, logPath: str = "") -> None:
        """Class to write data to a log file

        Args:
            config (dict[list]): Configuration for the logfile
            logName (str): Name of the log file, with toml extension
            logPath (str, optional): Path to the log file relative to the main script location (Directory must exist). Defaults to "".
        """
        if "-v" in sys.argv:
            self.verbose = True
        else:
            self.verbose = False
        if "-debug" in sys.argv:
            self.debug = True
        else:
            self.debug = False
        
        self.logPath: str = f"{logPath}/{logName}"
        dataDict = {"name": f"{logName}", "data": list()}
        with open(self.logPath, "wb") as logFile:
            tomli_w.dump(dataDict, logFile)
        return

    def updateLog(self, status: dataClass.data) -> None:
        """Updates the log file with the status of the system

        Args:
            status (dict[dict]): dictionary with the current state of the system
        """
        status.content.time.writeTime = datetime.datetime.timestamp(datetime.datetime.now(datetime.UTC))
        with open(self.logPath, "wb") as logFile:
            tomli_w.dump(status.model_dump(), logFile)
        return

    def readLog(self) -> None:
        logFile = open(self.logPath, "r")
        print(logFile.read())
        logFile.close()
        return

if __name__ == "__main__":
    import tomllib
    import datetime

    config = tomllib.load(open("config.toml", "rb"))
    log = LogFile(config["data"]["format"], f"{config["log"]["name"]}-test.toml", config["log"]["path"])

    #log.updateLog({
""""time": {
            "elapsedTime": 0.25, #  = 0.25, # Elapsed time in seconds with decimal seconds allowed
            "currentTime": 0.35 # Time on the server, as a unix time stamp with decimal seconds allowed
            },
        "valves": {
            "XV1": True,
            "XV2": True,
            "XV3": True,
            "XV4": True,
            "XV5": True,
            "XV6": True
            },
        "pressures": { # Pressure Readings
            "pi1": 50.2,
            "pi2": 74.2
            },
        "temps": { # Temperature Readings
            "t1": 40.5,
            "t2": 45.2
            },
        "loads": { # Load Cell and strain gauge readings
            "tankMass": 65.4, # Reading from strain gauge
            "thrust": 74 # Reading from load cell
            }
        })"""

