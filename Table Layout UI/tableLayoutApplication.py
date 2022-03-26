# Tkinter
import tkinter as tk
from tkinter import ttk
# Matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
# Serial
from pySerialTransfer import pySerialTransfer as txfer
# Other
import time
from datetime import datetime, timedelta
import random
import numpy as np
import os

def getNextRow(frame):
    if not hasattr(frame, 'row'):
        frame.row = 0
    row = frame.row
    frame.row += 1
    return row

class PressurePlot(tk.Frame):
    def __init__(self, parent):  
        # nb_points: number of points for the graph
        super().__init__(parent)

        # matplotlib figure
        self.figure = Figure(figsize=(8.5, 3.5), dpi=100)

        self.ax = self.figure.add_subplot(111)
        # Label Axes
        self.ax.set_xlabel('Time (hh:mm:ss)')
        self.ax.set_ylabel('Pressure (PSI)') 

        # Format the x-axis to show the time
        myFmt = mdates.DateFormatter("%H:%M:%S")
        self.ax.xaxis.set_major_formatter(myFmt)

        # Set initial x and y data (Null Data)
        self.x_data = []
        self.y_data = [[],[],[],[]] #[[0 for i in range(nb_points)] for i in range(0,4)]
        #print(self.y_data)

        # Create the plots
        self.pressure1Plot, = self.ax.plot(self.x_data, self.y_data[0], label='Pressure1', color="red")
        self.pressure2Plot, = self.ax.plot(self.x_data, self.y_data[1], label='Pressure2', color="yellow")
        self.pressure3Plot, = self.ax.plot(self.x_data, self.y_data[2], label='Pressure3', color="purple")
        self.pressure4Plot, = self.ax.plot(self.x_data, self.y_data[3], label='Pressure4', color="green")
        
        # Set default axis limits
        #self.ax.set_ylim(0, 100)
        #self.ax.set_xlim(self.x_data[0], self.x_data[-1])

        # Add Legend
        self.ax.legend()

        # Auto format date labels
        self.figure.autofmt_xdate()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack()

    def update(self, time, P1, P2, P3, P4):
        # append new data point to the x and y data
        self.x_data.append(time)
        #print(f"{P1},{P2},{P3},{P4}")
        self.y_data = np.append(self.y_data, [[P1],[P2],[P3],[P4]], axis=1)


        # remove oldest data point
        #self.x_data = self.x_data[1:]
        #self.y_data = np.delete(self.y_data, (0), axis=1)

        #print(self.y_data)
        #  update plot data
        self.pressure1Plot.set_xdata(self.x_data)
        self.pressure2Plot.set_xdata(self.x_data)
        self.pressure3Plot.set_xdata(self.x_data)
        self.pressure4Plot.set_xdata(self.x_data)
        self.pressure1Plot.set_ydata(self.y_data[0])
        self.pressure2Plot.set_ydata(self.y_data[1])
        self.pressure3Plot.set_ydata(self.y_data[2])
        self.pressure4Plot.set_ydata(self.y_data[3])

        self.canvas.draw_idle()  # redraw plot

class TemperaturePlot(tk.Frame):
    def __init__(self, parent):
        # nb_points: number of points for the graph
        super().__init__(parent)

        # matplotlib figure
        self.figure = Figure(figsize=(8.5, 3.5), dpi=100)

        self.ax = self.figure.add_subplot(111)
        # Format the x-axis to show the time
        myFmt = mdates.DateFormatter("%H:%M:%S")
        self.ax.xaxis.set_major_formatter(myFmt)

        # Set initial x and y data (Null Data)
        self.x_data = []
        self.y_data = []

        # Create the plot
        self.plot = self.ax.plot(self.x_data, self.y_data, label='Temperature', color="orange")[0]
        
        # Set default axis limits
        #self.ax.set_ylim(0, 100)
        #self.ax.set_xlim(self.x_data[0], self.x_data[-1])
        
        # Label Axes
        self.ax.set_xlabel('Time (hh:mm:ss)')
        self.ax.set_ylabel('Temperature (Degrees C)') 

        # Auto format date labels
        self.figure.autofmt_xdate()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack()

    def update(self, x_value, y_value):
        # append new data point to the x and y data
        self.x_data.append(x_value)
        self.y_data.append(y_value)

        # remove oldest data point
        #self.x_data = self.x_data[1:]
        #self.y_data = self.y_data[1:]

        #  update plot data
        self.plot.set_xdata(self.x_data)
        self.plot.set_ydata(self.y_data)
        #self.ax.set_xlim(self.x_data[0], self.x_data[-1])
        #self.ax.set_ylim(min(self.y_data)-5, max(self.y_data)+5)
        self.canvas.draw_idle()  # redraw plot

