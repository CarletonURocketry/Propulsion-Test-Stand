# Propulsion-Test-Stand
Propulsion's Test Stand Arduino Code



### Description:

This repo contains the code that will be run on two Arduino Mega 2560 rev3s. 

One Arduino (TestStand) will be located at the test stand itself will collect data from pressure transducers, a thermocouple, and the load cell, communicated with the other Arduino, and control the solenoid valves through relays.

The other Arduino (BlastShield) will be located at a safe distance from the test stand and connected to the test stand Arduino through a Cat6 cable. This Arduino will be responsible for recieving and displaying data from the other Arduino as well as passing controls from the blast shield to the test stand.
