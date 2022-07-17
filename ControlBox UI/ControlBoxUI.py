"""The Test Stand application is intended to be used for the Carleton CUInSpace rocket team test stand
for the new hybrid rocket engine.

Author: Michael Marsland (michaelmarsland@cmail.carleton.ca)
Date: June 11th, 2022
"""

# Tkinter
from cgi import test
from ctypes.wintypes import INT
import tkinter as tk
from tkinter import ttk
from turtle import width
# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
# Serial
from pySerialTransfer import pySerialTransfer as txfer
# Other
from datetime import datetime, timedelta
import numpy as np
import time, os, math, random

#Debuging variables
lastStatus = -1



""" Plot defines the tkinter component for the Pressure and Temperature Plot
"""
class Plot(tk.Frame):
    def __init__(self, parent, data):  
        super().__init__(parent)
        self.plotSet = parent

        # matplotlib figure
        self.figure = plt.Figure(figsize=(8,7.4), dpi=100)
        #Pressure subplot
        self.ax = self.figure.add_subplot(212)
        #Load/Temp subplot
        self.ax2 = self.figure.add_subplot(211)
         
        self.figure.subplots_adjust(left=0.1, bottom=0, right=0.9, top=0.97, wspace=0, hspace=0)
        
        # Label Axes
        self.ax3 = self.ax2.twinx()

        self.ax.set_xlabel('Time (hh:mm:ss)')
        self.ax.set_ylabel('Pressure (PSI)') 
        self.ax2.set_ylabel("Temperature (Degrees C)")
        self.ax3.set_ylabel("Load (N)")

        # Format the x-axis to show the time
        myFmt = mdates.DateFormatter("%H:%M:%S")
        self.ax.xaxis.set_major_formatter(myFmt)
        self.ax2.xaxis.set_major_formatter(myFmt)
        
        #Vertical grid lines
        self.ax.grid(axis = "both")
        self.ax2.grid(axis = "both")

        # Create the plots
        self.pressure1Plot, = self.ax.plot(data[0], data[1], label='Pressure1', color="red")
        self.pressure2Plot, = self.ax.plot(data[0], data[2], label='Pressure2', color="blue")
        self.pressure3Plot, = self.ax.plot(data[0], data[3], label='Pressure3', color="purple")
        self.pressure4Plot, = self.ax.plot(data[0], data[4], label='Pressure4', color="green")

        self.temperaturePlot, = self.ax2.plot(data[0], data[5], label='Temperature', color="red", linestyle="dashed")
        
        self.loadPlot, = self.ax3.plot(data[0], data[6], label='Load', color="blue")

        lns = [self.pressure1Plot, self.pressure2Plot, self.pressure3Plot, self.pressure4Plot]
        labs = [l.get_label() for l in lns]
        self.ax.legend(lns, labs, loc=2)
        
        lns2 = [ self.temperaturePlot, self.loadPlot]
        labs2 = [l2.get_label() for l2 in lns2]
        self.ax2.legend(lns2, labs2, loc=2)

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
        self.loadPlot.set_xdata(data[0])

        self.pressure1Plot.set_ydata(data[1])
        self.pressure2Plot.set_ydata(data[2])
        self.pressure3Plot.set_ydata(data[3])
        self.pressure4Plot.set_ydata(data[4])
        self.temperaturePlot.set_ydata(data[5])
        self.loadPlot.set_ydata(data[6])
            
        self.canvas.draw_idle()  # redraw plot

