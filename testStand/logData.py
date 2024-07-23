"""Module to read test data from a toml file and return it line by line in the correct format as dictionaries.
"""
import tomllib

class logData:
    def __init__(self) -> None:
        with open("testData.toml", "rb") as file:
            self.fullData = tomllib.load(file)

        self.i = 0
        self.data: list[dict[str, dict[str, str]]] = self.fullData["content"]

    def getTestData(self) -> dict[str, dict[str, str]]:
        sendData: dict[str, dict[str, str]] = self.data[self.i]
        self.i += 1
        if self.i == (len(self.data) - 1):
            self.i = 0
        return sendData
    
if __name__ == "__main__":
    data = logData()
    print(data.getTestData())
    print(data.getTestData())
    print(data.getTestData())