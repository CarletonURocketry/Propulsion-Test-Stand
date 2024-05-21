"""This module is the main module for the web based UI for the test stand control system. It is responsible for creating the UI and updating the UI with the data from the server.
"""
from nicegui import ui
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


danger: bool = True
warning: bool = True
error: bool = True
lastWarnUpdate: float = datetime.timestamp(datetime.now(UTC)) # Time of the last update of the warning icons
warnOn: bool = False # True if any of the warning icons are on
configSent: bool = False

connected = False
lastCommTime: float = 0

# Callback function to update the UI
async def dataUpdate() -> None:
    """Function to send the current state to the server and update the UI with the data recieved from the server
    """
    global connected
    global lastCommTime
    global time
    global t1
    global t2
    global p1
    global p2
    global l1
    global l2
    global danger
    global warning
    global error
    global configSent

    connected_state = False

    sendData: dict[str, dict[str, Any] | str] = dict()
    # Get the data from the server

    if not configSent:
        sendData["type"] = "control"
        sendData["content"] = config

    recvData = await comm.sendData(sendData)

    if type(recvData) == str:
        print(recvData)
        connected_state = False
        connected = False
        configSent = False
        data: dict[str, dict[str, Any]] = dict()
    elif type(recvData) == dict:
        connected_state = True
        connected = True
        configSent = True
        lastCommTime = datetime.timestamp(datetime.now(UTC))
        data = recvData
    else:
        connected_state = False
        connected = False
        configSent = False
        data: dict[str, dict[str, Any]] = dict()
    
    connection_icon.name = {True: 'link_off', False: 'link'}.get(connected, 'link_off')
    connection_icon.update()

    if connected:
        # Update the time
        time = time[1:]
        time.append(round(float(data.get("time", {}).get("elapsedTime", 0.0)), 4))

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
        tempGraph.options['series'][0]['data'] = list(zip(time, t1)) # type: ignore
        tempGraph.options['series'][1]['data'] = list(zip(time, t2)) # type: ignore
        pressureGraph.options['series'][0]['data'] = list(zip(time, p1)) # type: ignore
        pressureGraph.options['series'][1]['data'] = list(zip(time, p2)) # type: ignore
        loadCellGraph.options['series'][0]['data'] = list(zip(time, l1)) # type: ignore
        thrustGraph.options['series'][0]['data'] = list(zip(time, l2)) # type: ignore

        tempGraph.update()
        pressureGraph.update()
        loadCellGraph.update()
        thrustGraph.update()
        
        print('test1')

        # Update the time widgets
        serverUTC = datetime.fromtimestamp(float(data.get('time', {}).get('serverTime', 0)), UTC)
        print(serverUTC)
        serverTime.text = (f"Last Comm Time: {serverUTC.strftime('%H:%M:%S.%f')[:-3]}")
        elapsedTime.text = (f"Elapsed Time: {round(data.get('time', {}).get('elapsedTime', 0), 3)}")


    # Update Connected Status
    if connected:
        connection_icon.name = 'link'
        connection_icon.update()
    else:
        print("Connection Failed")
        connection_icon.name = 'link_off'
        connection_icon.update()

    # Update the valve state widgets
    if connected_state == True:
        print(data.get('valves', {}).get('xv1', False))
        state_xv1 = strToBool.get(data.get('valves', {}).get('xv1', False), False)
        if state_xv1:
            xv1_state_icon.name = 'toggle_on'
            xv1_state_icon.style(replace='color: Green')
            xv1_state_icon.update()
        else:
            xv1_state_icon.name = 'toggle_off'
            xv1_state_icon.style(replace='color: Red')
            xv1_state_icon.update()
        
        state_xv2 = strToBool.get(data.get('valves', {}).get('xv2', False), False)
        if state_xv2:
            xv2_state_icon.name = 'toggle_on'
            xv2_state_icon.style(replace='color: Green')
            xv2_state_icon.update()
        else:
            xv2_state_icon.name = 'toggle_off'
            xv2_state_icon.style(replace='color: Red')
            xv2_state_icon.update()
        
        state_xv3 = strToBool.get(data.get('valves', {}).get('xv3', False), False)
        if state_xv3:
            xv3_state_icon.name = 'toggle_on'
            xv3_state_icon.style(replace='color: Green')
            xv3_state_icon.update()
        else:
            xv3_state_icon.name = 'toggle_off'
            xv3_state_icon.style(replace='color: Red')
            xv3_state_icon.update()

        state_xv4 = strToBool.get(data.get('valves', {}).get('xv4', False), False)
        if state_xv4:
            xv4_state_icon.name = 'toggle_on'
            xv4_state_icon.style(replace='color: Green')
            xv4_state_icon.update()
        else:
            xv4_state_icon.name = 'toggle_off'
            xv4_state_icon.style(replace='color: Red')
            xv4_state_icon.update()

        state_xv5 = strToBool.get(data.get('valves', {}).get('xv5', False), False)
        if state_xv5:
            xv5_state_icon.name = 'toggle_on'
            xv5_state_icon.style(replace='color: Green')
            xv5_state_icon.update()
        else:
            xv5_state_icon.name = 'toggle_off'
            xv5_state_icon.style(replace='color: Red')
            xv5_state_icon.update()

        state_xv6 = strToBool.get(data.get('valves', {}).get('xv6', False), False)
        if state_xv6:
            xv6_state_icon.name = 'toggle_on'
            xv6_state_icon.style(replace='color: Green')
            xv6_state_icon.update()
        else:
            xv6_state_icon.name = 'toggle_off'
            xv6_state_icon.style(replace='color: Red')
            xv6_state_icon.update()

    if connected: 
        # Update the dial widgets
        p1_dial.options['series'][0]['data'][0]['value'] = float(data.get('pressures', {}).get('P1', 0)) # type: ignore
        p1_dial.update()
        p2_dial.options['series'][0]['data'][0]['value'] = float(data.get('pressures', {}).get('P2', 0)) # type: ignore
        p2_dial.update()
        t1_dial.options['series'][0]['data'][0]['value'] = float(data.get('temps', {}).get('T1', 0)) # type: ignore
        t1_dial.update()
    return

