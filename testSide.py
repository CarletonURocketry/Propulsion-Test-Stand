import shared.communication as comm
import shared.testData as testData

comm = comm.Server()
testData = testData.testData()

print("Starting Server")
while True:
    sendData = testData.getTestData()
    data = comm.recieveData(sendData)
