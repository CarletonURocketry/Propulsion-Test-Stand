import numpy as np
from nicegui import ui
from random import random
import sys
from testStand import log, communication as comm, IO
from datetime import datetime, UTC
import tomllib
from typing import Any



config = tomllib.load(open("config.toml", "rb"))
comm = comm.Client(config.get("server", {}).get("addr", ""), config.get("server", {}).get("port", 0))

io = IO.Control(config.get("switch", {}), config.get("leds", {}))
log = log.LogFile(config.get("data", {}).get("format"), f"control-{config.get("log", {}).get("name")}{datetime.now(UTC).strftime("%y-%m-%d-%H-%M")}.csv", config.get("log", {}).get("path"))

strToBool = {"True": True, "False": False, "true": True, "false": False}

#echart = ui.echart({'xAxis': {'type': 'value'},'yAxis': {'type': 'category', 'data': ['A', 'B'], 'inverse': True}, 'legend': {'textStyle': {'color': 'gray'}},'series': [{'type': 'bar', 'name': 'Alpha', 'data': [0, 0.5]}, {'type': 'bar', 'name': 'Beta', 'data': [0, 2]},],})

if "-v" in sys.argv:
    verbose = True
else:
    sverbose = False
if "-debug" in sys.argv:
    debug = True
else:
    debug = False
if '-native' in sys.argv:
    native = True
else:
    native = False

# Initial Data Values
time: list[float] = [0] * 100
t1: list[float] = [0] * 100
t2: list[float] = [0] * 100
p1: list[float] = [0] * 100
p2: list[float] = [0] * 100
l1: list[float] = [0] * 100
l2: list[float] = [0] * 100

# Callback function to update the UI
def update() -> None:
    """Function to send the current state to the server and update the UI with the data recieved from the server
    """
    sendData: dict[str, dict[str, Any]] = dict()

    # Get the data from the server
    data: dict[str, dict[str, Any]] = comm.sendData(sendData)

    global time
    global t1
    global t2
    global p1
    global p2
    global l1
    global l2

    # Update the time
    time = time[1:]
    time.append(float(data.get("time", {}).get("elapsedTime", 0.0)))

    # Update the temp data
    t1 = t1[1:]
    t1.append(float(data.get("temps", {}).get("T1", 0)))

    # Update the pressure data
    p1 = p1[1:]
    p1.append(float(data.get("pressures", {}).get("P1", 0)))

    p2 = p2[1:]
    p2.append(float(data.get("pressures", {}).get("P2", 0)))

    # Update the load cell data
    l1 = l1[1:]
    l1.append(float(data.get("loads", {}).get("L1", 0)))
        
    # Update the graphs
    tempGraph.options['series'][0]['data'] = list(zip(time, t1))
    tempGraph.options['series'][1]['data'] = list(zip(time, t2))
    pressureGraph.options['series'][0]['data'] = list(zip(time, p1))
    pressureGraph.options['series'][1]['data'] = list(zip(time, p2))
    loadCellGraph.options['series'][0]['data'] = list(zip(time, l1))
    thrustGraph.options['series'][0]['data'] = list(zip(time, l2))

    tempGraph.update()
    pressureGraph.update()
    loadCellGraph.update()
    thrustGraph.update()
        
    # Update the time widgets
    serverTime.text = (f"Last Comm Time: {data.get('time', {}).get('serverTime', 'hh:mm:ss')}")
    clientTime.text = (f"Client Time: {datetime.now(UTC).strftime('%H:%M:%S.%f')[:-3]}")

    #self.elapsedTimeWidget.setText(f"Elapsed Time: {self.data.get('time', {}).get('elapsedTime', 0)}s")

    # Update the valve state widgets
    state = strToBool.get(data.get('valves', {}).get('xv1', 'False'), False)
    if state == True:
        xv1_state.name = 'toggle_on'
        xv1_state.style(replace='color: Green')
        xv1_state.update()
    else:
        xv1_state.name = 'toggle_off'
        xv1_state.style(replace='color: Red')
        xv1_state.update()
    
    state = strToBool.get(data.get('valves', {}).get('xv2', 'False'), False)
    if state == True:
        xv2_state.name = 'toggle_on'
        xv2_state.style(replace='color: Green')
        xv2_state.update()
    else:
        xv2_state.name = 'toggle_off'
        xv2_state.style(replace='color: Red')
        xv2_state.update()
    
    state = strToBool.get(data.get('valves', {}).get('xv3', 'False'), False)
    if state == True:
        xv3_state.name = 'toggle_on'
        xv3_state.style(replace='color: Green')
        xv3_state.update()
    else:
        xv3_state.name = 'toggle_off'
        xv3_state.style(replace='color: Red')
        xv3_state.update()

    state = strToBool.get(data.get('valves', {}).get('xv4', 'False'), False)
    if state == True:
        xv4_state.name = 'toggle_on'
        xv4_state.style(replace='color: Green')
        xv4_state.update()
    else:
        xv4_state.name = 'toggle_off'
        xv4_state.style(replace='color: Red')
        xv4_state.update()

    state = strToBool.get(data.get('valves', {}).get('xv5', 'False'), False)
    if state == True:
        xv5_state.name = 'toggle_on'
        xv5_state.style(replace='color: Green')
        xv5_state.update()
    else:
        xv5_state.name = 'toggle_off'
        xv5_state.style(replace='color: Red')
        xv5_state.update()

    state = strToBool.get(data.get('valves', {}).get('xv6', 'False'), False)
    if state == True:
        xv6_state.name = 'toggle_on'
        xv6_state.style(replace='color: Green')
    else:
        xv6_state.name = 'toggle_off'
        xv6_state.style(replace='color: Red')


    # Update the valve state widgets
    #self.xv1Widget.setText(f"XV1: {self.data.get('valves', {}).get('xv1', 'False')}")
    #self.xv3Widget.setText(f"XV3: {self.data.get('valves', {}).get('xv3', 'False')}")
    #self.xv4Widget.setText(f"XV4: {self.data.get('valves', {}).get('xv4', 'False')}")
    #self.xv5Widget.setText(f"XV5: {self.data.get('valves', {}).get('xv5', 'False')}")
    #self.xv6Widget.setText(f"XV6: {self.data.get('valves', {}).get('xv6', 'False')}")

    tempGraph.update()
    return

