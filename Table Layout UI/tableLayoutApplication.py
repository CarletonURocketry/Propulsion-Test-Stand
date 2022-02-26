# Tkinter
import tkinter as tk
# Matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
# Serial
from pySerialTransfer import pySerialTransfer as txfer
# Other
import time
from datetime import datetime, timedelta
from random import randint



class Plot(tk.Frame):
    def __init__(self, parent, nb_points):  
        # nb_points: number of points for the graph
        super().__init__(parent)

        # matplotlib figure
        self.figure = Figure(figsize=(12, 4), dpi=100)

        self.ax = self.figure.add_subplot(111)
        # Format the x-axis to show the time
        myFmt = mdates.DateFormatter("%H:%M:%S")
        self.ax.xaxis.set_major_formatter(myFmt)

        # Set initial x and y data (Null Data)
        dateTimeObj = datetime.now() + timedelta(seconds=-nb_points)
        self.x_data = [dateTimeObj + timedelta(seconds=i) for i in range(nb_points)]
        self.y_data = [0 for i in range(nb_points)]

        # Create the plot
        self.plot = self.ax.plot(self.x_data, self.y_data, label='Pressure', marker="o")[0]
        
        # Set default axis limits
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(self.x_data[0], self.x_data[-1])
        
        # Label Axes
        self.ax.set_xlabel('time (hh:mm:ss)')
        self.ax.set_ylabel('pressure (?)') 

        # Auto format date labels
        self.figure.autofmt_xdate()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack()

    def update(self, x_value, y_value):
        # append new data point to the x and y data
        self.x_data.append(x_value)
        self.y_data.append(y_value)

        # remove oldest data point
        self.x_data = self.x_data[1:]
        self.y_data = self.y_data[1:]

        #  update plot data
        self.plot.set_xdata(self.x_data)
        self.plot.set_ydata(self.y_data)
        self.ax.set_xlim(self.x_data[0], self.x_data[-1])
        self.ax.set_ylim(min(self.y_data)-5, max(self.y_data)+5)
        self.canvas.draw_idle()  # redraw plot

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
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.file = open(f"data_{date}.txt", "w")

    def write(self, message):
        self.file.write(message)

    def close(self):
        self.file.close()

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.close)

        # Logger
        self.logger = Logger()
        self.logger.open()
        
        # Root window configuration
        self.title('Table Layout GUI')
        self.geometry('1200x750+200+10')
        self.row = 0

        # Figure
        self.plot = Plot(self, nb_points=600)
        self.plot.grid(row=self.nextRow(), column=0)

        # Pressure Label
        self.pressureReadout = tk.Label(self, text='Pressure', font=("Arial", 10))
        self.pressureReadout.grid(row=self.nextRow(), column=0)

        # Pressure Readout
        self.pressureReadout = tk.Label(self, text='Initalizing...', font=("Arial", 25))
        self.pressureReadout.grid(row=self.nextRow(), column=0)

        # Armed Check
        self.armed_state_var = tk.BooleanVar()
        self.armed_state_var.set(False) #set check state
        self.armed_checkbutton = tk.Checkbutton(self, text='Armed', var=self.armed_state_var)
        self.armed_checkbutton.grid(row=self.nextRow(), column=0)

        # Solenoid Toggles
        self.solenoid1_toggle = LabeledToggle(self, text="Fire", callback=self.sendCommand, command="0", armed_state_var=self.armed_state_var)
        self.solenoid1_toggle.grid(row=self.nextRow(), column=0)

        self.solenoid2_toggle = LabeledToggle(self, text="Fill", callback=self.sendCommand, command="1", armed_state_var=self.armed_state_var)
        self.solenoid2_toggle.grid(row=self.nextRow(), column=0)

        self.solenoid3_toggle = LabeledToggle(self, text="Vent", callback=self.sendCommand, command="2", armed_state_var=self.armed_state_var)
        self.solenoid3_toggle.grid(row=self.nextRow(), column=0)

        self.solenoid4_toggle = LabeledToggle(self, text="Power", callback=self.sendCommand, command="3", armed_state_var=self.armed_state_var)
        self.solenoid4_toggle.grid(row=self.nextRow(), column=0)

    def close(self):
        print("Closing Application") 
        if (hasattr(self, 'arduino')):
            self.arduino.close()
        self.logger.close()
        self.destroy()

    def nextRow(self):
        row = self.row
        self.row += 1
        return row
    
    def sendCommand(self, command):
        # Commands encoded as 2 digit numbers: 1-4 for solenoid number, and 0-1 for off/on
        control_list[-int(command[0])-1] = int(command[1]) 
        control_int = int(str(control_list).strip("[ ]").replace(", ",""),2)
        try:
            send_size = 0
            send_size = link.tx_obj(control_int, send_size)
            link.send(send_size)
        except:
            import traceback
            traceback.print_exc()
               
            link.close()    
            
    # The main code loop that runs in the background of the window (Every "frequency" milliseconds)
    def loop(self, frequency):
        try:
            #Check for received data
            recvData()                
        

            time = datetime.now()
            value = testdata.L1
            self.plot.update(time, value)
            self.pressureReadout.config(text=f'{value}')
            self.logger.write(f"{time},{value}")
        except Exception as e:
            print(f"Error Parsing Arduino data:\n{e}")
            

        # Run Loop again after "frequency" milliseconds
        self.after(frequency, self.loop, frequency)


