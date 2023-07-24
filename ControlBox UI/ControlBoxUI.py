import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import random
from datetime import datetime
import os

class Data():
    def __init__(self):
        self.millisSince = 0
        self.L1 = 0
        self.P1 = 0
        self.P2 = 0
        self.P3 = 0
        self.P4 = 0
        self.T1 = 0
        self.Safe = True

class Plot():
    def __init__(self, parent=None):
        self.parent = parent
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title="Plot")
        self.plot = self.win.addPlot(title="My Plot")
        self.curve = self.plot.plot(pen='r')

    def update(self, x, y):
        self.curve.setData(x, y)
        self.app.processEvents()

class PlotSet():
    def __init__(self, parent=None):
        self.parent = parent
        self.plot = Plot(parent=self.parent)

    def update(self, time, data):
        x = [time.timestamp()]
        y = [data.T1]
        self.plot.update(x, y)

class ScaleSlider():
    def __init__(self, parent, name, minVal, maxVal, step, value, callback):
        self.parent = parent
        self.callback = callback
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(minVal)
        self.slider.setMaximum(maxVal)
        self.slider.setSingleStep(step)
        self.slider.setValue(value)
        self.slider.valueChanged.connect(self.valueChanged)
        self.label = QtGui.QLabel(name)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slider)
        self.parent.setLayout(self.layout)

    def valueChanged(self, value):
        self.callback(value)

class LabeledToggle():
    def __init__(self, parent, id, callback, command, armed_state_var):
        self.parent = parent
        self.id = id
        self.callback = callback
        self.command = command
        self.armed_state_var = armed_state_var
        self.button = QtGui.QPushButton(f"Solenoid {id}")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.clicked)
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.button)
        self.parent.setLayout(self.layout)

    def clicked(self):
        if self.button.isChecked():
            self.callback(self.command)
        else:
            self.callback(f"{self.command}0")

class App(QtGui.QMainWindow):
    def __init__(self, arduino, logger):
        super().__init__()
        self.arduino = arduino
        self.logger = logger
        self.plotSet = PlotSet(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Test Stand Application")
        self.setGeometry(100, 100, 800, 600)

        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)

        self.gridLayout = QtGui.QGridLayout(self.centralWidget)

        self.buttonsFrame = QtGui.QFrame(self.centralWidget)
        self.buttonsFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.buttonsFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.gridLayout.addWidget(self.buttonsFrame, 0, 1, 1, 1)

        self.temperatureFrame = QtGui.QFrame(self.centralWidget)
        self.temperatureFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.temperatureFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.gridLayout.addWidget(self.temperatureFrame, 0, 0, 1, 1)

        self.temperatureReadout = QtGui.QLabel(self.temperatureFrame)
        self.temperatureReadout.setText("0.00")
        self.temperatureReadout.setAlignment(QtCore.Qt.AlignCenter)
        self.temperatureReadout.setStyleSheet("font-size: 48pt;")
        self.temperatureReadout.setGeometry(0, 0, 200, 100)

        self.scaleSlider = ScaleSlider(self.buttonsFrame, "Scale", 0, 100, 1, 50, self.slider)
        self.solenoid11_toggle = LabeledToggle(self.buttonsFrame, id=11, callback=self.arduino.sendCommand, command="10", armed_state_var=self.armed_state_var)
        self.solenoid11_toggle.layout.addWidget(self.solenoid11_toggle.button)
        self.solenoid12_toggle = LabeledToggle(self.buttonsFrame, id=12, callback=self.arduino.sendCommand, command="11", armed_state_var=self.armed_state_var)
        self.solenoid12_toggle.layout.addWidget(self.solenoid12_toggle.button)
        self.solenoid13_toggle = LabeledToggle(self.buttonsFrame, id=13, callback=self.arduino.sendCommand, command="12", armed_state_var=self.armed_state_var)
        self.solenoid13_toggle.layout.addWidget(self.solenoid13_toggle.button)
        self.solenoid14_toggle = LabeledToggle(self.buttonsFrame, id=14, callback=self.arduino.sendCommand, command="13", armed_state_var=self.armed_state_var)
        self.solenoid14_toggle.layout.addWidget(self.solenoid14_toggle.button)

        self.clearData_button = QtGui.QPushButton(self.buttonsFrame, text="Clear Data")
        self.clearData_button.clicked.connect(self.clearData)
        self.clearData_button.setGeometry(0, 0, 200, 100)

        self.show()

    def slider(self, value):
        print(value)

    def clearData(self):
        self.plotSet = PlotSet(self)
        self.plotSet.plot.update([], [])

    def close(self):
        print("Closing Application")
        if (hasattr(self, 'arduino')):
            self.arduino.close()
        self.logger.close()
        self.destroy()

    # The main code loop that runs in the background of the window (Repeatedly after "frequency" milliseconds)
    def loop(self, frequency):
        try:
            time = datetime.now()

            # Check for received data
            if (self.arduino.recvData()):

                # Update Plots
                self.plotSet.update(time, self.arduino.data)

                currentTime = datetime.now()
                # Update Readouts if 500ms have passed
                if ((currentTime - self.lastDisplayTime).total_seconds() * 1000 > self.refreshRate):
                    self.temperatureReadout.setText(f'{round(self.arduino.data.T1, 2)}')

                # Log data to file
                self.logger.write(time, self.arduino.data)

        except Exception as e:
            print(f"Error Parsing Arduino data: '{e}'")
            import traceback
            traceback.print_exc()

        # Run Loop again after "frequency" milliseconds
        self.after(frequency, self.loop, frequency)

