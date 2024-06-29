"""This module is the main module for the web based UI for the test stand control system. It is responsible for creating the UI and updating the UI with the data from the server.
"""
from nicegui import ui
import sys
from testStand import log, communication as comm, IO, svg
from datetime import datetime, UTC
import tomllib
from typing import Any



config = tomllib.load(open("config.toml", "rb"))
comm = comm.Client(config.get("server", {}).get("addr", ""), config.get("server", {}).get("port", 0))

io = IO.Control(config.get("switch", {}), config.get("leds", {}))
log = log.LogFile(config.get("data", {}).get("format"), f"control-{config.get("log", {}).get("name")}{datetime.now(UTC).strftime("%y-%m-%d-%H-%M")}.csv", config.get("log", {}).get("path"))

pidImage = svg.svgEdit("CF2_PID.svg")

strToBool = {"True": True, "False": False, "true": True, "false": False}

#echart = ui.echart({'xAxis': {'type': 'value'},'yAxis': {'type': 'category', 'data': ['A', 'B'], 'inverse': True}, 'legend': {'textStyle': {'color': 'gray'}},'series': [{'type': 'bar', 'name': 'Alpha', 'data': [0, 0.5]}, {'type': 'bar', 'name': 'Beta', 'data': [0, 2]},],})

if "-v" in sys.argv:
    verbose = True
else:
    verbose = False
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

connected: bool = False
lastCommTime: float = 0

data: dict[str, dict[str, Any]] = dict()

noValves = ['xv3', 'xv4']

ncValves = ['xv1', 'xv2']

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
    global data

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
        data = dict()
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
        data = dict()
    
    connection_icon.name = {True: 'link_off', False: 'link'}.get(connected, 'link_off')
    connection_icon.update()

    if connected:
        # Update the time
        time = time[1:]
        time.append(round(float(data.get("time", {}).get("elapsedTime", 0.0)), 3))

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
        print(data.get('relays', {}).get('xv1', False))
        state_xv1 = strToBool.get(data.get('relays', {}).get('xv1', False), False)
        if state_xv1:
            xv1_state_icon.name = 'toggle_on'
            xv1_state_icon.style(replace='color: Green')
            xv1_state_icon.update()
        else:
            xv1_state_icon.name = 'toggle_off'
            xv1_state_icon.style(replace='color: Red')
            xv1_state_icon.update()
        
        state_xv2 = strToBool.get(data.get('relays', {}).get('xv2', False), False)
        if state_xv2:
            xv2_state_icon.name = 'toggle_on'
            xv2_state_icon.style(replace='color: Green')
            xv2_state_icon.update()
        else:
            xv2_state_icon.name = 'toggle_off'
            xv2_state_icon.style(replace='color: Red')
            xv2_state_icon.update()
        
        state_xv3 = strToBool.get(data.get('relays', {}).get('xv3', False), False)
        if state_xv3:
            xv3_state_icon.name = 'toggle_on'
            xv3_state_icon.style(replace='color: Green')
            xv3_state_icon.update()
        else:
            xv3_state_icon.name = 'toggle_off'
            xv3_state_icon.style(replace='color: Red')
            xv3_state_icon.update()

        state_xv4 = strToBool.get(data.get('relays', {}).get('xv4', False), False)
        if state_xv4:
            xv4_state_icon.name = 'toggle_on'
            xv4_state_icon.style(replace='color: Green')
            xv4_state_icon.update()
        else:
            xv4_state_icon.name = 'toggle_off'
            xv4_state_icon.style(replace='color: Red')
            xv4_state_icon.update()

        state_xv5 = strToBool.get(data.get('relays', {}).get('xv5', False), False)
        if state_xv5:
            xv5_state_icon.name = 'toggle_on'
            xv5_state_icon.style(replace='color: Green')
            xv5_state_icon.update()
        else:
            xv5_state_icon.name = 'toggle_off'
            xv5_state_icon.style(replace='color: Red')
            xv5_state_icon.update()

        state_xv6 = strToBool.get(data.get('relays', {}).get('xv6', False), False)
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