async def clockUpdate() -> None:
    """Function to update the client time widget with the current time
    """
    clientTime.text = (f"Client Time: {datetime.now(UTC).strftime('%H:%M:%S.%f')[:-3]}")
    return

async def warnUpdate() -> None:
    """Function to update the warning icon and text
    """
    global warning
    global error
    global danger
    global lastWarnUpdate
    global warnOn

    if (datetime.timestamp(datetime.now(UTC)) - lastWarnUpdate) > 0.3 and not warnOn: # If the warning icons have been off for 3 seconds, turn them on
        if warning: # If there is a warning, turn on the warning icon
            warn_icon.style(replace='color: Orange')
            warn_icon.update()
        else:
            warn_icon.style(replace='color: LightGrey')
            warn_icon.update()
        
        if error: # If there is an error, turn on the error icon
            error_icon.style(replace='color: Gold')
            error_icon.update()
        else:
            error_icon.style(replace='color: LightGrey')
            error_icon.update()
        
        if danger: # If there is a danger, turn on the danger icon
            danger_icon.style(replace='color: Red')
            danger_icon.update()
        else:
            danger_icon.style(replace='color: LightGrey')
            danger_icon.update()
        
        lastWarnUpdate = datetime.timestamp(datetime.now(UTC))
        warnOn = True

    elif (datetime.timestamp(datetime.now(UTC)) - lastWarnUpdate) > 0.3 and warnOn: # If the warning icons have been on for 3 seconds, turn them off
        warn_icon.style(replace='color: LightGrey')
        warn_icon.update()
        error_icon.style(replace='color: LightGrey')
        error_icon.update()
        danger_icon.style(replace='color: LightGrey')
        danger_icon.update()
        lastWarnUpdate = datetime.timestamp(datetime.now(UTC))
        warnOn = False
    elif not warning and not error and not danger: # If there are no warnings, errors, or dangers, turn off the warning icons
        warn_icon.style(replace='color: LightGrey')
        warn_icon.update()
        error_icon.style(replace='color: LightGrey')
        error_icon.update()
        danger_icon.style(replace='color: LightGrey')
        danger_icon.update()
        lastWarnUpdate = datetime.timestamp(datetime.now(UTC))
        warnOn = False
    return

