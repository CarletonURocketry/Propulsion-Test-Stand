import testStand.communication as comm
import testStand.testData as testData
import testStand.IO as IO
import testStand.log as log
import tomllib
import datetime

comm = comm.Server()
testData = testData.testData()
config = tomllib.load(open("config.toml", "rb"))
log = log.LogFile(config.get("data", {}).get("format"), f"control-{config.get("log", {}).get("name")}{datetime.datetime.now().strftime("%y-%m-%d-%H-%M")}.csv", config.get("log", {}).get("path"))

io = IO.Test()

print("Starting Server")
while True:
    io.getSensors()
    sendData = testData.getTestData()
    log.writeData(sendData)
    data = comm.recieveData(sendData)
    io.update(data)
