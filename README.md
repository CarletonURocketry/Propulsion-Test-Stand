# Propulsion-Test-Stand
Propulsion's Test Stand Arduino Code

This repo contains the code that will be run on two Arduino Mega 2560 rev3s. 

One Arduino (TestStand) will be located at the test stand itself will collect data from pressure transducers, a thermocouple, and the load cell, communicated with the other Arduino, and control the solenoid valves through relays.

The other Arduino (BlastShield) will be located at a safe distance from the test stand and connected to the test stand Arduino through a Cat6 cable. This Arduino will be responsible for recieving and displaying data from the other Arduino as well as passing controls from the blast shield to the test stand.

## Descriptions:
BlastSheld and TestStand contain the main code for the blast shield and test stand ardionos.

BlastSheld_Table_Layout and TestStand_Table_Layout contain modified versions for usage at the table layout (TestStand_Table_Layout has not yet been modified), BlastSheld_Table_Layout has been modified to recieve commands from the UI and pass pressure data to the UI

Table Layout UI contains python code for running a tkinter application that recieves pressure data from the blastshield and sends commands for the four solenoids that can be passed on through the blast shield arduino to the test stand arduino.
