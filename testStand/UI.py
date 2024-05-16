import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
import pyqtgraph as pg # type: ignore
import PyQt6.QtCore as QtCore
from datetime import datetime, UTC
from testStand.communication import Client
from typing import Any
from testStand.log import LogFile
from testStand import IO

class MainWindow(QMainWindow):
    def __init__(self, comm: Client, config: dict[str, dict[str, Any | dict[str, list[Any]]]], switch: IO.Control, log: LogFile):
        """Class to create the main window for the control side of the system.

        Args:
            comm (Client): Instance of the client communication class.
            config (dict[str, Any]): Dictionary of the configuration options.
            switch (IO.Control): Instance of the control class.
            log (LogFile): Instance of the log file class.
        """
        super(MainWindow, self).__init__()
        
        if "-v" in sys.argv:
            self.verbose = True
        else:
            self.verbose = False
        if "-debug" in sys.argv:
            self.debug = True
        else:
            self.debug = False

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True) # type: ignore

        # Set up variables
        self.config = config
        self.comm = comm
        self.switch = switch
        self.log = log

        # Set up the graph widgets
        self.tempGraphWidget = pg.PlotWidget(title="Temperature")
        self.pressureGraphWidget = pg.PlotWidget(title="Pressure Transducers (Yellow=P1, Green=P2)")
        self.loadCellGraphWidget = pg.PlotWidget(title="Load Cell")
        self.thrustGraphWidget = pg.PlotWidget()

        # Define inital values
        self.time: list[float] = [0] * 100
        self.t1: list[float] = [0] * 100
        self.p1: list[float] = [0] * 100
        self.p2: list[float] = [0] * 100
        self.l1: list[float] = [0] * 100
        self.l2: list[float] = [0] * 100

        self.data = dict()
        
        # Configure the graphs
        self.pressureGraphWidget.setLabel('bottom', 'Time', units = 's')
        self.pressureGraphWidget.setLabel('left', 'Pressure', units = 'PSI')
        self.pressureGraphWidget.showGrid(x=True, y=True)
        self.pressureGraphWidget.setYRange(0,300) # type: ignore
        self.pressureGraphWidget.setBackground('w') # type: ignore

        self.loadCellGraphWidget.setLabel('bottom', 'Time', units = 's')
        self.loadCellGraphWidget.setLabel('left', 'Unit Load')
        self.loadCellGraphWidget.showGrid(x=True, y=True)
        self.loadCellGraphWidget.setBackground('w') # type: ignore

        self.tempGraphWidget.setLabel('bottom', 'Time', units = 's')
        self.tempGraphWidget.setLabel('left', 'Temperature', units = 'C')
        self.tempGraphWidget.showGrid(x=True, y=True)
        self.tempGraphWidget.setYRange(0,40) # type: ignore
        self.tempGraphWidget.setBackground('w') # type: ignore

        self.thrustGraphWidget.setLabel('bottom', 'Time', units = 's')
        self.thrustGraphWidget.setLabel('left', 'Thrust', units = 'N')
        self.thrustGraphWidget.showGrid(x=True, y=True)
        self.thrustGraphWidget.setBackground('w') # type: ignore

        self.thrustGraphWidget.setBackground('w') # type: ignore

        # Set up the time widgets
        self.serverTimeWidget = QLabel("Last Comm Time: hh:mm:ss")
        self.clientTimeWidget = QLabel("Client Time: hh:mm:ss")
        
        self.elapsedTimeWidget = QLabel("Elapsed Time: 0")

        # Set up the valve state widgets
        self.xv1Widget = QLabel("XV1: Closed")
        self.xv2Widget = QLabel("XV2: Open")
        self.xv3Widget = QLabel("XV3: Open")
        self.xv4Widget = QLabel("XV4: Open")
        self.xv5Widget = QLabel("XV5: Closed")
        self.xv6Widget = QLabel("XV6: Open")

        # Set up the data lines
        pen = pg.mkPen(color=(0, 0, 0)) # type: ignore
        self.temp_data_line = self.tempGraphWidget.plot(self.time, self.t1, pen=pen)
        self.pressure_1_data_line = self.pressureGraphWidget.plot(self.time, self.p1, pen=pen)
        self.pressure_2_data_line = self.pressureGraphWidget.plot(self.time, self.p2, pen=pen)
        self.loadCell_data_line = self.loadCellGraphWidget.plot(self.time, self.l1, pen=pen)
        self.thrust_data_line = self.thrustGraphWidget.plot(self.time, self.l2, pen=pen)
        
        # Set up the timer to update the UI
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_ui) # type: ignore
        self.timer.start()

        # Initalize Layouts
        mainLayout = QHBoxLayout()
        graphLayout = QGridLayout()
        topLayout = QHBoxLayout()
        leftLayout = QVBoxLayout()
        rightLayout = QVBoxLayout()
        timeLayout = QVBoxLayout()

        # Configure Graph Layout
        graphLayout.addWidget(self.tempGraphWidget, 0, 0)
        graphLayout.addWidget(self.pressureGraphWidget, 0, 1)
        graphLayout.addWidget(self.loadCellGraphWidget, 1, 0)
        graphLayout.addWidget(self.thrustGraphWidget, 1, 1)

        # Configure Time Layout
        timeLayout.addWidget(self.serverTimeWidget)
        timeLayout.addWidget(self.clientTimeWidget)

        # Configure Right Layout
        rightLayout.addWidget(self.xv1Widget)
        rightLayout.addWidget(self.xv2Widget)
        rightLayout.addWidget(self.xv3Widget)
        rightLayout.addWidget(self.xv4Widget)
        rightLayout.addWidget(self.xv5Widget)
        rightLayout.addWidget(self.xv6Widget)

        # Configure Top Layout
        topLayout.addLayout(timeLayout)
        topLayout.addWidget(self.elapsedTimeWidget)

        # Configure Main Layout
        leftLayout.addLayout(topLayout)
        leftLayout.addLayout(graphLayout)
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)
        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)
        return


    def update_ui(self):
        """Function to send the current state to the server and update the UI with the data recieved from the server
        
        """
        sendData: dict[str, dict[str, Any]] = dict()

        # Get the data from the server
        self.data: dict[str, dict[str, Any]] = self.comm.sendData(sendData)

        # Update the time
        self.time = self.time[1:]
        self.time.append(float(self.data.get("time", {}).get("elapsedTime", 0.0)))

        # Update the temp data
        self.t1 = self.t1[1:]
        self.t1.append(float(self.data.get("temps", {}).get("T1", 0)))

        # Update the pressure data
        self.p1 = self.p1[1:]
        self.p1.append(float(self.data.get("pressures", {}).get("P1", 0)))

        self.p2 = self.p2[1:]
        self.p2.append(float(self.data.get("pressures", {}).get("P2", 0)))

        # Update the load cell data
        self.l1 = self.l1[1:]
        self.l1.append(float(self.data.get("loads", {}).get("L1", 0)))
        
        # Update the graphs
        self.temp_data_line.setData(self.time, self.t1)
        self.pressure_1_data_line.setData(self.time, self.p1)
        self.pressure_2_data_line.setData(self.time, self.p2)
        self.loadCell_data_line.setData(self.time, self.l1)
        self.thrust_data_line.setData(self.time, self.l2)
        
         # Update the time widgets
        self.serverTimeWidget.setText(f"Last Comm Time: {self.data.get('time', {}).get('serverTime', 'hh:mm:ss')}")
        self.clientTimeWidget.setText(f"Client Time: {datetime.now(UTC).strftime('%H:%M:%S.%f')[:-3]}")

        self.elapsedTimeWidget.setText(f"Elapsed Time: {self.data.get('time', {}).get('elapsedTime', 0)}s")


        # Update the valve state widgets
        self.xv1Widget.setText(f"XV1: {self.data.get('valves', {}).get('xv1', 'False')}")
        self.xv2Widget.setText(f"XV2: {self.data.get('valves', {}).get('xv2', 'False')}")
        self.xv3Widget.setText(f"XV3: {self.data.get('valves', {}).get('xv3', 'False')}")
        self.xv4Widget.setText(f"XV4: {self.data.get('valves', {}).get('xv4', 'False')}")
        self.xv5Widget.setText(f"XV5: {self.data.get('valves', {}).get('xv5', 'False')}")
        self.xv6Widget.setText(f"XV6: {self.data.get('valves', {}).get('xv6', 'False')}")
        return
