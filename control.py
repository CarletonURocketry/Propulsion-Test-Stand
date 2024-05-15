"""Main module for the control side of the system. This module is responsible for starting the UI and the communication with the server.
"""

import shared.IO as IO
import shared.UI as UI
import shared.communication as comm
import tomllib
import datetime
import sys
from PyQt6.QtWidgets import QApplication
import shared.log as log


config = tomllib.load(open("config.toml", "rb"))
comm = comm.Client(config["server"]["addr"], config["server"]["port"])
print(config)
print(config["switch"])
switch = IO.Switch(config["switch"])
log = log.LogFile(config["data"]["format"], f"{config["log"]["name"]}{datetime.datetime.now().strftime("%y-%m-%d-%H-%M")}.csv", config["log"]["path"])

print("Starting UI")

app = QApplication(sys.argv)
ui = UI.MainWindow(comm, config, switch, log)
ui.show()
app.exec()