# Set up the page layout and widgets
with ui.row(): # Full Page Layout
    with ui.row().style('height: 80vh'): # Main Layout
        with ui.column().style('width: 75vw'): # Left Layout
            with ui.row().style('height: 6vh'): # Top Bar Layout
                connection_icon = ui.icon('link_off', color='DarkSlateGrey').style('width: 5vw; height: 5vh').classes('content-center text-5xl')
                with ui.column().style('height: 5vh'):
                    serverTime = ui.label('Server Time: 00:00:00.000').style('width: 25vw; height: 2.5vh')
                    clientTime = ui.label('Client Time: 00:00:00.000').style('width: 25vw; height: 2.5vh')
                    ui.space().style('width: 25vw')
                elapsedTime = ui.label('Elapsed Time: ').style('width: 25vw; height: 5vh')

                error_icon = ui.icon('error', color='LightGrey').style('width: 5vw; height: 5vh').classes('content-center text-5xl')

                warn_icon = ui.icon('warning', color='LightGrey').style('width: 5vw; height: 5vh').classes('content-center text-5xl')

                danger_icon = ui.icon('dangerous', color='LightGrey').style('width: 5vw; height: 5vh').classes('content-center text-5xl')
            
            with ui.grid(columns='1fr 1fr').style('width: 75vw; height: 80vh'): # Graph Layout

                tempGraph = ui.echart({'title': {'text': 'Temperature Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Temperature (C)', 'nameLocation': 'middle', 'min': 0, 'max': 40}, 'series': [{'name': 'T1', 'type': 'line', 'data': list(zip(time, t1))}, {'name': 'T2', 'type': 'line', 'data': list(zip(time, t2))}], 'animationDurationUpdate': 0})

                pressureGraph = ui.echart({'title': {'text': 'Pressure Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Pressure (PSI)', 'nameLocation': 'middle', 'min': 0, 'max': 300}, 'series': [{'name': 'P1', 'type': 'line', 'data': list(zip(time, p1))}, {'name': 'P2', 'type': 'line', 'data': list(zip(time, p2))}], 'animationDurationUpdate': 0})

                loadCellGraph = ui.echart({'title': {'text': 'Load Cell Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Load (UNITS)', 'nameLocation': 'middle', 'nameTextStyle': {'padding': 15}}, 'series': [{'name': 'L1', 'type': 'line', 'data': list(zip(time, l1))}], 'animationDurationUpdate': 0})

                thrustGraph = ui.echart({'title': {'text': 'Thrust Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Thrust (N)'}, 'series': [{'name': 'L2', 'nameLocation': 'middle', 'type': 'line', 'data': list(zip(time, l2))}], 'animationDurationUpdate': 0})
        
        with ui.column().style('width: 21vw'): # Right Layout
            with ui.grid(columns='7vw 7vw 7vw').style('height: 25vh'): # Valve State Layout
                ui.label('XV1').style('text-align: center; width: 1fr').classes('w-full')
                ui.label('XV2').style('text-align: center; width: 1fr').classes('w-full')
                ui.label('XV3').style('text-align: center; width: 1fr').classes('w-full')
                xv1_state_icon = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
                xv2_state_icon = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
                xv3_state_icon = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
                ui.label('XV4').style('text-align: center')
                ui.label('XV5').style('text-align: center')
                ui.label('XV6').style('text-align: center')
                xv4_state_icon = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
                xv5_state_icon = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
                xv6_state_icon = ui.icon('toggle_on', color='Green').classes('w-full content-center text-5xl')
            with ui.grid(columns='10.5vw 10.5vw').style('height: 30vh width: 21vw'): # Pressure Dial Layout
                p1_dial = ui.echart({'title': {'text': "P1", 'left': "center", 'top': "20%", 'textStyle': {'fontSize': 12}}, 'detail': {'padding': 100}, 'series': [{'type': 'gauge', 'splitNumber': 5, 'axisLine': {'show': True, 'lineStyle': {'width': 10, 'color': [[0.5, 'LightGreen'], [0.75, 'Orange'], [1, 'Tomato']]}}, 'splitLine': {'show': True, 'length': 5, 'distance': -5}, 'pointer': {'show': False}, 'progress': {'show': True, 'width': 5, 'itemStyle': {'color': 'Grey'}}, 'axisTick': {'show': False}, 'axisLabel': {'show': True, 'color': 'DarkSLateGrey', 'distance': 15, 'fontSize': 8}, 'detail': {'valueAnimation': True, 'formatter': '{value} PSI', 'color': 'inherit', 'offsetCenter': ['0%', '25%'], 'fontSize': 10}, 'radius': '100%', 'min': 0, 'max': 600, 'data': [{'value': 10, 'title': {'offsetCenter': [0, 0]}},]}]}).style('height: 15vh')
                
                p2_dial = ui.echart({'title': {'text': "P2", 'left': "center", 'top': "20%", 'textStyle': {'fontSize': 12}}, 'detail': {'padding': 100}, 'series': [{'type': 'gauge', 'splitNumber': 5, 'axisLine': {'show': True, 'lineStyle': {'width': 10, 'color': [[0.5, 'LightGreen'], [0.75, 'Orange'], [1, 'Tomato']]}}, 'splitLine': {'show': True, 'length': 5, 'distance': -5}, 'pointer': {'show': False}, 'progress': {'show': True, 'width': 5, 'itemStyle': {'color': 'DarkSlateGrey'}}, 'axisTick': {'show': False}, 'axisLabel': {'show': True, 'color': 'DarkSlateGrey', 'distance': 15, 'fontSize': 8}, 'detail': {'valueAnimation': True, 'formatter': '{value} PSI', 'color': 'inherit', 'offsetCenter': ['0%', '25%'], 'fontSize': 10}, 'radius': '100%', 'min': 0, 'max': 600, 'data': [{'value': 10, 'title': {'offsetCenter': [0, 0]}},]}]}).style('height: 15vh')

                t1_dial = ui.echart({'title': {'text': "T1", 'left': "center", 'top': "20%", 'textStyle': {'fontSize': 12}}, 'detail': {'padding': 100}, 'series': [{'type': 'gauge', 'axisLine': {'show': 'false', 'lineStyle': {'width': 10, 'color': [[0.5, 'LightGreen'], [0.7, 'Orange'], [1, 'Tomato']]}}, 'splitLine': {'show': False}, 'pointer': {'show': False}, 'progress': {'show': True, 'width': 5, 'itemStyle': {'color': 'Grey'}}, 'axisTick': {'show': False}, 'axisLabel': {'show': True, 'color': 'DarkSlateGrey', 'distance': -5, 'fontSize': 8}, 'detail': {'valueAnimation': True, 'formatter': '{value}°C', 'color': 'inherit', 'offsetCenter': ['0%', '25%'], 'fontSize': 10}, 'radius': '100%', 'min': 0, 'max': 100, 'data': [{'value': 0, 'title': {'offsetCenter': [0, 0]}},]}]}).style('height: 15vh').classes('col-span-full')

            ui_log = ui.log(max_lines=10).classes('w-full').style('height: 20vh')


dataUpdateTimer = ui.timer(0.25, dataUpdate, active=True)
clockUpdateTimer = ui.timer(0.001, clockUpdate, active=True)
warnUpdateTimer = ui.timer(0.01, warnUpdate, active=True)

ui.run(title='teststand UI', port=5000, favicon='🚀', native=native, reload=True)

lastUpdate = datetime.timestamp(datetime.now(UTC))

#while True:
    #if (datetime.timestamp(datetime.now(UTC)) - lastUpdate) > 1:
        #update()
        #lastUpdate = datetime.timestamp(datetime.now(UTC))