""" PlotSet defines the tkinter component for the Pressure and Temperature Plot as well as the
controls for the plot including the slider, range, display checkboxes and save plot button.
"""
class PlotSet(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.data = np.zeros((7,0))
        
        self.plot = Plot(self, self.data)
        self.plot.grid(row=0, column=0)

        self.plotButtonsFrame = tk.Frame(self)
        self.plotButtonsFrame.grid(row=0, column=0, sticky="se")

        self.maxDuration = tk.IntVar(value=600)
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
        
        self.displayLoad = tk.IntVar(value=True)
        self.loadCB = tk.Checkbutton(self.plotButtonsFrame, text="Load", variable=self.displayLoad, command=lambda: self.checkboxClicked(6, self.displayLoad))
        self.loadCB.grid(row=2, column=5)
        
        self.clearData_button = tk.Button(self.plotButtonsFrame, text="Clear Data", command=self.clearData)
        self.clearData_button.grid(row=1, column=6)
        
        self.saveButton = tk.Button(self.plotButtonsFrame, text="Save  Plot", command=self.savePlot)
        self.saveButton.grid(row=2, column=6)
    
    def checkboxClicked(self, id, var):
        if (id == 5):
            if (var.get() == False):
                self.plot.ax2.get_yaxis().set_visible(False)
                self.plot.temperaturePlot.set_linestyle("none")
            else:
                self.plot.ax2.get_yaxis().set_visible(True)
                self.plot.temperaturePlot.set_linestyle("dashed")
        elif (id == 6):
            if (var.get() == False):
                self.plot.ax3.get_yaxis().set_visible(False)
                self.plot.loadPlot.set_linestyle("none")
            else:
                self.plot.ax3.get_yaxis().set_visible(True)
                self.plot.loadPlot.set_linestyle("solid")
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
        
    def clearData(self):
        self.data = np.zeros((7,0))

    def update(self, time, data):

        self.data = np.append(self.data, [[time],[data.P1],[data.P2],[data.P3],[data.P4],[data.T1],[data.L1]], axis=1)

        self.slider.update(self.data[0])
        self.plot.update(self.data)   
        if not len(self.data[0]) == 1:
            self.updatePlotLimits()

    def getPlotMinIndex(self, maxIndex):
        currentTime = self.data[0][maxIndex]
        approxMinTime = self.data[0][maxIndex] - timedelta(seconds=self.duration.get())
        minTime = min(self.data[0], key=lambda d: abs(d - approxMinTime))
        return np.where(self.data[0] == minTime)[0][0]
    
    def getMinIndex(self, maxIndex):
        currentTime = self.data[0][maxIndex]
        approxMinTime = self.data[0][maxIndex] - timedelta(seconds=self.maxDuration.get())
        minTime = min(self.data[0], key=lambda d: abs(d - approxMinTime))
        return np.where(self.data[0] == minTime)[0][0]

    def updatePlotLimits(self):
        data = self.data
        maxIndex = self.slider.index
        minPlotIndex = self.getPlotMinIndex(maxIndex) # Get index of oldest data to show in the plot
        
        minIndex = self.getMinIndex(maxIndex) #Get index of data that is too old
        if minIndex > 0: 
            self.data = np.delete(self.data,[0,minIndex,1],1) #Delete old data from memory
            
        self.plot.ax.set_xlim(data[0][minPlotIndex], data[0][maxIndex-minIndex])
        self.plot.ax2.set_xlim(data[0][minPlotIndex], data[0][maxIndex-minIndex])#Resize Plot

        #Make only for shown range
        self.plot.ax.set_ylim(-15, 1000)

        maxTemp = np.max(data[5, minIndex:maxIndex+1])
        minTemp = np.min(data[5, minIndex:maxIndex+1])
        self.plot.ax2.set_ylim(-50, 1000)
        

        self.plot.ax3.set_ylim(-500, 10000)
        
""" ScaleSlider defines the component for the slider for the plot
"""
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
            self.index = self.plotSet.data[0].size - 1
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

""" LabeledToggle defines the component for the toggle switches that are used
to control the solenoid valves
"""
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
        # Replaces the default left click behavior with a right click
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
        # Reads the labels from the labels file
        f = open("labels.csv", "r")
        label = ""
        for l in f:
            if l.split(",")[0] == f"{self.id}":
                label = l.split(",")[1]
        f.close()
        return label

""" App is the main component for the application. It is the main tkinter window as well as
the main running code for the application
"""
class App(tk.Tk):
    def __init__(self, arduino, refreshRate, debug = False):
        super().__init__()

        self.arduino = arduino
        self.lastDisplayTime = datetime.now()
        self.refreshRate = refreshRate
        
        indicators = [[0,"Error","red",1],[0,"Warning","yellow",2],[0,"Waiting","blue",256],[0,"Packet","blue",512],
                [0,"Armed","yellow",4],[0,"Active","yellow",8],[0,"Abort","red",16],[0,"Invalid","red",32],
                [0,"Mismatch","red",1024],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],
                [0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],
                [0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],
                [0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],
                [0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],
                [0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0],[0,"Unused","red",0]]
        
        self.indicators = indicators

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
        
        #Load Readout
        self.loadLabel = tk.Label(self.readoutsFrame, text='Load', font=("Arial", 10))
        self.loadLabel.grid(row=2, column=0, columnspan=2)
        self.loadReadout = tk.Label(self.readoutsFrame, text='Initalizing...', font=("Arial", 25), width=6)
        self.loadReadout.grid(row=3, column=0, columnspan=2)

        # Pressure Readouts
        self.pressureLabel1 = tk.Label(self.readoutsFrame, text='Pressure 1', font=("Arial", 10))
        self.pressureLabel1.grid(row=4, column=0)
        self.pressureReadout1 = tk.Label(self.readoutsFrame, text='Initalizing...', font=("Arial", 25), width=6)
        self.pressureReadout1.grid(row=5, column=0, padx=20)

        self.pressureLabel2 = tk.Label(self.readoutsFrame, text='Pressure 2', font=("Arial", 10))
        self.pressureLabel2.grid(row=4, column=1)
        self.pressureReadout2 = tk.Label(self.readoutsFrame, text='Initalizing...', font=("Arial", 25), width=6)
        self.pressureReadout2.grid(row=5, column=1, padx=20)

        self.pressureLabel3 = tk.Label(self.readoutsFrame, text='Pressure 3', font=("Arial", 10))
        self.pressureLabel3.grid(row=6, column=0)
        self.pressureReadout3 = tk.Label(self.readoutsFrame, text='Initalizing...', font=("Arial", 25), width=6)
        self.pressureReadout3.grid(row=7, column=0, padx=20)

        self.pressureLabel4 = tk.Label(self.readoutsFrame, text='Pressure 4', font=("Arial", 10))
        self.pressureLabel4.grid(row=6, column=1)
        self.pressureReadout4 = tk.Label(self.readoutsFrame, text='Initalizing...', font=("Arial", 25), width=6)
        self.pressureReadout4.grid(row=7, column=1, padx=20)
        
        #Status Indicators
        self.indicatorsFrame = tk.Frame(self.rightFrame)
        self.indicatorsFrame.grid(row=1, column=0 ,columnspan=2, pady=25)

        i = 0
        
        for x in range(32):
            if indicators[x][1] != "Unused":
                indicator = tk.Label(self.indicatorsFrame, text=indicators[x][1], width = 10, height = 2 , border = 5,relief="sunken")
                indicator.grid(column=x%4 , row = i)
                indicators[x][0] = indicator
            if x%4 == 3:
                i += 1
        
        if debug:
            controls = ControlsApp(arduino,250)
            controls.grab_set()
        
        

    def close(self):
        print("Closing Application") 
        if (hasattr(self, 'arduino')):
            self.arduino.close()
        self.logger.close()
        self.destroy()
    
    def slider(self, name):
        print(name)

    # The main code loop that runs in the background of the window (Repeatedly after "frequency" milliseconds)
    def loop(self, frequency):
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
                    self.loadReadout.config(text=f'{round(self.arduino.data.L1, 2)}')
                    self.lastDisplayTime = currentTime

                # Log data to file
                self.logger.write(time, self.arduino.data)

        except Exception as e:
            print(f"Error Parsing Arduino data: '{e}'")
            import traceback
            traceback.print_exc()
            
        # Run Loop again after "frequency" milliseconds
        self.after(frequency, self.loop, frequency)
        
