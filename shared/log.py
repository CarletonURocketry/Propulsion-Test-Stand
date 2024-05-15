"""Class for logging data to a file from a predefined format
"""
from datetime import datetime


class LogFile():
    """Datalogger class
    """
    def __init__(self, config: dict[list], logName: str, logPath: str = "") -> None:
        """Initalizes the data logger and write headers

        Args:
            logName (str): Name of the log file
            logPath (str): Relative to the log file from the main script location
            config (dict): Configuration for the logfile
        """

        self.logPath: str = f"{logPath}{logName}"
        logFile = open(self.logPath, "w")
        self.config = config
        headerStr: str = "time.WriteTime"
        print(self.config.keys())
        for key in self.config.keys():
            print(key)
            #key = config[key].split(".")
            for subkey in self.config[key]:
                header: str = f"{key}.{subkey},"
                headerStr += header
        print(headerStr)
        logFile.write(headerStr)
        logFile.close()
        return

    def updateLog(self, status: dict[dict]) -> None:
        """Updates the log file with the status of the switches

        Args:
            status (dict): dictionary with the current state of the system
        """

        logFile = open(self.logPath, "w")
        dataWrite: str = f"{datetime.now().strftime('%H-%M-%S.%f')[:-3]},"
        for key in self.config.keys():
            for subKey in self.config[key]:
                dataWrite.append(f"{status[key][subKey]},")
            
        self.logfile.write(dataWrite)
        self.logFile.close()
        return

    def readLog(self) -> None:
        self.logFile = open(self.logPath, "r")
        print(self.logFile.read())
        self.logFile.close()
        return

if __name__ == "__main__":
    import tomllib
    import datetime

    config = tomllib.load(open("config.toml", "rb"))
    print(config["data"]["format"])
    log = LogFile(config["data"]["format"], f"{config["log"]["name"]}-test-{datetime.datetime.now().strftime("%y-%m-%d-%H-%M")}.csv", config["log"]["path"])

