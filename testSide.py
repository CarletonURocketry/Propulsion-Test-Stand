import testStand.communication as comm
import testStand.testData as testData
import testStand.IO as IO
import testStand.log as log
import tomllib
from datetime import datetime, UTC
import sys
from typing import Any


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

startTime: float = float(datetime.now(UTC).strftime("%S.%f")) # Start time in seconds with fractional seconds allowed

comm = comm.Server(config.get("server", {}).get("addr", ""), config.get("server", {}).get("port", ""),)

io = IO.Test()

print("Starting Server")

sendData:dict[str, dict[str, Any]] = {}

while True:
    if debug:
        sendData.update(testData.getTestData())
    else:
        sendData.update(io.updateSensorData())
    sendData.update({"time": {"elapsedTime": float(datetime.now(UTC).strftime("%S.%f")) - startTime, "serverTime": datetime.now(UTC).strftime("%S.%f")}}) # Elapsed time since program start in seconds with fractional seconds allowed, Time on the server, as a unix time stamp with fractional seconds allowed
    log.updateLog(sendData)
    data = comm.recieveData(sendData)
    if debug:
        io.updateOutput(testData.getTestData())
    else:
        io.updateOutput(data)
