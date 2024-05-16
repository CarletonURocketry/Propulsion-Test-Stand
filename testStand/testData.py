"""Module to read test data from a csv file and return it line by line in the correct format as dictionaries.
"""

class testData:
    def __init__(self):
        file = open("testData.csv", newline='', encoding='utf-8-sig')
        lines: list[str] = list()
        for line in file.read().splitlines():
            lines.append(line)

        headers: list[str] = lines[0].split(",")
        splitHeaders: list[list[str]] = list()
        splitLines: list[list[str]] = list()
        self.i = 0
        self.data: list[dict[str, dict[str, str]]] = list()
        for h in range(len(headers)):
            splitHeaders.append(headers[h].split("."))
        print(headers)
        for k in range(1, len(lines)):
            splitLines.append(lines[k].split(","))
            dataLine: dict[str, dict[str, str]] = dict()
            for j in range(len(splitLines[k - 1])):
                item: dict[str, str] = dict()
                item[splitHeaders[j][1]] = splitLines[k - 1][j]
                if splitHeaders[j][0] not in dataLine:
                    dataLine[splitHeaders[j][0]] = {}
                dataLine[splitHeaders[j][0]].update(item)
            self.data.append(dataLine)

    def getTestData(self) -> dict[str, dict[str, str]]:
        sendData: dict[str, dict[str, str]] = self.data[self.i]
        self.i += 1
        if self.i == (len(self.data) - 1):
            self.i = 0
        return sendData
    
if __name__ == "__main__":
    data = testData()
    data.getTestData()