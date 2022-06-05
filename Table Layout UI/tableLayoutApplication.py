# Tkinter
import tkinter as tk
from tkinter import ttk
# Matplotlib
import matplotlib.pyplot as plt
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
import math


class Plot(tk.Frame):
    def __init__(self, parent, data):  
        super().__init__(parent)
        self.plotSet = parent

        # matplotlib figure
        self.figure = plt.Figure(figsize=(8,7.4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.1, bottom=0, right=0.92, top=0.97, wspace=0, hspace=0)
        

        # Label Axes
        self.ax2 = self.ax.twinx()

        self.ax.set_xlabel('Time (hh:mm:ss)')
        self.ax.set_ylabel('Pressure (PSI)') 
        self.ax2.set_ylabel("Temperature (Degrees C)")

        # Format the x-axis to show the time
        myFmt = mdates.DateFormatter("%H:%M:%S")
        self.ax.xaxis.set_major_formatter(myFmt)

        # Create the plots
        self.pressure1Plot, = self.ax.plot(data[0], data[1], label='Pressure1', color="red")
        self.pressure2Plot, = self.ax.plot(data[0], data[2], label='Pressure2', color="blue")
        self.pressure3Plot, = self.ax.plot(data[0], data[3], label='Pressure3', color="purple")
        self.pressure4Plot, = self.ax.plot(data[0], data[4], label='Pressure4', color="green")

        self.temperaturePlot, = self.ax2.plot(data[0], data[5], label='Temperature', color="orange", linestyle="dashed")

        lns = [self.pressure1Plot, self.pressure2Plot, self.pressure3Plot, self.pressure4Plot, self.temperaturePlot]
        labs = [l.get_label() for l in lns]
        self.ax.legend(lns, labs, loc=2)

        # Auto format date labels
        self.figure.autofmt_xdate()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
    def update(self, data):    
        #  Update plot data
        self.pressure1Plot.set_xdata(data[0])
        self.pressure2Plot.set_xdata(data[0])
        self.pressure3Plot.set_xdata(data[0])
        self.pressure4Plot.set_xdata(data[0])
        self.temperaturePlot.set_xdata(data[0])

        self.pressure1Plot.set_ydata(data[1])
        self.pressure2Plot.set_ydata(data[2])
        self.pressure3Plot.set_ydata(data[3])
        self.pressure4Plot.set_ydata(data[4])
        self.temperaturePlot.set_ydata(data[5])
            
        self.canvas.draw_idle()  # redraw plot

class PlotSet(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.data = np.zeros((6,0))

        self.plot = Plot(self, self.data)
        self.plot.grid(row=0, column=0)

        self.plotButtonsFrame = tk.Frame(self)
        self.plotButtonsFrame.grid(row=0, column=0, sticky="se")

        self.duration = tk.IntVar(value=10)

        self.duration_10mins = tk.Radiobutton(self.plotButtonsFrame, text="10 Minutes", variable=self.duration, value=600)
        self.duration_10mins.grid(row=0, column=0)
        self.duration_5mins = tk.Radiobutton(self.plotButtonsFrame, text="5 Minutes", variable=self.duration, value=300)
        self.duration_5mins.grid(row=0, column=1)
        self.duration_1min = tk.Radiobutton(self.plotButtonsFrame, text="1 Minute", variable=self.duration, value=60)
        self.duration_1min.grid(row=0, column=2)
        self.duration_30secs = tk.Radiobutton(self.plotButtonsFrame, text="30 Seconds", variable=self.duration, value=30)
        self.duration_30secs.grid(row=0, column=3)
        self.duration_10secs = tk.Radiobutton(self.plotButtonsFrame, text="10 Seconds", variable=self.duration, value=10)
        self.duration_10secs.grid(row=0, column=4)

        self.slider = ScaleSlider(self.plotButtonsFrame, self, self.updatePlotLimits)
        self.slider.grid(row=1, column=0, columnspan=6)
        
        self.displayPressure1 = tk.IntVar(value=True)
        self.Pressure1CB = tk.Checkbutton(self.plotButtonsFrame, text="Pressure 1", variable=self.displayPressure1, command=lambda: self.checkboxClicked(1, self.displayPressure1))
        self.Pressure1CB.grid(row=2, column=0)
        self.displayPressure2 = tk.IntVar(value=True)
        self.Pressure2CB = tk.Checkbutton(self.plotButtonsFrame, text="Pressure 2", variable=self.displayPressure2, command=lambda: self.checkboxClicked(2, self.displayPressure2))
        self.Pressure2CB.grid(row=2, column=1)
        self.displayPressure3 = tk.IntVar(value=True)
        self.Pressure3CB = tk.Checkbutton(self.plotButtonsFrame, text="Pressure 3", variable=self.displayPressure3, command=lambda: self.checkboxClicked(3, self.displayPressure3))
        self.Pressure3CB.grid(row=2, column=2)
        self.displayPressure4 = tk.IntVar(value=True)
        self.Pressure4CB = tk.Checkbutton(self.plotButtonsFrame, text="Pressure 4", variable=self.displayPressure4, command=lambda: self.checkboxClicked(4, self.displayPressure4))
        self.Pressure4CB.grid(row=2, column=3)
        self.displayTemperature = tk.IntVar(value=True)
        self.TemperatureCB = tk.Checkbutton(self.plotButtonsFrame, text="Temperature", variable=self.displayTemperature, command=lambda: self.checkboxClicked(5, self.displayTemperature))
        self.TemperatureCB.grid(row=2, column=4)

        self.saveButton = tk.Button(self.plotButtonsFrame, text="Save Plot", command=self.savePlot)
        self.saveButton.grid(row=2, column=5)
    
    def checkboxClicked(self, id, var):
        if (id == 5):
            if (var.get() == False):
                self.plot.ax2.get_yaxis().set_visible(False)
                self.plot.temperaturePlot.set_linestyle("none")
            else:
                self.plot.ax2.get_yaxis().set_visible(True)
                self.plot.temperaturePlot.set_linestyle("dashed")
        else:
            if (var.get() == False):
                self.plot.ax.lines[id-1].set_linestyle("none")
            else:
                self.plot.ax.lines[id-1].set_linestyle("solid")

    def savePlot(self):
        figuresPath = "figures"
        if not os.path.isdir(figuresPath):
            os.makedirs(figuresPath)

        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.plot.figure.savefig(f"{figuresPath}/plot_{date}.png")

    def update(self, time, data):

        self.data = np.append(self.data, [[time],[data.P1],[data.P2],[data.P3],[data.P4],[data.T1]], axis=1)

        self.slider.update(self.data[0])
        self.plot.update(self.data)   
        if not len(self.data[0]) == 1:
            self.updatePlotLimits()

    def getMinIndex(self, maxIndex):
        currentTime = self.data[0][maxIndex]
        approxMinTime = self.data[0][maxIndex] - timedelta(seconds=self.duration.get())
        minTime = min(self.data[0], key=lambda d: abs(d - approxMinTime))
        return np.where(self.data[0] == minTime)[0][0]

    def updatePlotLimits(self):
        data = self.data
        maxIndex = self.slider.index
        minIndex = self.getMinIndex(maxIndex)
        self.plot.ax.set_xlim(data[0][minIndex], data[0][maxIndex])

        #TODO: Make adjust for only shown data
        maxPressure = 0
        minPressure = 99999999
        if (self.displayPressure1.get() == 1):
            maxPressure = max(maxPressure, np.max(np.array(data[1, minIndex:maxIndex+1])))
            minPressure = min(minPressure, np.min(np.array(data[1, minIndex:maxIndex+1])))
        if (self.displayPressure2.get() == 1):
            maxPressure = max(maxPressure, np.max(np.array(data[2, minIndex:maxIndex+1])))
            minPressure = min(minPressure, np.min(np.array(data[2, minIndex:maxIndex+1])))
        if (self.displayPressure3.get() == 1):
            maxPressure = max(maxPressure, np.max(np.array(data[3, minIndex:maxIndex+1])))
            minPressure = min(minPressure, np.min(np.array(data[3, minIndex:maxIndex+1])))
        if (self.displayPressure4.get() == 1):
            maxPressure = max(maxPressure, np.max(np.array(data[4, minIndex:maxIndex+1])))
            minPressure = min(minPressure, np.min(np.array(data[4, minIndex:maxIndex+1])))

        #Make only for shown range
        #maxYValue = np.max(np.array(data[1:5, minIndex:maxIndex+1])) #[:, minIndex:maxIndex+1]
        self.plot.ax.set_ylim(minPressure-abs(maxPressure)*0.1, maxPressure*1.10)

        maxTemp = np.max(data[5, minIndex:maxIndex+1])
        minTemp = np.min(data[5, minIndex:maxIndex+1])
        self.plot.ax2.set_ylim(minTemp-abs(maxTemp)*0.2, maxTemp*1.2)

class ScaleSlider(tk.Frame):
    def __init__(self, parent, plotSet, callback):
        super().__init__(parent)
        self.plotSet = plotSet
        self.callback = callback

        self.sliderAtMax = True
        self.index = 1
        
        self.slider = tk.Scale(self, from_=1, to=1, length=730, orient='horizontal', command=self.sliderChanged, showvalue=0, sliderlength=10, relief=tk.GROOVE)
        self.slider.grid(column=0, row=0)
        self.slider.set(1)

        def replaceClick(event):
            self.slider.event_generate('<Button-3>', x=event.x, y=event.y)
            return 'break'
        # Turn left clicks into right clicks for better usage
        self.slider.bind('<Button-1>', replaceClick)

        #Values
        self.sliderLabel = tk.Label(self, text="...")
        self.sliderLabel.grid(column=1, row=0)

    def sliderChanged(self, index):
        self.index = int(index)
        self.slider.set(self.index)
        if (self.index >= self.plotSet.data[0].size - 1):
            self.sliderAtMax = True
        else:
            self.sliderAtMax = False
        self.sliderLabel.configure(text=f"{self.plotSet.data[0][self.index]}"[10:-4])
        self.callback()

    def update(self, x_data):
        maxIndex = x_data.size - 1
        self.slider.configure(to=maxIndex)
        if self.sliderAtMax:
            self.index = x_data.size - 1
            self.slider.set(self.index)
            self.sliderLabel.configure(text=f"{self.plotSet.data[0][self.index]}"[10:-4])

class LabeledToggle(tk.Frame):
    def __init__(self, parent, id, callback, command, armed_state_var):
        super().__init__(parent)
        self.on = False
        self.id = id
        self.armed_state_var = armed_state_var
        self.callback = callback
        self.command = command

        self.label = tk.Label(self, text=self.readLabel())
        self.label.bind("<Button-1>", self.labelClicked)
        self.label.pack()

        self.toggleFrame = tk.Frame(self)
        self.toggleFrame.pack()
        self.offButton = tk.Button(self.toggleFrame, text="OFF", command=self.toggle)
        self.offButton.pack(side="left")
        self.originalColor = self.offButton.cget("background")
        self.onButton = tk.Button(self.toggleFrame, text="ON", command=self.toggle, relief=tk.SUNKEN, bg='#808080', fg="#808080", activeforeground="#808080", activebackground="#808080")
        self.onButton.pack(side="right")
        

    def labelClicked(self, event):
        widget = event.widget
        entry_widget = tk.Entry(widget)
        entry_widget.place(x=0, y=0, anchor="nw", relwidth=1.0, relheight=1.0)
        entry_widget.bind("<Return>", self.remove_entry)
        entry_widget.focus_set()

    def remove_entry(self, event):
        entry = event.widget
        label = entry.place_info()["in"]
        label.configure(text=entry.get())
        self.updateLabel(entry.get())
        entry.destroy()

    def toggle(self):
        if (self.armed_state_var.get() == True):
            if (self.on):
                self.on = False
                self.offButton.config(relief=tk.RAISED, bg=self.originalColor, fg="#000000", activeforeground="#000000", activebackground=self.originalColor)
                self.onButton.config(relief=tk.SUNKEN, bg='#808080', fg="#808080", activeforeground="#808080", activebackground="#808080")
                
                self.callback(self.command+"0")
            else:
                self.on = True
                self.onButton.config(relief=tk.RAISED, bg=self.originalColor, fg="#000000", activeforeground="#000000", activebackground=self.originalColor)
                self.offButton.config(relief=tk.SUNKEN, bg="#00aa00", fg="#00aa00", activeforeground="#00aa00", activebackground="#00aa00")

                self.callback(self.command+"1")

    def updateLabel(self, label):
        f = open("labels.csv", "r")
        content = f.readlines()
        f.close()
        content[self.id-1] = f"{self.id},{label},\n"

        f = open("labels.csv", "w")
        new_file_contents = "".join(content)
        f.write(new_file_contents)
        f.close()

    def readLabel(self):
        f = open("labels.csv", "r")
        label = ""
        for l in f:
            if l.split(",")[0] == f"{self.id}":
                label = l.split(",")[1]
        f.close()
        return label

class App(tk.Tk):
    def __init__(self, arduino, refreshRate):
        super().__init__()

        self.arduino = arduino
        self.lastDisplayTime = datetime.now()
        self.refreshRate = refreshRate

        self.protocol("WM_DELETE_WINDOW", self.close)

        # Logger
        self.logger = Logger()
        self.logger.open()
        
        # Root window configuration
        self.title('Table Layout GUI')
        self.geometry('1200x750+200+10')
        self.row = 0

        # Plots and Sliders
        self.plotSet = PlotSet(self)
        self.plotSet.grid(row=0, column=0)

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
        self.armed_checkbutton.grid(row=0, column=0, pady=(20,0), columnspan=3)

        # Solenoid Toggles
        self.solenoidFire_toggle = LabeledToggle(self.buttonsFrame, id=1, callback=self.arduino.sendCommand, command="00", armed_state_var=self.armed_state_var)
        self.solenoidFire_toggle.grid(row=1, column=0, pady=10, padx=20)

        self.solenoidFill_toggle = LabeledToggle(self.buttonsFrame, id=2, callback=self.arduino.sendCommand, command="01", armed_state_var=self.armed_state_var)
        self.solenoidFill_toggle.grid(row=2, column=0, pady=10, padx=20)

        self.solenoidVent_toggle = LabeledToggle(self.buttonsFrame, id=3, callback=self.arduino.sendCommand, command="02", armed_state_var=self.armed_state_var)
        self.solenoidVent_toggle.grid(row=3, column=0, pady=10, padx=20)

        self.solenoidPower_toggle = LabeledToggle(self.buttonsFrame, id=4, callback=self.arduino.sendCommand, command="03", armed_state_var=self.armed_state_var)
        self.solenoidPower_toggle.grid(row=4, column=0, pady=10, padx=20)

        self.solenoid5_toggle = LabeledToggle(self.buttonsFrame, id=5, callback=self.arduino.sendCommand, command="04", armed_state_var=self.armed_state_var)
        self.solenoid5_toggle.grid(row=5, column=0, pady=10, padx=20)

        self.solenoid6_toggle = LabeledToggle(self.buttonsFrame, id=6, callback=self.arduino.sendCommand, command="05", armed_state_var=self.armed_state_var)
        self.solenoid6_toggle.grid(row=1, column=1, pady=10, padx=20)

        self.solenoid7_toggle = LabeledToggle(self.buttonsFrame, id=7, callback=self.arduino.sendCommand, command="06", armed_state_var=self.armed_state_var)
        self.solenoid7_toggle.grid(row=2, column=1, pady=10, padx=20)

        self.solenoid8_toggle = LabeledToggle(self.buttonsFrame, id=8, callback=self.arduino.sendCommand, command="07", armed_state_var=self.armed_state_var)
        self.solenoid8_toggle.grid(row=3, column=1, pady=10, padx=20)

        self.solenoid9_toggle = LabeledToggle(self.buttonsFrame, id=9, callback=self.arduino.sendCommand, command="08", armed_state_var=self.armed_state_var)
        self.solenoid9_toggle.grid(row=4, column=1, pady=10, padx=20)

        self.solenoid10_toggle = LabeledToggle(self.buttonsFrame, id=10, callback=self.arduino.sendCommand, command="09", armed_state_var=self.armed_state_var)
        self.solenoid10_toggle.grid(row=5, column=1, pady=10, padx=20)

        self.solenoid11_toggle = LabeledToggle(self.buttonsFrame, id=11, callback=self.arduino.sendCommand, command="10", armed_state_var=self.armed_state_var)
        self.solenoid11_toggle.grid(row=1, column=2, pady=10, padx=20)

        self.solenoid12_toggle = LabeledToggle(self.buttonsFrame, id=12, callback=self.arduino.sendCommand, command="11", armed_state_var=self.armed_state_var)
        self.solenoid12_toggle.grid(row=2, column=2, pady=10, padx=20)

        self.solenoid11_toggle = LabeledToggle(self.buttonsFrame, id=13, callback=self.arduino.sendCommand, command="12", armed_state_var=self.armed_state_var)
        self.solenoid11_toggle.grid(row=3, column=2, pady=10, padx=20)

        self.solenoid12_toggle = LabeledToggle(self.buttonsFrame, id=14, callback=self.arduino.sendCommand, command="13", armed_state_var=self.armed_state_var)
        self.solenoid12_toggle.grid(row=4, column=2, pady=10, padx=20)

        self.clearData_button = tk.Button(self.buttonsFrame, text="Clear Data", command=self.clearData)
        self.clearData_button.grid(row=7, column=0, columnspan=3, pady=20)

    def close(self):
        print("Closing Application") 
        if (hasattr(self, 'arduino')):
            self.arduino.close()
        self.logger.close()
        self.destroy()
    
    def slider(self, name):
        print(name)

    def clearData(self):
        self.plotSet = PlotSet(self)
        self.plotSet.grid(row=0, column=0)


    # The main code loop that runs in the background of the window (Every "frequency" milliseconds)
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
                    self.temperatureReadout.config(text=f'{round(self.arduino.data.T1, 2)}')
                    self.pressureReadout1.config(text=f'{round(self.arduino.data.P1, 2)}')
                    self.pressureReadout2.config(text=f'{round(self.arduino.data.P2, 2)}')
                    self.pressureReadout3.config(text=f'{round(self.arduino.data.P3, 2)}')
                    self.pressureReadout4.config(text=f'{round(self.arduino.data.P4, 2)}')
                    self.lastDisplayTime = currentTime

                # Log data to file
                self.logger.write(time, self.arduino.data)

        except Exception as e:
            print(f"Error Parsing Arduino data: '{e}'")
            import traceback
            traceback.print_exc()
            
        # Run Loop again after "frequency" milliseconds
        self.after(frequency, self.loop, frequency)

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
        self.file.write(f"{time},{data.L1},{data.P1},{data.P2},{data.P3},{data.P4},{data.T1},{data.Safe}\n")

    def close(self):
        self.file.close()

class Data():
        millisSince = 0
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
        print(command)
        # Commands encoded as 2 digit numbers: 1-4 for solenoid number, and 0-1 for off/on
        self.control_list[-int(command[0]+command[1])-1] = int(command[2])
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
  
if __name__ == "__main__":

    serialPort = "COM3"
    #arduino = Arduino(serialPort)
    arduino = ArduinoSim()

    refreshRate = 500 # Ms
    app = App(arduino, refreshRate)
    app.loop(10)
    app.mainloop()