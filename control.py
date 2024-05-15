"""Main module for the control side of the system. This module is responsible for starting the UI and the communication with the server.
"""

import testStand.IO as IO
import testStand.UI as UI
import testStand.communication as comm
import tomllib
import datetime
import sys
from PyQt6.QtWidgets import QApplication
import testStand.log as log


config = tomllib.load(open("config.toml", "rb"))
comm = comm.Client(config.get("server", {}).get("addr", ""), config.get("server", {}).get("port", 0))

switch = IO.Switch(config.get("switch", {}))
log = log.LogFile(config.get("data", {}).get("format"), f"control-{config.get("log", {}).get("name")}{datetime.datetime.now().strftime("%y-%m-%d-%H-%M")}.csv", config.get("log", {}).get("path"))

print("Starting UI")

app = QApplication(sys.argv)
ui = UI.MainWindow(comm, config, switch, log)
ui.show()
app.exec()
