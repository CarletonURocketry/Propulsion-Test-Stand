import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
import pyqtgraph as pg
import numpy as np
import PyQt6.QtCore as QtCore
import datetime

class MainWindow(QMainWindow):
    def __init__(self, comm, config, switch, log):
        """
        Initialize the MainWindow class.

        Args:
            comm (object): The communication object.
            config (object): The configuration object.
            switch (object): The switch object.
            log (object): The log object.
        """
        super(MainWindow, self).__init__()
        
        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)

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
        self.x = [0] * 100
        self.Time = [0] * 100 
        self.y = [0] * 100
        self.T1 = [0] * 100
        self.P1 = [0] * 100
        self.P2 = [0] * 100
        self.L1 = [0] * 100

        self.data = {"serverTime": 0, "elapsedTime": 0, "XV1": 0, "XV2": 0, "XV3": 0, "XV4": 0, "XV5": 0, "XV6": 0}
        
        # Configure the graphs
        self.pressureGraphWidget.setLabel('bottom', 'Time', units = 's')
        self.pressureGraphWidget.setLabel('left', 'Pressure', units = 'PSI')
        self.pressureGraphWidget.showGrid(x=True, y=True)
        self.pressureGraphWidget.setYRange(0,300)
        self.pressureGraphWidget.setBackground('w')

        self.loadCellGraphWidget.setLabel('bottom', 'Time', units = 's')
        self.loadCellGraphWidget.setLabel('left', 'Unit Load')
        self.loadCellGraphWidget.showGrid(x=True, y=True)
        self.loadCellGraphWidget.setBackground('w')

        self.tempGraphWidget.setLabel('bottom', 'Time', units = 's')
        self.tempGraphWidget.setLabel('left', 'Temperature', units = 'C')
        self.tempGraphWidget.showGrid(x=True, y=True)
        self.tempGraphWidget.setYRange(0,40)
        self.tempGraphWidget.setBackground('w')

        self.thrustGraphWidget.setLabel('bottom', 'Time', units = 's')
        self.thrustGraphWidget.setLabel('left', 'Thrust', units = 'N')
        self.thrustGraphWidget.showGrid(x=True, y=True)
        self.thrustGraphWidget.setBackground('w')

        self.thrustGraphWidget.setBackground('w')

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
        pen = pg.mkPen(color=(0, 0, 0))
        self.temp_data_line = self.tempGraphWidget.plot(self.Time, self.T1, pen=pen)
        self.pressure_1_data_line = self.pressureGraphWidget.plot(self.Time, self.P1, pen=pen)
        self.pressure_2_data_line = self.pressureGraphWidget.plot(self.Time, self.P2, pen=pen)
        self.loadCell_data_line = self.loadCellGraphWidget.plot(self.Time, self.L1, pen=pen)
        self.thrust_data_line = self.thrustGraphWidget.plot(self.Time, self.y, pen=pen)
        
        # Set up the timer to update the UI
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_ui)
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


    def update_ui(self):

        # Get the data from the server
        self.data = self.comm.sendData({"command": "start"})

        # Update the time
        self.Time = self.Time[1:]
        self.Time.append(float(self.data["time"]["elapsedTime"]))
        

        self.y = self.y[1:]  
        self.y.append(np.sin(self.Time[-1]))

        # Update the temp data
        self.T1 = self.T1[1:]
        self.T1.append(float(self.data["temps"]["T1"]))

        # Update the pressure data
        self.P1 = self.P1[1:]
        self.P1.append(float(self.data["pressures"]["P1"]))

        self.P2 = self.P2[1:]
        self.P2.append(float(self.data["pressures"]["P2"]))

        # Update the load cell data
        self.L1 = self.L1[1:]
        self.L1.append(float(self.data["loads"]["L1"]))
        
        # Update the graphs
        self.temp_data_line.setData(self.Time, self.T1)
        self.pressure_1_data_line.setData(self.Time, self.P1)
        self.pressure_2_data_line.setData(self.Time, self.P2)
        self.loadCell_data_line.setData(self.Time, self.L1)
        self.thrust_data_line.setData(self.x, self.y)
        
        # Update the time widgets
        self.serverTimeWidget.setText(f"Last Comm Time: {self.data["time"]["serverTime"]}")
        self.clientTimeWidget.setText(f"Client Time: {datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

        self.elapsedTimeWidget.setText(f"Elapsed Time: {self.data["time"]["elapsedTime"]}s")

        print(self.data)
        # Update the valve state widgets
        self.xv1Widget.setText(f"XV1: {self.data["valves"]["XV1"]}")
        self.xv2Widget.setText(f"XV2: {self.data["valves"]["XV2"]}")
        self.xv3Widget.setText(f"XV3: {self.data["valves"]["XV3"]}")
        self.xv4Widget.setText(f"XV4: {self.data["valves"]["XV4"]}")
        self.xv5Widget.setText(f"XV5: {self.data["valves"]["XV5"]}")
        self.xv6Widget.setText(f"XV6: {self.data["valves"]["XV6"]}")
        print(self.data)