async def pidUpdate() -> None:
    """_summary_

    Returns:
        _type_: _description_
    """
    global noValves
    global ncValves
    openValves: list[str] = []
    closedValves: list[str] = []

    for valve in noValves:
        print(valve)
        if strToBool.get(data.get('relays', {}).get(valve, False), False):
            closedValves.append(valve)
        else:
            openValves.append(valve)
    for valve in ncValves:
        print(valve)
        #print(type(data.get('relays', {}).get(valve, False)))
        if strToBool.get(data.get('relays', {}).get(valve, False), False):
            openValves.append(valve)
        else:
            closedValves.append(valve)
    
    print(openValves)
    print(closedValves)
    
    pidImage.changeColor(openValves, 'red')
    #closedValves.append('xv1')
    #openValves.append('xv2')
    #openValves.append('xv3')
    #openValves.append('xv4')
    pidImage.changeColor(closedValves, 'green')

    #print(pidImage.changeColor(openValves, 'red'))

    pidImageHTML.content = pidImage.returnStr().decode() #type: ignore
    #pidImageHTML.content = pidImage.changeColor(closedValves, 'green').decode()
    pidImageHTML.update()
    #pidImageWidget.set_source('UI_PID.svg')
    #pidImageWidget.update()

# Set up the page layout and widgets
with ui.column(): # Full Page Layout
    with ui.row().style('height: 6vh'): # Top Bar Layout
        connection_icon = ui.icon('link_off', color='DarkSlateGrey').style('width: 4vw; height: 5vh').classes('content-center text-5xl')
        with ui.column().style('height: 5vh'):
            serverTime = ui.label('Server Time: 00:00:00.000').style('width: 15vw; height: 2.5vh')
            clientTime = ui.label('Client Time: 00:00:00.000').style('width: 15vw; height: 2.5vh')
        elapsedTime = ui.label('Elapsed Time: ').style('width: 15vw; height: 5vh')

        with ui.tabs().style('width: 20vw') as tabs:
            graphTab = ui.tab('Graphs', label='Graphs', icon='show_chart')
            checkListTab = ui.tab('Checklist', label='Checklist', icon='checklist')
            pidTab = ui.tab('P&ID', label='P&ID', icon='engineering')

        ui.space().style('width: 5vw')

        error_icon = ui.icon('error', color='LightGrey').style('width: 5vw; height: 5vh').classes('content-center text-5xl')

        warn_icon = ui.icon('warning', color='LightGrey').style('width: 5vw; height: 5vh').classes('content-center text-5xl')

        danger_icon = ui.icon('dangerous', color='LightGrey').style('width: 5vw; height: 5vh').classes('content-center text-5xl')

    with ui.row().style('height: 80vh'): # Main Layout
        with ui.column().style('width: 74vw'): # Left Layout

            with ui.tab_panels(tabs, value=graphTab).style('width: 74vw'):
                with ui.tab_panel(graphTab):
                    with ui.grid(columns='1fr 1fr').style('width: 73vw; height: 80vh'): # Graph Layout

                        tempGraph = ui.echart({'title': {'text': 'Temperature Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Temperature (C)', 'nameLocation': 'middle', 'min': 0, 'max': 40}, 'series': [{'name': 'T1', 'type': 'line', 'data': list(zip(time, t1))}, {'name': 'T2', 'type': 'line', 'data': list(zip(time, t2))}], 'animationDurationUpdate': 0}).style('width: 35vw')

                        pressureGraph = ui.echart({'title': {'text': 'Pressure Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Pressure (PSI)', 'nameLocation': 'middle', 'min': 0, 'max': 300}, 'series': [{'name': 'P1', 'type': 'line', 'data': list(zip(time, p1))}, {'name': 'P2', 'type': 'line', 'data': list(zip(time, p2))}], 'animationDurationUpdate': 0}).style('width: 35vw')

                        loadCellGraph = ui.echart({'title': {'text': 'Load Cell Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Load (UNITS)', 'nameLocation': 'middle', 'nameTextStyle': {'padding': 15}}, 'series': [{'name': 'L1', 'type': 'line', 'data': list(zip(time, l1))}], 'animationDurationUpdate': 0}).style('width: 35vw')

                        thrustGraph = ui.echart({'title': {'text': 'Thrust Graph'}, 'legend': {}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': 'true'}, 'xAxis': {'name': 'Time (s)', 'nameLocation': 'middle', 'min': 'dataMin', 'max': 'dataMax'}, 'yAxis': {'name': 'Thrust (N)'}, 'series': [{'name': 'L2', 'nameLocation': 'middle', 'type': 'line', 'data': list(zip(time, l2))}], 'animationDurationUpdate': 0}).style('width: 35vw')

                with ui.tab_panel(checkListTab).style('width: 74vw'):
                    with ui.scroll_area().style('width: 74vw; height: 80vh'):
                        ui.label('1. LEAK TEST PROCEDURE').style('text-align: center').classes('w-full')

                        ui.checkbox('1.1.0: PROP Verify Test Stand Assembly has been completed to satisfaction and leak testing is ready to commence').classes('w-full')
                        ui.checkbox('1.2.0: PAD: Remove FOD caps from all vent lines and place in a clean bag. Turn the valve on the nitrous run tank to OPEN position.')
                        ui.checkbox('1.3.0: CONTROL: Set all valves to closed position (XV-2, XV-4, XV-5 on, XV-1, XV-3 off)')
                        ui.checkbox('1.4.0: PAD: Put on face safety glasses, cut resistant gloves , a face shield and hearing protection.')
                        ui.checkbox('1.5.0: PAD: Set the regulator on the nitrogen tank to 250 psi. ')
                        ui.checkbox('1.5.1: PAD: Move the smaller black knob to the “on” position on the side of the tank .')
                        ui.checkbox('1.5.2: PAD: Move the larger knob (regulator) dial until you reach the 250psi position facing straight up.')
                        ui.checkbox('1.6.0: TIDO: Read the pressure on PI-1. Hold ')
                        ui.checkbox('1.7.0: CONTROL: Open XV-6.')
                        ui.checkbox('1.8.0: TIDO: Read the pressure on PI-1.')
                        ui.checkbox('1.8.1: CONTROL: If pressure raises above 300 psi vent from XV-2').classes('indent-8')
                        ui.checkbox('ABORT 1A: If the pressure rises above 450 psi abort.').classes('indent-16')
                        ui.checkbox('1.9.0: PAD: Check the system for leaks')
                        ui.checkbox('1.9.1: CONTROL: Close XV-6').classes
                        ui.checkbox('1.9.2: TIDO: Read Pressure Transducers and announce leak rate (psi/s).').classes('indent-8')
                        ui.checkbox('1.9.3: PAD: If a loud leak sound is heard check XV-2 by holding a piece of paper in front of its outlet. If the valve is still leaking adjust the poppet tensioning screw on the bottom of the valve and the bix hex on the bottom of the valve.').classes('indent-8').style('width: 70vw')
                        ui.checkbox('1.9.3.1 TIDO: Announce changes in leak rate due to tensioning of valve.').classes('indent-16')
                        ui.checkbox('1.9.4: PAD: Spray each individual fitting before XV-3 with leak detection fluid. If bubbles are observed torque the fitting further until bubbles disappear. Mark each fitting after testing.').classes('indent-8').style('width: 70vw')
                        ui.checkbox('1.9.4.1: TIDO: If any fittings are torqued, Announce any change in leak rate').classes('indent-16')
                        ui.checkbox('1.9.5: PAD: If bubbles cannot be completely eliminated take note of the leaking fitting in question.').classes('indent-8')
                        ui.checkbox('1.9.6: PAD: If XV-2 continues to leak audibly proceed to ABORT 1A').classes('indent-8')
                        ui.checkbox('1.9.7: TIDO: If the pressure falls below 150 psi return to 1.6.0').classes('indent-8')
                        ui.checkbox('1.10.0: CONTROL: Open and close XV-6 to re-pressurize the system and wait 10 minutes. TIDO takes note of the drop in pressure that occurs over the time period. (acceptable fill system leak rate is 2psi/min)').style('width: 70vw')
                        ui.checkbox('1.11.0: CONTROL: Open XV-6 and XV-3')
                        ui.checkbox('1.12.0: TIDO: Once system reaches 200 psi CONTROL close XV-6 and XV-3')
                        ui.checkbox('1.12.1: TIDO: If pressure rises above 300 psi CONTROL vent from XV-2').classes('indent-8')
                        ui.checkbox('ABORT 1A: If the pressure rises above 450 psi abort.').classes('indent-16')
                        ui.checkbox('1.13.0: PAD: Check the system for leaks')
                        ui.checkbox('1.13.1: CONTROL: Close XV-6 and XV-3  and monitor pressure on pressure transducers').classes('indent-8')
                        ui.checkbox('1.13.2: TIDO: Read Pressure Transducers and announce leak rate (psi/s).').classes('indent-8')
                        ui.checkbox('1.13.3: PAD: If a loud leak sound is heard check XV-4 and XV-5 by holding a glove in front of its outlet. If the valves are still leaking adjust the poppet tensioning screw on the bottom of the valve.').classes('indent-8').style('width: 70vw')
                        ui.checkbox('1.13.3.1 TIDO: Announce changes in leak rate due to tensioning of valve.').classes('indent-16')
                        ui.checkbox('1.13.4: PAD: Spray each individual fitting after XV-3 with leak detection fluid. If bubbles are observed torque the fitting further until bubbles disappear. Mark each fitting after testing.').classes('indent-8').style('width: 70vw')
                        ui.checkbox('1.13.4.1: TIDO: If any fittings are torqued, Announce any change in leak rate').classes('indent-16')
                        ui.checkbox('1.13.5: PAD If bubbles cannot be completely eliminated take note of the leaking fitting in question. **Acceptable rate of leak is approximately 1 psi/min').classes('indent-8')
                        ui.checkbox('1.13.6: PAD If XV-4 and/or XV-5 continue to leak audibly proceed to ABORT 1A').classes('indent-8')
                        ui.checkbox('1.13.8: TIDO: If the pressure falls below 150 psi return to step 1.6.0').classes('indent-8')
                        ui.checkbox('1.14.0: CONTROL: Open and close XV-6 and XV-3  to re-pressurize the system and wait 10 minutes. TIDO takes note of the drop in pressure that occurs over the time period.').style('width: 70vw')
                        ui.checkbox('1.15.0: PAD Close the nitrogen tank valve and put the regulator back into the closed position.')
                        ui.checkbox('1.16.0: CONTROL Shut power to all solenoid valves and allow the system to depressurize.')

                        ui.label('2. PRE-PRESSURIZATION PROCEDURE').style('text-align: center').classes('w-full')
                        ui.checkbox('2.1.0: PAD Confirm the oxidizing tank is open, allowing flow to the vent section')
                        ui.checkbox('2.1.1: TIDO Verify PI-1 and PI-2 are reading zero gauge pressure. (+/- 10 psi acceptable).').classes('indent-8')
                        ui.checkbox('Abort 2A: PI-1 and/or PI-2 is indicating the system is pressurizing.').classes('indent-16')
                        ui.checkbox('2.2.0: TIDO Verify all systems are depressurized. TI-1 is indicating ambient temperatures based on the current weather condition (approximately 15-20°C). PI-1 and PI-2 are indicating approximately 0 psig. (Atmospheric conditions, +/- 10 psig acceptable).').style('width: 70vw')
                        ui.checkbox('Abort 2A: TI-1, PI-1, and/or PI-2 are indicating the system is not depressurized.')
                        ui.checkbox('2.3.0: PAD Set the nitrogen tank regulator to 665 psig. Slowly open HV-2 (⅛ crack) to pressurize between HV-2 and XV-6. XV-6 should be closed and isolating nitrogen gas from the rest of the system.').style('width: 70vw')
                        ui.checkbox('2.3.1: TIDO Verify PI-1 is reading zero gauge pressure. (+/- 10 psi acceptable).').classes('indent-8')
                        ui.checkbox('Abort 2A: PI-1 is indicating the system is pressurizing.').classes('indent-16')
                        ui.checkbox('2.4.0: PROP and PAD Leave the test stand and take the safety key from the test stand control box. Join with TIDO and CONTROL at the minimum safety distance of 80m.').style('width: 70vw')
                        ui.checkbox('2.4.1: CONTROL Arm switch control box with the key. Valves are now live. No one should be near the test stand.').classes('indent-8')
                        ui.checkbox('2.5.0: CONTROL Open XV-6 to pressurize the fill system, between XV-1 and XV-3.')
                        ui.checkbox('2.5.1: TIDO Verify PI-1 is increasing to a range of 665 - 758 psig (+/- 10 psi acceptable) - Pressure should be at a difference of 73 psi with the expected CO2 pressures (738 - 831 psig, depending on temperature of CO2)').classes('indent-8')
                        ui.checkbox('ABORT 2A: PI-1 is indicating values outside of the expected range and cannot be addressed by pulsing XV-2 or XV-6.').classes('indent-16')
                        ui.checkbox('2.6.0: CONTROL Open XV-3 to pressurize the entire system. XV-2, XV-4, and XV-5 should be closed at this point.')
                        ui.checkbox('2.6.1: TIDO Verify PI-2 is increasing to a range of 665 - 758 psig (+/- 10 psi acceptable) - Pressure should be at a difference of 73 psi with the expected CO2 pressures (738 - 831 psig, depending on temperature of CO2)').classes('indent-8').style('width: 70vw')
                        ui.checkbox('ABORT 2A: PI-2 is indicating values outside of the expected range and cannot be fixed by pulsing XV-6, XV-3 or XV-4 and XV-5.').classes('indent-16')
                        ui.checkbox('2.7.0: CONTROL Close XV-3 and XV-6 to isolate the nitrogen tank, fill, and run system.')
                        ui.checkbox('2.8.0: Hold for 5 minutes at pressure to confirm there are no leaks (1 psi/min leak rate acceptable). All valves should be closed.')
                        ui.checkbox('2.8.1: TIDO Verify PI-1 and PI-2 are holding near constant pressure').classes('indent-8')
                        ui.checkbox('ABORT 2C: PI-1 and PI-2 are indicating values outside the expected range (rapidly increasing or decreasing)').classes('indent-16')
                        ui.label('HOLD POINT:')
                        ui.checkbox('2.9.0: PROP and TIDO verify the following checklist:')
                        with ui.grid(columns='auto auto auto'):
                            ui.label('Sensor').style('text-align: center')
                            ui.label('Acceptable Range').style('text-align: center')
                            ui.label('Acceptable?').style('text-align: center')

                            ui.label('PI-1').style('text-align: center')
                            ui.label('665 - 758 psig').style('text-align: center')
                            ui.checkbox()

                            ui.label('PI-2').style('text-align: center')
                            ui.label('665 - 758 psig').style('text-align: center')
                            ui.checkbox()
                        ui.checkbox('ABORT 2C: Any of the above sensors are not within the expected range').classes('indent-8')

                        ui.label('3. LOADING PROCEDURE').style('text-align: center').classes('w-full')
                        ui.checkbox('3.1.0: Have one person start recording the time it takes to load the oxidizing tank.')
                        ui.checkbox('3.2.0: CONTROL Open XV-1, pressurizing the fill system up to XV-3.')
                        ui.checkbox('3.2.1: TIDO Verify PI-1 has increased by approximately 73 psi (+/- 10 psi acceptable)')
                        ui.checkbox('ABORT 3A: PI-2 is indicating the vent/run system is pressurizing')
                        ui.checkbox('ABORT 3B: PI-1 is indicating values outside of the expected range.')
                        ui.checkbox('3.3.0: CONTROL Maintain fill system pressure by pulsing XV-2.')
                        ui.checkbox('3.3.1: TIDO Verify PI-1 is maintaining an approximate constant pressure within the expected range of 738 - 831 psig. (+/- 10 psi acceptable)')
                        ui.checkbox('ABORT 3B: PI-1 is indicating values outside of the expected range.')
                        ui.checkbox('3.4.0: CONTROL Open XV-3 and XV-5 to begin filling the oxidizing tank. Gaseous CO2 will begin to exit XV-5 due to boil off.')
                        ui.checkbox('3.4.1: TIDO Verify PI-2 has increased to approximately the same pressure as PI-1')
                        ui.checkbox('ABORT 3C: PI-2 is not increasing in pressure')
                        ui.checkbox('3.4.2: CONTROL Pulse XV-5 to maintain run system pressure')
                        ui.checkbox('3.4.3: TIDO Verify the load cell is increasing to the expected weight of 7-9 kg.')
                        ui.checkbox('ABORT 3D: The load cell is indicating no increase in weight after at least 3 minutes')
                        ui.checkbox('3.5.0: PROP Visually verify the oxidizing tank has completed filling when liquid carbon dioxide exits XV-5.')
                        ui.checkbox('3.5.1: TIDO Verify PI-2 is maintaining pressure within the expected range of 738 - 831 psig (+/- 10 psi acceptable)')
                        ui.checkbox('ABORT 3B: PI-2 is indicating values outside of the expected range')
                        ui.checkbox('3.6.0: CONTROL Close XV-1 and XV-3 to isolate the source tank, fill and run system.')
                        ui.checkbox('3.7.0: CONTROL Leave XV-2 open to vent the fill system')
                        ui.checkbox('3.7.1: TIDO Verify PI-1 is decreasing')
                        ui.checkbox('3.7.1: TIDO Verify PI-2 is reading steady pressure (1psi/min leak rate acceptable)')
                        ui.checkbox('ABORT 3E: PI-1 is not indicating depressurization')
                        ui.checkbox('3.8.0: Stop loading timer here.')
                        ui.label('HOLD POINT:')
                        ui.checkbox('3.9.0: PROP and TIDO verify the following checklist:')
                        with ui.grid(columns='auto auto auto'):
                            ui.label('Sensor')
                            ui.label('Acceptable Range')
                            ui.label('Acceptable?')
                            ui.label('TI-1')
                            ui.label('10 - 20°C')
                            ui.checkbox()
                            ui.label('PI-1')
                            ui.label('0 - 10 psig')
                            ui.checkbox()
                            ui.label('PI-2')
                            ui.label('738 - 831 psig')
                            ui.checkbox()

                        ui.label('4. FIRE PROCEDURE')
                        ui.checkbox('4.1.0: PROP Verify there are no personnel or passerbys within the minimum safety distance of the test stand.')
                        ui.checkbox('4.2.0: PROP Verify HOLD POINT 3.9.0 has been completed')
                        ui.checkbox('4.3.0: CONTROL Close XV-5.')
                        ui.checkbox('4.4.0: PROP Instruct CONTROL to open CV-1 and fire the oxidizing tank.')
                        ui.checkbox('4.4.1: Once CO2 has discharged from system, TIDO verifies PI-2 has decreased to approximately 0 psig. (+/- 10 psi acceptable)')
                        ui.checkbox('4.5.0: CONTROL Leave XV-1 closed and CV-1 open. Open all other valves to vent system')
                        ui.checkbox('4.5.1: CONTROL Open XV-6 for approximately 10 seconds to purge system with nitrogen gas.')
                        ui.checkbox('4.5.2: TIDO Monitor PI-1 and PI-2 during the purging.')
                        ui.checkbox('4.6.0: CONTROL Close XV-6')
                        ui.checkbox('4.6.1: TIDO Verify PI-1 and PI-2 are indicating ambient pressures, i.e., approximately 0 psig.')
                        ui.checkbox('4.7.0: CONTROL Ensure all valves are returned to their normal positions (i.e., XV-2, XV-4, and XV-5 open, XV-1, XV-3, XV-6, CV-1 closed)')
                        ui.checkbox('4.7.1: TIDO Verify PI-1 and PI-2 are indicating ambient pressures, i.e., approximately 0 psig.')
                        ui.checkbox('4.8.0: PROP Confirm PI-1 and PI-2 are reading ambient pressure. It should now be safe to return to the test stand and return the safety key to the test stand control box.').style('width: 70vw')

                        ui.label('5. POST-FIRING PROCEDURE').style('text-align: center; width: 1fr').classes('w-full')
                        ui.checkbox('5.1.0: PROP and PAD return to the test stand and return the safety key to the test stand control box.')
                        ui.checkbox('5.1.1: TIDO Monitor PI-1 and PI-2 and reading ambient pressures').style('text-align: center; width: 1fr').classes('indent-8')
                        ui.checkbox('5.2.0: PROP and PAD Close HV-1 on the CO2 source tank')
                        ui.checkbox('5.3.0: PROP and PAD Set the regulator on the nitrogen tank to 0 psig and close HV-2.')
                        ui.checkbox('5.4.0: PROP and PAD Disconnect the CO2 source tank. Confirm it is now safe for the rest of personnel to join at the test stand and commence disassembly.')
                    
                with ui.tab_panel(pidTab).style('width: 74vw'):
                    #pidImageWidget = ui.interactive_image('UI_PID.png').style('width: 70vw; height: 80vh')
                    #ui.image('CF2_PID.svg').style('width: 70vw; height: 80vh')
                    pidImage = svg.svgEdit("CF2_PID.svg")
                    pidStr = pidImage.returnStr().decode() #type: ignore

                    pidImageHTML = ui.html(pidStr).style('width: 70vw; height: 80vh; max-width: 70vw').classes('object-scale-down')
                    pidImageHTML.update()

        with ui.column().style('width: 21vw'): # Right Layout
            with ui.grid(columns='7vw 7vw 7vw').style('width: 21vw; height: 20vh'):
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
            
            ui.space().style('height: 4vh')
            with ui.grid(columns='10.5vw 10.5vw').style('height: 30vh width: 21vw'): # Pressure Dial Layout
                p1_dial = ui.echart({'title': {'text': "P1", 'left': "center", 'top': "20%", 'textStyle': {'fontSize': 12}}, 'detail': {'padding': 100}, 'series':[{'type': 'gauge', 'splitNumber': 5, 'axisLine': {'show': True, 'lineStyle': {'width': 10, 'color': [[0.5, 'LightGreen'], [0.75, 'Orange'], [1, 'Tomato']]}}, 'splitLine': {'show': True, 'length': 5, 'distance': -5}, 'pointer': {'show': False}, 'progress': {'show': True, 'width': 5, 'itemStyle': {'color': 'Grey'}}, 'axisTick': {'show': False}, 'axisLabel': {'show': True, 'color': 'DarkSLateGrey', 'distance': 15, 'fontSize': 8}, 'detail': {'valueAnimation': True, 'formatter': '{value} PSI', 'color': 'inherit', 'offsetCenter': ['0%', '25%'], 'fontSize': 10}, 'radius': '100%', 'min': 0, 'max': 600, 'data': [{'value': 10, 'title': {'offsetCenter': [0, 0]}},]}]}).style('height: 15vh')
                        
                p2_dial = ui.echart({'title': {'text': "P2", 'left': "center", 'top': "20%", 'textStyle': {'fontSize': 12}}, 'detail': {'padding': 100}, 'series': [{'type': 'gauge', 'splitNumber': 5, 'axisLine': {'show': True, 'lineStyle': {'width': 10, 'color': [[0.5, 'LightGreen'], [0.75, 'Orange'], [1, 'Tomato']]}}, 'splitLine': {'show': True, 'length': 5, 'distance': -5}, 'pointer': {'show': False}, 'progress': {'show': True, 'width': 5, 'itemStyle': {'color': 'DarkSlateGrey'}}, 'axisTick': {'show': False}, 'axisLabel': {'show': True, 'color': 'DarkSlateGrey', 'distance': 15, 'fontSize': 8}, 'detail': {'valueAnimation': True, 'formatter': '{value} PSI', 'color': 'inherit', 'offsetCenter': ['0%', '25%'], 'fontSize': 10}, 'radius': '100%', 'min': 0, 'max': 600, 'data': [{'value': 10, 'title': {'offsetCenter': [0, 0]}},]}]}).style('height: 15vh')

                t1_dial = ui.echart({'title': {'text': "T1", 'left': "center", 'top': "20%", 'textStyle': {'fontSize': 12}}, 'detail': {'padding': 100}, 'series': [{'type': 'gauge', 'axisLine': {'show': 'false', 'lineStyle': {'width': 10, 'color': [[0.5, 'LightGreen'], [0.7, 'Orange'], [1, 'Tomato']]}}, 'splitLine': {'show': False}, 'pointer': {'show': False}, 'progress': {'show': True, 'width': 5, 'itemStyle': {'color': 'Grey'}}, 'axisTick': {'show': False}, 'axisLabel': {'show': True, 'color': 'DarkSlateGrey', 'distance': -5, 'fontSize': 8}, 'detail': {'valueAnimation': True, 'formatter': '{value}°C', 'color': 'inherit', 'offsetCenter': ['0%', '25%'], 'fontSize': 10}, 'radius': '100%', 'min': 0, 'max': 100, 'data': [{'value': 0, 'title': {'offsetCenter': [0, 0]}},]}]}).style('height: 15vh').classes('col-span-full')

            ui_log = ui.log(max_lines=10).classes('w-full').style('height: 20vh')


dataUpdateTimer = ui.timer(0.25, dataUpdate, active=True)
clockUpdateTimer = ui.timer(0.05, clockUpdate, active=True)
warnUpdateTimer = ui.timer(0.01, warnUpdate, active=True)
pidUpdateTimer = ui.timer(1, pidUpdate, active=True)

ui.run(title='teststand UI', port=5000, favicon='🚀', native=native, reload=True)

