import testStand.communication as comm
import testStand.testData as testData
import testStand.IO as IO
import testStand.log as log
import tomllib
import datetime
import sys

if "-debug" in sys.argv:
    print("Debug Mode")
    debug = True
else:
    debug = False

comm = comm.Server()
testData = testData.testData()
config = tomllib.load(open("config.toml", "rb"))
log = log.LogFile(config.get("data", {}).get("format"), f"testSide-{config.get("log", {}).get("name")}{datetime.datetime.now().strftime("%y-%m-%d-%H-%M")}.csv", config.get("log", {}).get("path"))

io = IO.Test()

print("Starting Server")

sendData:dict[dict] = {}

while True:
    if debug:
        sendData.update(testData.getTestData())
    else:
        sendData.update(io.updateSensorData())
    log.updateLog(sendData)
    data = comm.recieveData(sendData)
    if debug:
        io.updateOutput(testData.getTestData())
    else:
        io.updateOutput(data)
