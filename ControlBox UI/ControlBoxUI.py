"""The refactored Test Stand application is intended to be used for the Carleton CUInSpace rocket team test stand
for the new hybrid rocket engine.

Note that chunks of the code have yet to be cleaned up, due to lack in context on respective functionality from team members.

Author: Angela Chen (angelachen4@cmail.carleton.ca)
Date: November 6, 2023
"""
# def toggleMode(state):
#     if state == 2:  # 2 corresponds to checked state
#         # Dark mode
#         pg.setConfigOption('background', 'k')
#         pg.setConfigOption('foreground', 'w')
#     else:
#         # Light mode
#         pg.setConfigOption('background', 'w')
#         pg.setConfigOption('foreground', 'k')
# Be sure to use the local subpackage rather than any globally-installed version.
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
# Serial
from pySerialTransfer import pySerialTransfer as txfer
# Other
from datetime import datetime
import numpy as np
import time, os, math, random

#Debuging variables
lastStatus = -1
qtApp = pg.mkQApp("Control Box UI")
pg.setConfigOption('background', 'w')
view = pg.GraphicsView()
win = pg.GraphicsLayout(border=(100,100,100))
#win = pg.GraphicsLayout(show=True, title="Control Box UI")
view.setCentralItem(win)
view.show()
view.resize(2880,1920)
view.setWindowTitle('Control Box UI')
# pg.setConfigOption('foreground', 'k')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)
L1 = win.addPlot(title="Load Cell")
L1.setLabel('bottom', 'Time', units = 's')
L1.setLabel('left', 'Unit Load')
L1.showGrid(x=True, y=True)

# toggleArea = win.addViewBox(lockAspect=True)
# checkbox = pg.QCheckBox("Dark Mode")
# toggleArea.addWidget(checkbox)
# toggleArea.autoRange()

legend = win.addPlot(title="Legend")
legend.setYRange(-1, 2)
current_time = pg.TextItem("Current Time:")
current_time.setPos(0, 0)
elapsed_seconds = pg.TextItem("Elapsed Seconds Since Program Start:")
speed = pg.TextItem("Speed (in Hz):")
legend.addItem(current_time)
legend.addItem(elapsed_seconds)
legend.addItem(speed)
# legend.addItem(checkbox)
# checkbox.setPos(400, 20, 100)
win.nextRow()

pressure = win.addPlot(title="Pressure Chambers")
pressure.setLabel('bottom', 'Time', units = 's')
pressure.setLabel('left', 'Pressure', units = 'PSI')
pressure.showGrid(x=True, y=True)

T1 = win.addPlot(title="Temperature")
T1.setLabel('bottom', 'Time', units = 's')
T1.setLabel('left', 'Temperature', units = 'C')
T1.showGrid(x=True, y=True)

nPlots = 6
# curves = [loadcell, pressure1, pressure2, pressure3, pressure4, temperature]
curves = []
for idx in range(nPlots):
    curve = pg.PlotCurveItem(pen=({'color': (idx, nPlots*1.3), 'width': 8}), skipFiniteCheck=True)
    if idx == 0:
        L1.addItem(curve)
    elif idx == 5:
        T1.addItem(curve)
    else:
        pressure.addItem(curve)
    curve.setPos(0,idx*6)
    curves.append(curve)
ptr = 0