class ScaleSlider(tk.Frame):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback

        self.values = []

        self.sliderAtMax = True
        self.sliderAtMin = True

        self.minValue = 0
        self.maxValue = 0
        
        #Labels
        self.minLabel = tk.Label(self, text="Min:")
        self.minLabel.grid(column=0, row=0)
        self.maxLabel = tk.Label(self, text="Max:")
        self.maxLabel.grid(column=0, row=1)

        # Sliders
        self.sliderMin = tk.Scale(self, from_=0, to=100, length=600, orient='horizontal', command=self.minSliderChanged, showvalue=0, sliderlength=10, relief=tk.GROOVE)
        self.sliderMin.grid(column=1, row=0)
        
        self.sliderMax = tk.Scale(self, from_=0, to=100, length=600, orient='horizontal', command=self.maxSliderChanged, showvalue=0, sliderlength=10, relief=tk.GROOVE)
        self.sliderMax.grid(column=1, row=1)
        self.sliderMax.set(100)

        #Values
        self.minValueLabel = tk.Label(self, text="...")
        self.minValueLabel.grid(column=2, row=0)
        self.maxValueLabel = tk.Label(self, text="...")
        self.maxValueLabel.grid(column=2, row=1)

    def minSliderChanged(self, minValue):
        self.minValue = int(minValue)
        if (self.minValue >= self.maxValue - 1):
            self.minValue = self.maxValue - 1
            self.sliderMin.set(self.minValue)
        if (self.minValue == 0):
            self.sliderAtMin= True
        else:
            self.sliderAtMin = False
        
        self.minValueLabel.configure(text=f"{self.values[self.minValue]}"[10:-4])
        self.callback(self.minValue, self.maxValue)
    
    def maxSliderChanged(self, maxValue):
        self.maxValue = int(maxValue)
        if (self.maxValue <= self.minValue + 1):
            self.maxValue = self.minValue + 1
            self.sliderMax.set(self.maxValue)
        if (self.maxValue == len(self.values)-1):
            self.sliderAtMax = True
        else:
            self.sliderAtMax = False

        self.maxValueLabel.configure(text=f"{self.values[self.maxValue]}"[10:-4])
        self.callback(self.minValue, self.maxValue)

    def update(self, time):
        self.values.append(time)
        maxIndex = len(self.values) - 1
        self.sliderMin.configure(to=maxIndex)
        self.sliderMax.configure(to=maxIndex)
        if self.sliderAtMax:
            self.maxValue = len(self.values) - 1
            self.sliderMax.set(self.maxValue)
            if not self.sliderAtMin:
                self.minValue = self.minValue + 1
                self.sliderMin.set(self.minValue)
            else:
                self.minValueLabel.configure(text=f"{self.values[self.minValue]}"[10:-4])