""" Logger is used to log the data to a dataFile while the application is running
"""
class Logger():
    def __init__(self):
        pass

    def open(self):
        dataFilesPath = "dataFiles"
        if not os.path.isdir(dataFilesPath):
            os.makedirs(dataFilesPath)
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file = open(f"{dataFilesPath}/data_{date}.txt", "w")
        self.file.write(f"Time,L1,P1,P2,P3,P4,T1,Safe\n")

    def write(self, time, data):
        self.file.write(f"{time},{data.L1},{data.P1},{data.P2},{data.P3},{data.P4},{data.T1},{data.status_int}\n")

    def close(self):
        self.file.close()

""" This Data class defines the data structure that is received from the Ardiono
"""
class Data():
        millisSince = 0
        L1 = 0.0 #Loadcell
        P1 = 0.0 #Don't know
        P2 = 0.0 #Tank Pressure Bottom
        P3 = 0.0 #Tank Pressure Top
        P4 = 0.0 #Don't know
        T1 = 0.0 #Tank Temperature
        status_int = 0 

""" The Arduino class defines the connection to the arduino connected to the computer on which
the application runs, this allows the application to read data off the Arduino through a serial
connection
"""
class Arduino():
    def __init__(self, serialPort):
        #Initialize Serial Link
        try:
            self.link = txfer.SerialTransfer(serialPort)
            self.link.open()
            time.sleep(2)

        except Exception:
            import traceback
            traceback.print_exc()

            try:
                self.link.close()
            except Exception:
                pass

        self.control_int = 0
        self.control_list = [0] * 32#[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.data = Data()

    def close(self):
        try:
            self.link.close()
        except Exception:
            pass

    def recvData(self):
        if self.link.available():
            recSize = 0

            self.data.millisSince = self.link.rx_obj(obj_type='i', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['i']

            self.data.L1 = self.link.rx_obj(obj_type='f', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

            self.data.P1 = self.link.rx_obj(obj_type='f', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

            self.data.P2 = self.link.rx_obj(obj_type='f', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

            self.data.P3 = self.link.rx_obj(obj_type='f', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

            self.data.P4 = self.link.rx_obj(obj_type='f', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

            self.data.T1 = self.link.rx_obj(obj_type='f', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

            self.data.Safe = self.link.rx_obj(obj_type='b', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['b']
            return True
        
        elif self.link.status < 0:
            if self.link.status == txfer.CRC_ERROR:
                print('ERROR: CRC_ERROR')
            elif self.link.status == txfer.PAYLOAD_ERROR:
                print('ERROR: PAYLOAD_ERROR')
            elif self.link.status == txfer.STOP_BYTE_ERROR:
                print('ERROR: STOP_BYTE_ERROR')
            else:
                print('ERROR: {}'.format(self.link.status))
        return False

    def sendCommand(self, command):
        # Commands encoded as 3 digit numbers: 01-... for solenoid number, and 0-1 for off/on
        self.control_list[-int(command[0]+command[1])-1] = int(command[2])
        self.control_int = int(str(self.control_list).strip("[ ]").replace(", ",""),2) + 327680
        try:
            send_size = 0
            send_size = self.link.tx_obj(self.control_int, send_size)
            self.link.send(send_size)
        except:
            import traceback
            traceback.print_exc()

            self.link.close()

""" The ArduinoSim is used to allow the application to be tested (for development) without
needing to connect an arduino
"""
class ArduinoSim():
    def __init__(self):
        self.data = Data()
        self.data.P1 = 100
        self.data.P2 = 300
        self.data.P3 = 700
        self.data.P4 = 900
        self.data.T1 = 25

        self.lastSendTime = datetime.now()


    def close(self):
        print(f"Sim close()")
        pass

    def recvData(self):
        currentTime = datetime.now()

        if (((currentTime - self.lastSendTime).total_seconds() * 1000) > 100):
            self.data.millisSince = self.data.millisSince + ((currentTime - self.lastSendTime).total_seconds() * 1000)
            self.data.L1 = self.data.L1 + (random.random() * 2 - 1)*100
            self.data.P1 = self.data.P1 + (random.random() * 2 - 1)*10
            self.data.P2 = self.data.P2 + (random.random() * 2 - 1)*10
            self.data.P3 = self.data.P3 + (random.random() * 2 - 1)*10
            self.data.P4 = self.data.P4 + (random.random() * 2 - 1)*10
            self.data.T1 = self.data.T1 + (random.random() * 2 - 1)*1
            self.data.Safe = False
            self.lastSendTime = currentTime
            return True
        return False

    def sendCommand(self, command):
        print(f"Sim send command: {command}")

""" The main code block is run when this python file is run and starts the application"""
if __name__ == "__main__":

    # Select the serial port of the arduino, may be COM or whatever the Mac one is, use the Arduino IDE to find it.
    serialPort = "COM3"
    #arduino = Arduino(serialPort)

    # Currently using the ArduinoSim class to test the application with fake data.
    arduino = ArduinoSim()

    # Refresh Rate is how often the UI readouts are updated to allow for better readability
    refreshRate = 250 # The UI updates every 500 ms
    app = App(arduino, refreshRate, debug = False)
    
    # The app main loop will run repeatedly in a loop with at 10ms delay to allow the UI to update
    app.loop(10)
    app.mainloop()
