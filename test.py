from testStand import svg
from nicegui import ui

pidImage = svg.svgEdit("CF2_PID.svg")

pidStr = pidImage.changeColor(["xv1"], "red").decode()
color = "green"

with ui.column():
    pidImageHTML = ui.html(pidStr).classes('object-scale-down w-full')




def updateColor():
    global color
    
    if color == "red":
        pidStr = pidImage.changeColor(["xv1"], color).decode()
        color = "green"
        pidStr = pidImage.changeColor(["xv2"], color).decode()
        pidImageHTML.content = pidStr
        print("1")
    else:
        color = "green"
        pidStr = pidImage.changeColor(["xv1"], color).decode()
        color = "red"
        pidStr = pidImage.changeColor(["xv2"], color).decode()
        pidImageHTML.content = pidStr
        pidImageHTML.update()
        print("2")
    

timer = ui.timer(1, updateColor, active=True)

ui.run(port=5000)