class PlotSet(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.pressurePlot = PressurePlot(self)
        self.pressurePlot.grid(row=getNextRow(self), column=0)

        self.slider = ScaleSlider(self, self.updatePlotLimits)
        self.slider.grid(row=getNextRow(self), column=0)

        self.temperaturePlot = TemperaturePlot(self)
        self.temperaturePlot.grid(row=getNextRow(self), column=0)

    # def setLimits(self, x_min_index, x_max_index):
    #     self.ax.set_xlim(self.x_data[x_min_index], self.x_data[x_max_index])
    #     self.ax.set_ylim(min(self.y_data[x_min_index:x_max_index])-5, max(self.y_data[x_min_index:x_max_index])+5)
    #     self.canvas.draw_idle()  # redraw plot

    def update(self, time, data):
            self.slider.update(time)
            
            self.pressurePlot.update(time, data.P1, data.P2, data.P3, data.P4)
            self.temperaturePlot.update(time, data.T1)

            # Update Limits
            if self.slider.sliderAtMax:
                self.updatePlotLimits(self.slider.minValue, self.slider.maxValue)

    def updatePlotLimits(self, minIndex, maxIndex):
        self.pressurePlot.ax.set_xlim(self.pressurePlot.x_data[minIndex], self.pressurePlot.x_data[maxIndex])
        maxYValue = np.max(np.array(self.pressurePlot.y_data)[:, minIndex:maxIndex+1])
        self.pressurePlot.ax.set_ylim(np.min(np.array(self.pressurePlot.y_data)[:, minIndex:maxIndex+1])-maxYValue*0.1, maxYValue*1.10)
        #print(f"{minIndex}:{maxIndex}")
        self.temperaturePlot.ax.set_xlim(self.temperaturePlot.x_data[minIndex], self.temperaturePlot.x_data[maxIndex])
        self.temperaturePlot.ax.set_ylim(np.min(self.temperaturePlot.y_data[minIndex:maxIndex+1])-5, np.max(self.temperaturePlot.y_data[minIndex:maxIndex+1])+5)

class LabeledToggle(tk.Frame):
    def __init__(self, parent, text, callback, command, armed_state_var):
        super().__init__(parent)
        self.on = False
        self.armed_state_var = armed_state_var
        self.callback = callback
        self.command = command

        self.label = tk.Label(self, text=text)
        self.label.pack()

        self.toggleFrame = tk.Frame(self)
        self.toggleFrame.pack()
        self.offButton = tk.Button(self.toggleFrame, text="OFF", command=self.toggle)
        self.offButton.pack(side="left")
        self.onButton = tk.Button(self.toggleFrame, text="ON", command=self.toggle, relief=tk.SUNKEN, bg='#808080', fg="#808080", activeforeground="#808080", activebackground="#808080")
        self.onButton.pack(side="right")
        self.originalColor = self.offButton.cget("background")

    def toggle(self):
        if (self.armed_state_var.get() == True):
            if (self.on):
                self.on = False
                self.offButton.config(relief=tk.RAISED, bg=self.originalColor, fg="#000000", activeforeground="#000000")
                self.onButton.config(relief=tk.SUNKEN, bg='#808080', fg="#808080", activeforeground="#808080", activebackground="#808080")
                
                self.callback(self.command+"0")
            else:
                self.on = True
                self.onButton.config(relief=tk.RAISED, bg=self.originalColor, fg="#000000", activeforeground="#000000")
                self.offButton.config(relief=tk.SUNKEN, bg="#00aa00", fg="#00aa00", activeforeground="#00aa00", activebackground="#00aa00")

                self.callback(self.command+"1")

class Logger():
    def __init__(self):
        pass

    def open(self):
        dataFilesPath = "dataFiles"
        if not os.path.isdir(dataFilesPath):
            os.makedirs(dataFilesPath)
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file = open(f"{dataFilesPath}/data_{date}.txt", "w")
        self.write(f"Time,L1,P1,P2,P3,P4,T1,Safe\n")

    def write(self, message):
        self.file.write(message)

    def close(self):
        self.file.close()

class Data():
        millisSince = 0;
        L1 = 0.0 #Loadcell
        P1 = 0.0 #Don't know
        P2 = 0.0 #Tank Pressure Bottom
        P3 = 0.0 #Tank Pressure Top
        P4 = 0.0 #Don't know
        T1 = 0.0 #Tank Temperature
        Safety = False

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
        self.control_list = [0] * 13
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
        elif self.link.status < 0:
            if self.link.status == txfer.CRC_ERROR:
                print('ERROR: CRC_ERROR')
            elif self.link.status == txfer.PAYLOAD_ERROR:
                print('ERROR: PAYLOAD_ERROR')
            elif self.link.status == txfer.STOP_BYTE_ERROR:
                print('ERROR: STOP_BYTE_ERROR')
            else:
                print('ERROR: {}'.format(self.link.status))
    
    def sendCommand(self, command):
        # Commands encoded as 2 digit numbers: 1-4 for solenoid number, and 0-1 for off/on
        self.control_list[-int(command[0])-1] = int(command[1]) 
        self.control_int = int(str(self.control_list).strip("[ ]").replace(", ",""),2)
        try:
            send_size = 0
            send_size = self.link.tx_obj(self.control_int, send_size)
            self.link.send(send_size)
        except:
            import traceback
            traceback.print_exc()
               
            self.link.close()    
    
class ArduinoSim():
    def __init__(self):
        self.data = Data()
        self.data.P1 = 100
        self.data.P2 = 200
        self.data.P3 = 1000
        self.data.P4 = 700
        self.data.T1 = 25

    
    def close(self):
        print(f"Sim close()") 
        pass

    def recvData(self): 
        self.data.millisSince = self.data.millisSince + 10
        self.data.L1 = self.data.L1 + (random.random() * 2 - 1)*100
        self.data.P1 = self.data.P1 + (random.random() * 2 - 1)*10
        self.data.P2 = self.data.P2 + (random.random() * 2 - 1)*10
        self.data.P3 = self.data.P3 + (random.random() * 2 - 1)*10
        self.data.P4 = self.data.P4 + (random.random() * 2 - 1)*10
        self.data.T1 = self.data.T1 + (random.random() * 2 - 1)*1
        self.data.Safe = False
    
    def sendCommand(self, command):
        print(f"Sim send command: {command}") 

class App(tk.Tk):
    def __init__(self, arduino):
        super().__init__()

        self.arduino = arduino

        self.protocol("WM_DELETE_WINDOW", self.close)

        # Logger
        self.logger = Logger()
        self.logger.open()
        
        # Root window configuration
        self.title('Table Layout GUI')
        self.geometry('1200x750+200+10')
        self.row = 0

        self.plotsFrame = tk.Frame(self)
        self.plotsFrame.grid(row=0, column=0)

        # Plots and Sliders
        self.plotSet = PlotSet(self.plotsFrame)
        self.plotSet.grid(row=getNextRow(self.plotsFrame), column=0)

        # Right Hand Frame
        self.rightFrame = tk.Frame(self)
        self.rightFrame.grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1)


        # Readouts Frame
        self.readoutsFrame = tk.Frame(self.rightFrame)
        self.readoutsFrame.grid(row=0, column=0, columnspan=2)
        
        # Temperature Readout
        self.temperatureLabel = tk.Label(self.readoutsFrame, text='Temperature', font=("Arial", 10))
        self.temperatureLabel.grid(row=0, column=0, columnspan=2)
        self.temperatureReadout = tk.Label(self.readoutsFrame, text='Initalizing...', font=("Arial", 25), width=6)
        self.temperatureReadout.grid(row=1, column=0, columnspan=2)

        # Pressure Readouts
        self.pressureLabel1 = tk.Label(self.readoutsFrame, text='Pressure 1', font=("Arial", 10))
        self.pressureLabel1.grid(row=2, column=0)
        self.pressureReadout1 = tk.Label(self.readoutsFrame, text='Initalizing...', font=("Arial", 25), width=6)
        self.pressureReadout1.grid(row=3, column=0, padx=20)

        self.pressureLabel2 = tk.Label(self.readoutsFrame, text='Pressure 2', font=("Arial", 10))
        self.pressureLabel2.grid(row=2, column=1)
        self.pressureReadout2 = tk.Label(self.readoutsFrame, text='Initalizing...', font=("Arial", 25), width=6)
        self.pressureReadout2.grid(row=3, column=1, padx=20)

        self.pressureLabel3 = tk.Label(self.readoutsFrame, text='Pressure 3', font=("Arial", 10))
        self.pressureLabel3.grid(row=4, column=0)
        self.pressureReadout3 = tk.Label(self.readoutsFrame, text='Initalizing...', font=("Arial", 25), width=6)
        self.pressureReadout3.grid(row=5, column=0, padx=20)

        self.pressureLabel4 = tk.Label(self.readoutsFrame, text='Pressure 4', font=("Arial", 10))
        self.pressureLabel4.grid(row=4, column=1)
        self.pressureReadout4 = tk.Label(self.readoutsFrame, text='Initalizing...', font=("Arial", 25), width=6)
        self.pressureReadout4.grid(row=5, column=1, padx=20)

        self.buttonsFrame = tk.Frame(self.rightFrame)
        self.buttonsFrame.grid(row=1, column=0)
        self.rightFrame.grid_columnconfigure(0, weight=1)

        # Armed Check
        self.armed_state_var = tk.BooleanVar()
        self.armed_state_var.set(False) #set check state
        self.armed_checkbutton = tk.Checkbutton(self.buttonsFrame, text='Armed', var=self.armed_state_var)
        self.armed_checkbutton.grid(row=0, column=0, pady=(20,0), columnspan=2)

        # Solenoid Toggles
        self.solenoidFire_toggle = LabeledToggle(self.buttonsFrame, text="Fire", callback=self.arduino.sendCommand, command="0", armed_state_var=self.armed_state_var)
        self.solenoidFire_toggle.grid(row=1, column=0, pady=5, padx=20)

        self.solenoidFill_toggle = LabeledToggle(self.buttonsFrame, text="Fill", callback=self.arduino.sendCommand, command="1", armed_state_var=self.armed_state_var)
        self.solenoidFill_toggle.grid(row=2, column=0, pady=5, padx=20)

        self.solenoidVent_toggle = LabeledToggle(self.buttonsFrame, text="Vent", callback=self.arduino.sendCommand, command="2", armed_state_var=self.armed_state_var)
        self.solenoidVent_toggle.grid(row=3, column=0, pady=5, padx=20)

        self.solenoidPower_toggle = LabeledToggle(self.buttonsFrame, text="Power", callback=self.arduino.sendCommand, command="3", armed_state_var=self.armed_state_var)
        self.solenoidPower_toggle.grid(row=4, column=0, pady=5, padx=20)


        self.solenoid5_toggle = LabeledToggle(self.buttonsFrame, text="Solenoid 5", callback=self.arduino.sendCommand, command="4", armed_state_var=self.armed_state_var)
        self.solenoid5_toggle.grid(row=5, column=0, pady=5, padx=20)

        self.solenoid6_toggle = LabeledToggle(self.buttonsFrame, text="Solenoid 6", callback=self.arduino.sendCommand, command="5", armed_state_var=self.armed_state_var)
        self.solenoid6_toggle.grid(row=6, column=0, pady=0, padx=20)

        self.solenoid7_toggle = LabeledToggle(self.buttonsFrame, text="Solenoid 7", callback=self.arduino.sendCommand, command="6", armed_state_var=self.armed_state_var)
        self.solenoid7_toggle.grid(row=1, column=1, pady=5, padx=20)

        self.solenoid8_toggle = LabeledToggle(self.buttonsFrame, text="Solenoid 8", callback=self.arduino.sendCommand, command="7", armed_state_var=self.armed_state_var)
        self.solenoid8_toggle.grid(row=2, column=1, pady=5, padx=20)

        self.solenoid9_toggle = LabeledToggle(self.buttonsFrame, text="Solenoid 9", callback=self.arduino.sendCommand, command="8", armed_state_var=self.armed_state_var)
        self.solenoid9_toggle.grid(row=3, column=1, pady=5, padx=20)

        self.solenoid10_toggle = LabeledToggle(self.buttonsFrame, text="Solenoid 10", callback=self.arduino.sendCommand, command="9", armed_state_var=self.armed_state_var)
        self.solenoid10_toggle.grid(row=4, column=1, pady=5, padx=20)

        self.solenoid11_toggle = LabeledToggle(self.buttonsFrame, text="Solenoid 11", callback=self.arduino.sendCommand, command="10", armed_state_var=self.armed_state_var)
        self.solenoid11_toggle.grid(row=5, column=1, pady=5, padx=20)

        self.solenoid12_toggle = LabeledToggle(self.buttonsFrame, text="Solenoid 12", callback=self.arduino.sendCommand, command="11", armed_state_var=self.armed_state_var)
        self.solenoid12_toggle.grid(row=6, column=1, pady=5, padx=20)

    def close(self):
        print("Closing Application") 
        if (hasattr(self, 'arduino')):
            self.arduino.close()
        self.logger.close()
        self.destroy()
    
    def slider(self, name):
        print(name)

    # The main code loop that runs in the background of the window (Every "frequency" milliseconds)
    def loop(self, frequency):
        try:
            #Check for received data
            self.arduino.recvData()                
        
            time = datetime.now()
            # Update Plots
            self.plotSet.update(time, self.arduino.data)
            
            # Update Readouts
            self.temperatureReadout.config(text=f'{round(self.arduino.data.T1, 2)}')
            self.pressureReadout1.config(text=f'{round(self.arduino.data.P1, 2)}')
            self.pressureReadout2.config(text=f'{round(self.arduino.data.P2, 2)}')
            self.pressureReadout3.config(text=f'{round(self.arduino.data.P3, 2)}')
            self.pressureReadout4.config(text=f'{round(self.arduino.data.P4,2)}')

            self.logger.write(f"{time},{self.arduino.data.L1},{self.arduino.data.P1},{self.arduino.data.P2},{self.arduino.data.P3},{self.arduino.data.P4},{self.arduino.data.T1},{self.arduino.data.Safe}\n")
        except Exception as e:
            print(f"Error Parsing Arduino data: '{e}'")
            import traceback
            traceback.print_exc()
            
            

        # Run Loop again after "frequency" milliseconds
        self.after(frequency, self.loop, frequency)
  
if __name__ == "__main__":

    serialPort = "COM3"
    #arduino = Arduino(serialPort)
    arduino = ArduinoSim()

    app = App(arduino)
    app.loop(100)
    app.mainloop()
