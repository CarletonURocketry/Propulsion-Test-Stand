"""Module to read test data from a csv file and return it line by line in the correct format as dictionaries.
"""
import csv

class testData:
    def __init__(self):
        file = open("testData.csv", newline='', encoding='utf-8-sig')
        lines = []
        for line in file.read().splitlines():
            lines.append(line)

        headers = lines[0].split(",")
        self.i = 0
        self.data: list[dict[dict]] = list()
        for h in range(len(headers)):
            headers[h] = headers[h].split(".")
        for k in range(1, len(lines)):
            lines[k] = lines[k].split(",")
            dataLine = {}
            for j in range(len(lines[k])):
                item: dict = {}
                item[headers[j][1]] = lines[k][j]
                if headers[j][0] not in dataLine:
                    dataLine[headers[j][0]] = {}
                dataLine[headers[j][0]].update(item)
            print(dataLine)
            self.data.append(dataLine)

    def getTestData(self):
        sendData = self.data[self.i]
        self.i += 1
        if self.i == (len(self.data) - 1):
            self.i = 0
        print(sendData)
        return sendData
    
if __name__ == "__main__":
    data = testData()
    data.getTestData()