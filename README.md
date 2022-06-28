# Propulsion-Test-Stand
Propulsion's Test Stand Arduino Code

This repo contains the code that will be run on two Arduino Mega 2560 rev3s. 

One Arduino (TestStand) will be located at the test stand itself will collect data from pressure transducers, a thermocouple, and the load cell, communicated with the other Arduino, and control the solenoid valves through relays.

The other Arduino (BlastShield) will be located at a safe distance from the test stand and connected to the test stand Arduino through a Cat6 cable. This Arduino will be responsible for receiving and displaying data from the other Arduino as well as passing controls from the blast shield to the test stand.

## Descriptions:
BlastSheld and TestStand contain the main code for the blast shield and test stand Ardionos.

Test Stand UI contains python code for running a Tkinter application that receives pressure data from the BlastShield and sends commands for the four solenoids that can be passed on through the blast shield arduino to the test stand arduino.

### Test Stand UI
The Test Stand UI application can be run through python by installing the required libraries (Tkinter, etc...) via pip and running the testStandApplication.py with Python. The application will collect data, log it to a file, display the data in readouts and a plot as well as allow the user to control the solenoids.

The Test Stand UI currently looks like this:
![alt text](Test%20Stand%20UI/GUI_Example.png)