def recvData():    
    if link.available():
        recSize = 0
        
        testdata.millisSince = link.rx_obj(obj_type='i', start_pos=recSize)
        recSize += txfer.STRUCT_FORMAT_LENGTHS['i']   
        
        testdata.L1 = link.rx_obj(obj_type='f', start_pos=recSize)
        recSize += txfer.STRUCT_FORMAT_LENGTHS['f']
        
        testdata.P1 = link.rx_obj(obj_type='f', start_pos=recSize)
        recSize += txfer.STRUCT_FORMAT_LENGTHS['f']
        
        testdata.P2 = link.rx_obj(obj_type='f', start_pos=recSize)
        recSize += txfer.STRUCT_FORMAT_LENGTHS['f']
        
        testdata.P3 = link.rx_obj(obj_type='f', start_pos=recSize)
        recSize += txfer.STRUCT_FORMAT_LENGTHS['f']
        
        testdata.P4 = link.rx_obj(obj_type='f', start_pos=recSize)
        recSize += txfer.STRUCT_FORMAT_LENGTHS['f']
        
        testdata.T1 = link.rx_obj(obj_type='f', start_pos=recSize)
        recSize += txfer.STRUCT_FORMAT_LENGTHS['f']
        
        testdata.Safe = link.rx_obj(obj_type='b', start_pos=recSize)
        recSize += txfer.STRUCT_FORMAT_LENGTHS['b']
        
        
    
    elif link.status < 0:
        if link.status == txfer.CRC_ERROR:
            print('ERROR: CRC_ERROR')
        elif link.status == txfer.PAYLOAD_ERROR:
            print('ERROR: PAYLOAD_ERROR')
        elif link.status == txfer.STOP_BYTE_ERROR:
            print('ERROR: STOP_BYTE_ERROR')
        else:
            print('ERROR: {}'.format(link.status))    

if __name__ == "__main__":
    #Initialize Serial Link
    try:
        link = txfer.SerialTransfer("COM3")
        link.open()
        time.sleep(2)
        
    except:
        import traceback
        traceback.print_exc()
        
        try:
            link.close()
        except:
            pass
        
    class testdata(object):
        millisSince = 0;
        L1 = 0.0 #Loadcell
        P1 = 0.0 #Don't know
        P2 = 0.0 #Tank Pressure Bottom
        P3 = 0.0 #Tank Pressure Top
        P4 = 0.0 #Don't know
        T1 = 0.0 #Tank Temperature
        Safety = False
    
    control_int = 0
    
    control_list = [0] * 13
    
       
    #
    
    app = App()
    app.loop(10)
    app.mainloop()
