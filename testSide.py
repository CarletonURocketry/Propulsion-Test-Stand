import testStand.communication as comm
import testStand.testData as testData
import testStand.IO as IO
import testStand.log as log
import tomllib
from datetime import datetime, UTC
#from calendar import timegm
import sys
from typing import Any
#import time


if "-debug" in sys.argv:
    print("Debug Mode")
    debug = True
else:
    debug = False

if "-v" in sys.argv:
    print("Verbose Mode")
    verbose = True
else:
    verbose = False


testData = testData.testData()
config = tomllib.load(open("config.toml", "rb"))
log = log.LogFile(config.get("data", {}).get("format"), f"testSide-{config.get("log", {}).get("name")}{datetime.now(UTC).strftime("%y-%m-%d-%H-%M")}.csv", config.get("log", {}).get("path"))

startTime: float = float(datetime.timestamp(datetime.now(UTC))) # Start time in seconds with fractional seconds allowed
print(f"Start Time: {startTime}")

comm = comm.Server(config.get("server", {}).get("addr", ""), config.get("server", {}).get("port", ""),)

io = IO.Test(config.get("relay", {}))

print("Starting Server")

sendData:dict[str, dict[str, Any]] = {}

while True:
    if debug:
        sendData.update(testData.getTestData())
    else:
        sendData.update(io.updateSensorData())
    sendData.update({"time": {"elapsedTime": (datetime.timestamp(datetime.now(UTC)) - startTime), "serverTime": datetime.timestamp(datetime.now(UTC))}}) # Elapsed time since program start in seconds with fractional seconds allowed, Time on the server, as a unix time stamp with fractional seconds allowed
    log.updateLog(sendData)
    data = comm.recieveData(sendData)
    #if debug:
        #io.updateOutput(testData.getTestData().get("switch"))
    #else:
        #io.updateOutput(data)
