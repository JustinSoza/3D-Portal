###########################################
#
# Name: Justin Soza Soto
# Project Name: 15-112 Term Project Portal
#
###########################################

from cmu_112_graphics import *
import time, math, numpy, os 
from dataclasses import make_dataclass


# Note: In 3D, will take a z dimension
Box = make_dataclass('Box',['x', 'y','r','speed','start'])

def appStarted(app):
    app.boxes = []
    app.gravity = 50

def keyPressed(app, event):
    if event.key.lower() == 'r':
        appStarted(app)


def mousePressed(app,event):
    createBox(app, event.x, event.y)

# Creates a new box object
def createBox(app, x, y):
    newBox = Box(x, y, 30, 0, time.time())
    app.boxes.append(newBox)

def timerFired(app):
    for box in app.boxes:
        if time.time() - box.start >= .1:
            box.speed += app.gravity * .1
            box.start = time.time()
    for box in app.boxes:
        # Note: In 3D it would be box.coords - num.py[0,app.speed,0]
        # OR box.coords[1] - app.speed
        if box.y + box.r < app.height:
            box.y += box.speed
        elif box.y + box.r >= app.height:
            box.y = app.height - box.r

def drawBox(app, canvas):
    for box in app.boxes:
        x0, y0 = box.x - box.r, box.y - box.r
        x1, y1 = box.x + box.r, box.y + box.r
        canvas.create_rectangle(x0, y0, x1, y1, fill = 'wheat2', outline = 'wheat3', width = 2)

def drawBoxCount(app, canvas):
    canvas.create_text(app.width // 2, app.height // 2, text = len(app.boxes),
                        font = 'Lato 30')

def redrawAll(app, canvas):
    drawBox(app, canvas)
    drawBoxCount(app, canvas)

def startApplication():
    runApp(width = 500, height = 500)

startApplication()