""" ControlsApp is used to send controls from the computer for debugging
"""
class ControlsApp(tk.Toplevel):
    def __init__(self, arduino, refreshRate):
        super().__init__()

        self.arduino = arduino
        self.lastDisplayTime = datetime.now()
        self.refreshRate = refreshRate

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        # Root window configuration
        self.title('Controls GUI')
        self.geometry('500x500')
        self.row = 0

        # Right Hand Frame
        self.rightFrame = tk.Frame(self)
        self.rightFrame.grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1)
        
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

        self.solenoid13_toggle = LabeledToggle(self.buttonsFrame, id=13, callback=self.arduino.sendCommand, command="12", armed_state_var=self.armed_state_var)
        self.solenoid13_toggle.grid(row=3, column=2, pady=10, padx=20)

        self.solenoid14_toggle = LabeledToggle(self.buttonsFrame, id=14, callback=self.arduino.sendCommand, command="13", armed_state_var=self.armed_state_var)
        self.solenoid14_toggle.grid(row=4, column=2, pady=10, padx=20)

    def close(self):
        print("Closing Application") 
        if (hasattr(self, 'arduino')):
            self.arduino.close()
        self.logger.close()
        self.destroy()

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
            
            self.data.L1 = 1000#self.link.rx_obj(obj_type='H', start_pos=recSize)
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
            recSize += 2
            self.data.T1 = (self.data.T1/10) - 273
                       
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
    serialPort = "COM4"
    arduino = Arduino(serialPort)

    # Currently using the ArduinoSim class to test the application with fake data.
    #arduino = ArduinoSim()

    # Refresh Rate is how often the UI readouts are updated to allow for better readability
    refreshRate = 250 # The UI updates every 500 ms
    app = App(arduino, refreshRate, debug = True)
    
    # The app main loop will run repeatedly in a loop with at 10ms delay to allow the UI to update
    app.loop(10)
    app.mainloop()
    