# Set up the page layout and widgets

with ui.row(): # Main Layout
    with ui.column().style('width: 75vw'): # Left Layout
        with ui.row().style('height: 10vh'): # Top Layout
            serverTime = ui.label('Server Time: ')
            clientTime = ui.label('Client Time: ')
    
        with ui.grid(columns='1fr 1fr').style('width: 75vw; height: 80vh'): # Graph Layout

            tempGraph = ui.echart({'title': {'text': 'Temperature Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Temperature (C)', 'nameLocation': 'middle', 'min': 0, 'max': 40}, 'series': [{'name': 'T1', 'type': 'line', 'data': list(zip(time, t1))}, {'name': 'T2', 'type': 'line', 'data': list(zip(time, t2))}], 'animationDurationUpdate': 0})

            pressureGraph = ui.echart({'title': {'text': 'Pressure Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Pressure (PSI)', 'nameLocation': 'middle', 'min': 0, 'max': 300}, 'series': [{'name': 'P1', 'type': 'line', 'data': list(zip(time, p1))}, {'name': 'P2', 'type': 'line', 'data': list(zip(time, p2))}], 'animationDurationUpdate': 0})

            loadCellGraph = ui.echart({'title': {'text': 'Load Cell Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Load (UNITS)', 'nameLocation': 'middle', 'nameTextStyle': {'padding': 15}}, 'series': [{'name': 'L1', 'type': 'line', 'data': list(zip(time, l1))}], 'animationDurationUpdate': 0})

            thrustGraph = ui.echart({'title': {'text': 'Thrust Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Thrust (N)'}, 'series': [{'name': 'L2', 'nameLocation': 'middle', 'type': 'line', 'data': list(zip(time, l2))}], 'animationDurationUpdate': 0})
    
    with ui.column().style('width: 21vw'): # Right Layout
        with ui.grid(columns='7vw 7vw 7vw'): # Valve State Layout
            ui.label('XV1').style('text-align: center').classes('w-full')
            ui.label('XV2').style('text-align: center; width: 1fr').classes('w-full')
            ui.label('XV3').style('text-align: center; width: 1fr').classes('w-full')
            xv1_state = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
            xv2_state = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
            xv3_state = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
            ui.label('XV4').style('text-align: center')
            ui.label('XV5').style('text-align: center')
            ui.label('XV6').style('text-align: center')
            xv4_state = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
            xv5_state = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
            xv6_state = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
        with ui.grid(columns='1fr 1fr'): # Pressure Dial Layout
            ui.label('Pressure 1').style('width: 10vw; text-align: center')
            ui.label('Pressure 2').style('width: 10vw; text-align: center')
            p1_dial = ui.circular_progress(value=0, min=0, max=300).style('width: 10vw')
            p2_dial = ui.circular_progress(value=0, min=0, max=300).style('width: 10vw')

        ui_log = ui.log(max_lines=10).classes('w-full h-20')


timer = ui.timer(0.25, update)

ui.run(title='teststand UI', port=5000, favicon='🚀', native=native, reload=debug)