pressure_legend = pressure.addLegend()
""" App is the main component for the application. It is the main tkinter window as well as
the main running code for the application
"""
class App():
    def __init__(self, arduino, refreshRate, debug = False):
        super().__init__()
        self.data = np.zeros((7,0))
        self.arduino = arduino
        self.lastDisplayTime = datetime.now()
        self.refreshRate = refreshRate
        self.start_time = datetime.now()

        indicators = [[0,"Error","red",1],[0,"Warning","yellow",2],[0,"Waiting","blue",256],[0,"Packet","blue",512],
                [0,"Armed","yellow",4],[0,"Active","yellow",8],[0,"Abort","red",16],[0,"Invalid","red",32],
                [0,"Mismatch","red",1024],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],
                [0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],
                [0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],
                [0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],
                [0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],
                [0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0]]
        
        self.indicators = indicators

        #self.protocol("WM_DELETE_WINDOW", self.close)

        # Logger
        self.logger = Logger()
        self.logger.open()
        
        # #Status Indicators
        # self.indicatorsFrame = tk.Frame(self.rightFrame)
        # self.indicatorsFrame.grid(row=1, column=0 ,columnspan=2, pady=25)

    def close(self):
        print("Closing Application") 
        if (hasattr(self, 'arduino')):
            self.arduino.close()
        self.logger.close()
        self.destroy()

    # The main code loop that runs in the background of the window (Repeatedly after "frequency" milliseconds)
    def loop(self):
        try:
            time = datetime.now()
            global lastStatus
            # Check for received data
            if (self.arduino.recvData()):
                output = ""
                for x in self.indicators:
                    if x[0] != 0:
                        if self.arduino.data.status_int & x[3]:
                            output += (x[1] + " ")
                            x[0].config(bg = x[2])
                        else:
                            x[0].config(bg = "white")
                            
                if lastStatus != self.arduino.data.status_int:
                    print(output)
                    lastStatus = self.arduino.data.status_int
            
                elapsed_seconds = (time - self.start_time).total_seconds()
                global curves, ptr
                self.data = np.append(self.data, [[elapsed_seconds],[self.arduino.data.P1],[self.arduino.data.P2],[self.arduino.data.P3],[self.arduino.data.P4],[self.arduino.data.T1],[self.arduino.data.L1]], axis=1)

                if ptr < 100:
                   curves[0].setData(self.data[0], self.data[6])
                   curves[1].setData(self.data[0], self.data[1])
                   curves[2].setData(self.data[0], self.data[2])
                   curves[3].setData(self.data[0], self.data[3])
                   curves[4].setData(self.data[0], self.data[4])
                   curves[5].setData(self.data[0], self.data[5])
                else:
                    #self.data = self.data[0:6,:-1]
                    ptr += 1
                # Update Readouts if 50ms have passed
                    
                    # self.data = self.data[0:7, :-99]
                    # np.append(self.data, [[elapsed_seconds],[self.arduino.data.P1],[self.arduino.data.P2],[self.arduino.data.P3],[self.arduino.data.P4],[self.arduino.data.T1],[self.arduino.data.L1]], axis=1)
                    # curves[0].setPos(self.data[0,-100], self.data[6,0])
                    # curves[1].setPos(self.data[0, -100], self.data[1,0])
                    # curves[2].setPos(self.data[0, -100], self.data[2,0])
                    # curves[3].setPos(self.data[0, -100], self.data[3,0])
                    # curves[4].setPos(self.data[0, -100], self.data[4,0])
                    curves[0].setData(self.data[0, -100:-1], self.data[6, -100:-1])
                    curves[1].setData(self.data[0, -100:-1], self.data[1, -100:-1])
                    curves[2].setData(self.data[0, -100:-1], self.data[2, -100:-1])
                    curves[3].setData(self.data[0, -100:-1], self.data[3, -100:-1])
                    curves[4].setData(self.data[0, -100:-1], self.data[4, -100:-1])
                    curves[5].setData(self.data[0, -100:-1], self.data[5, -100:-1])
        
                #plot.setTitle(f'Elapsed Time: {elapsed_seconds:.1f} seconds')
                # Log data to file
                self.logger.write(time, self.arduino.data)
                ptr += 1

        except Exception as e:
            print(f"Error Parsing Arduino data: '{e}'")
            import traceback
            traceback.print_exc()
        
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
            
            self.data.L1 = self.link.rx_obj(obj_type='H', start_pos=recSize)
            recSize += 2
            
            self.data.P1 = self.link.rx_obj(obj_type='H', start_pos=recSize)
            recSize += 2
            
            self.data.P2 = self.link.rx_obj(obj_type='H', start_pos=recSize)
            recSize += 2
            
            self.data.P3 = self.link.rx_obj(obj_type='H', start_pos=recSize)
            recSize += 2
            
            self.data.P4 = self.link.rx_obj(obj_type='H', start_pos=recSize)
            recSize += 2
            
            self.data.T1 = self.link.rx_obj(obj_type='H', start_pos=recSize)
            self.data.T1 = self.data.T1/10
            recSize += 2

            self.data.status_int = self.link.rx_obj(obj_type='I', start_pos=recSize)
            recSize += 4
            
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
    app = App(arduino, refreshRate, debug = True)
    timer = QtCore.QTimer()
    timer.timeout.connect(app.loop)
    timer.start(50)
    pg.exec()
