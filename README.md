# Propulsion-Test-Stand
Propulsion's Test Stand Arduino Code

This repo contains the code that will be run on two Arduino Mega 2560 rev3s. 

One Raspberry Pi (testSide) will be located at the test stand itself will collect data from pressure transducers, a thermocouple, and the load cell, communicates with the other Arduino, and control the solenoid valves through relays.

The other Raspberry Pi (control) will be located at a safe distance from the test stand and connected to the testSide through a network connection. This Pi will be responsible for receiving and displaying data from the other Arduino as well as passing controls from the blast shield to the test stand.

## Descriptions:
testSide.py contains the main code for the test side Pi and control.py contains the main code for the control side Pi. Both these scripts depend heavily on the scripts located in the testStand

testStand/UI.py contains the code for a PyQt GUI application started by control.py that receives data from the test side arduino and sends commands for the solenoids that can be passed on to the test side Pi through a network connection.

## Running
To run this code on a non Raspberry Pi machine: Fro0m terminals in the directory you copied this code to enter ```python control.py -debug``` in one terminal and ```python testSide.py``` in the other.

## Installation
### Dependencies
- Python 3.11+ (Tested with Python 3.12.3)
- All other dependencies can be installed with ```pip install -r requirments.txt```

