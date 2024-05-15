"""Contains the class to write data to a log file
"""
from datetime import datetime


class LogFile():
    def __init__(self, config: dict[list], logName: str, logPath: str = "") -> None:
        """Class to write data to a log file

        Args:
            logName (str): Name of the log file
            logPath (str): Relative to the log file from the main script location
            config (dict): Configuration for the logfile
        """
        self.logPath: str = f"{logPath}{logName}"
        logFile = open(self.logPath, "w")
        self.config = config
        headerStr: str = "time.WriteTime"
        for key in self.config.keys():
            #key = config[key].split(".")
            for subkey in self.config[key]:
                header: str = f",{key}.{subkey}"
                headerStr += header
        print(headerStr)
        logFile.write(headerStr)
        logFile.close()
        return

    def updateLog(self, status: dict[dict]) -> None:
        """Updates the log file with the status of the system

        Args:
            status (dict): dictionary with the current state of the system
        """

        logFile = open(self.logPath, "w")
        dataWrite: str = f"{datetime.now()},"
        for key in self.config.keys():
            for subKey in self.config[key]:
                dataWrite += f",{status.get(key, {}).get(subKey)}"
            
        logFile.write(dataWrite)
        logFile.close()
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
    log = LogFile(config["data"]["format"], f"{config["log"]["name"]}-test-{datetime.datetime.now().strftime("%y-%m-%d-%H-%M")}.csv", config["log"]["path"])

