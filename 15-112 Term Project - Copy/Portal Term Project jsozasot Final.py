###########################################
#
# Name: Justin Soza-Soto
# Andrew ID: jsozasot
# Project Name: 15-112 Term Project Portal
# File Description: Runs the 15-112 Portal Application
#
###########################################

from cmu_112_graphics import *
import time, math, numpy, os, copy
from dataclasses import make_dataclass

class Box(object):
    def __init__(self, x, y, z, r, speed, force, start, bounceCount, restingY, 
    pickedUp):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.speed = speed
        self.force = force
        self.start = start
        self.restingY = restingY
        self.bounceCount = bounceCount
        self.pickedUp = pickedUp
    def updateSpeed(self, app):
        self.speed -= app.gravity * .1
        self.start = time.time()
    def drop(self, app):
        if self.y - self.r > self.restingY - self.r:
            self.y += self.speed
        elif self.y <= self.restingY:
            self.y = self.restingY
            self.speed = 0
            self.start = time.time()
            self.bounceCount += 1
    def bounce(self, app):
        self.y += self.speed + self.force
        self.speed -= app.gravity * .2
        self.start = time.time()
        if self.y <= self.restingY: 
            self.speed = 0
            self.y = self.restingY
            self.force -= 10
            self.bounceCount += 1
            teleportBox(app)
            detectPress(app)

class Portal(object):
    def __init__(self, x, y, z, w, h, color, active, facing):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.h = h
        self.color = color
        self.active = active
        self.facing = facing # 6 possible directions
    
class Player(object):
    def __init__(self, x, y, z, width, height, speed, start, restingY):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.speed = speed
        self.start = start
        self.restingY = restingY
    def updateSpeed(self, app):
        self.speed -= app.gravity * .1
        self.start = time.time()
    def drop(self, app):
        if self.y - self.height > self.restingY - self.height:
            self.y += self.speed
        elif self.y - self.height <= self.restingY - self.height:
            self.y = self.restingY
            self.speed = 0
            self.start = time.time()
            self.restingY = self.y
            teleport(app)
            updatePlayerProjection(app)
    def getCoords(self, app):
        return(int(self.x), int(self.y), int(self.z))

class Button(object):
    def __init__(self, x, y, z, r, h, buttonPressed, generationCoords, 
    generationFlag):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.h = h
        self.buttonPressed = buttonPressed
        self.generationCoords = generationCoords
        self.generationFlag = False
    def generateCube(self, app):
        if self.generationCoords == []: return # Check if button is cube generator
        else:
            if self.generationFlag: return # Check if button already created a box 
            bX, bY, bZ = self.generationCoords
            createBox(app, bX, bY + 10, bZ)

class Exit(object):
    def __init__(self, x, y, z, w, h, facing, unlocked):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.h = h
        self.facing = facing
        self.unlocked = unlocked

class Wall(object):
    def __init__(self, x, y, z, l, h, w):
        self.x = x
        self.y = y
        self.z = z
        self.l = l # in x direction
        self.h = h # in y direction
        self.w = w # in z direction
        

def appStarted(app):
    app.gameOver = False
    # Initialize ray casting presets
    app.screenLeftBound = -.7
    app.screenBottomBound = -.43
    # Initialize camera
    app.cameraCoords = [500,500,500]
    app.lookAtCoords = [0, 0, 0]
    # Ray casting stuff
    app.distanceFromCam = 1
    updatePlaneCoords(app)
    app.rayCastCoords = None
    app.rayCastPoint = None
    # DEBUG
    app.showRay = False
    app.prevCameraCoords = [0, 0, 0]
    # Initialize axis
    app.orgin = [0, 0, 0]
    app.roomLines = [([-500, 0, -500], [500, 0, -500]),
                     ([500, 0, -500],  [500, 0, 500]),
                     ([500, 0, 500], [-500, 0, 500]),
                     ([-500, 0, 500], [-500, 0, -500]),
                     ([-500, 0, -500], [-500, 500, -500]),
                     ([500, 0, -500], [500, 500, -500]),
                     # ([500, 0, 500], [500, 500, 500]),
                     ([-500, 0, 500], [-500, 500, 500]),
                     ([-500, 500, -500], [500, 500, -500]),
                     # ([500, 500, -500],  [500, 500, 500]),
                     # ([500, 500, 500], [-500, 500, 500]),
                     ([-500, 500, 500], [-500, 500, -500])
    ]
    projection(app)
    app.level = 0
    app.mouseCoords = [-1, -1]

def resetLevel(app):
    if app.level == 1:
        # Initialize walls
        app.walls = set()
        app.walls.add( createWall(app, -300, 50, -200, 100, 50, 150) )
        app.walls.add( createWall(app, -300, 150, -400, 100, 150, 50) )
        app.wallPoints = dict()
        # Initialize boxes
        app.holdingBox = False
        app.boxes = set()
        app.boxPoints = []
        app.gravity = 30
        # Initialize player
        x, y, z, w, h = 100, 0, 100, 20, 40
        app.player = Player(x, y, z, w, h, 0, time.time(), h)
        app.playerPoints = []
        app.playerPoints = dict()
        app.playerUnitVecs = getPlayerNormalVec(app)
        app.teleportDelay = time.time()
        app.playerShadowPoints = []
        app.moveUp = False
        app.moveLeft = False
        app.moveDown = False
        app.moveRight = False
        # Initialize buttons 
        app.buttons = []
        app.buttonPoints = []
        app.cubeGenerationPoints = dict()
        createButton(app, 0, 0, -200, [])
        createButton(app, 0, 0, 200, [0, 0, 0])
        # Initialize portals
        w, h = 30, 60
        bluePortal = Portal(None, None, None, w, h, 'blue', False, 'y')
        orangePortal = Portal(None, None, None, w, h, 'orange', False, 'y')
        app.portals = [bluePortal, orangePortal]
        app.portalPoints = []
        # Initialize exit
        app.door = Exit(-500, 50, 0, 50, 50, 'x', False)
        app.doorPoints = dict()
        app.mouseCoords = [-1, -1]
        updatePlayerProjection(app)
        updateDoorProjection(app)
        updateButtonProjections(app)
        updateCubeGeneration(app)
        updatePlayerShadowProjection(app)
        updateWallProjections(app)
    elif app.level == 2:
        # Initialize walls
        app.walls = set()
        app.walls.add( createWall(app, -300, 70, -400, 200, 70, 100) )
        app.wallPoints = dict()
        # Initialize boxes
        app.holdingBox = False
        app.boxes = set()
        app.boxPoints = []
        app.gravity = 30
        # Initialize player
        x, y, z, w, h = 100, 0, 100, 20, 40
        app.player = Player(x, y, z, w, h, 0, time.time(), h)
        app.playerPoints = []
        app.playerPoints = dict()
        app.playerUnitVecs = getPlayerNormalVec(app)
        app.teleportDelay = time.time()
        app.playerShadowPoints = []
        app.moveUp = False
        app.moveLeft = False
        app.moveDown = False
        app.moveRight = False
        # Initialize buttons 
        app.buttons = []
        app.buttonPoints = []
        app.cubeGenerationPoints = dict()
        createButton(app, 0, 0, -200, [])
        createButton(app, 0, 0, 200, [-300, 140, -400])
        # Initialize portals
        w, h = 30, 60
        bluePortal = Portal(None, None, None, w, h, 'blue', False, 'y')
        orangePortal = Portal(None, None, None, w, h, 'orange', False, 'y')
        app.portals = [bluePortal, orangePortal]
        app.portalPoints = []
        # Initialize exit
        app.door = Exit(-500, 50, 0, 50, 50, 'x', False)
        app.doorPoints = dict()
        app.mouseCoords = [-1, -1]
        app.cameraCoords = [600,500,300]
        app.distanceFromCam = 1
        updatePlaneCoords(app)
        app.rayCastCoords = None
        app.rayCastPoint = None
        projection(app)
        updatePlayerProjection(app)
        updateDoorProjection(app)
        updateButtonProjections(app)
        updateCubeGeneration(app)
        updatePlayerShadowProjection(app)
        updateWallProjections(app)
    elif app.level == 3:
        # Initialize walls
        app.walls = set()
        app.walls.add( createWall(app, -200, 100, -400, 200, 100, 100) )
        app.walls.add( createWall(app, 300, 100, -400, 100, 100, 100) )
        app.wallPoints = dict()
        # Initialize boxes
        app.holdingBox = False
        app.boxes = set()
        app.boxPoints = []
        app.gravity = 30
        # Initialize player
        x, y, z, w, h = 100, 0, 100, 20, 40
        app.player = Player(x, y, z, w, h, 0, time.time(), h)
        app.playerPoints = []
        app.playerPoints = dict()
        app.playerUnitVecs = getPlayerNormalVec(app)
        app.teleportDelay = time.time()
        app.playerShadowPoints = []
        app.moveUp = False
        app.moveLeft = False
        app.moveDown = False
        app.moveRight = False
        # Initialize buttons 
        app.buttons = []
        app.buttonPoints = []
        app.cubeGenerationPoints = dict()
        createButton(app, 300, 200, -400, [])
        createButton(app, 0, 0, 0, [-300, 200, -400])
        # Initialize portals
        w, h = 30, 60
        bluePortal = Portal(None, None, None, w, h, 'blue', False, 'y')
        orangePortal = Portal(None, None, None, w, h, 'orange', False, 'y')
        app.portals = [bluePortal, orangePortal]
        app.portalPoints = []
        # Initialize exit
        app.door = Exit(-300, 250, -500, 50, 50, 'z', False)
        app.doorPoints = dict()
        app.mouseCoords = [-1, -1]
        app.cameraCoords = [800,800,500]
        app.distanceFromCam = 1
        updatePlaneCoords(app)
        app.rayCastCoords = None
        app.rayCastPoint = None
        projection(app)
        updatePlayerProjection(app)
        updateDoorProjection(app)
        updateButtonProjections(app)
        updateCubeGeneration(app)
        updatePlayerShadowProjection(app)
        updateWallProjections(app)
    elif app.level == 4:
        # Initialize walls
        app.walls = set()
        app.walls.add( createWall(app, -400, 75, -300, 100, 75, 100) )
        app.walls.add( createWall(app, -300, 75, 300, 200, 75, 200) )
        app.wallPoints = dict()
        # Initialize boxes
        app.holdingBox = False
        app.boxes = set()
        app.boxPoints = []
        app.gravity = 30
        # Initialize player
        x, y, z, w, h = 100, 0, 100, 20, 40
        app.player = Player(x, y, z, w, h, 0, time.time(), h)
        app.playerPoints = []
        app.playerPoints = dict()
        app.playerUnitVecs = getPlayerNormalVec(app)
        app.teleportDelay = time.time()
        app.playerShadowPoints = []
        app.moveUp = False
        app.moveLeft = False
        app.moveDown = False
        app.moveRight = False
        # Initialize buttons 
        app.buttons = []
        app.buttonPoints = []
        app.cubeGenerationPoints = dict()
        createButton(app, -400, 150, -300, [])
        createButton(app, -300, 150, 300, [0, 0, 0])
        # Initialize portals
        w, h = 30, 60
        bluePortal = Portal(None, None, None, w, h, 'blue', False, 'y')
        orangePortal = Portal(None, None, None, w, h, 'orange', False, 'y')
        app.portals = [bluePortal, orangePortal]
        app.portalPoints = []
        # Initialize exit
        app.door = Exit(-300, 50, -300, 50, 50, 'x', False)
        app.doorPoints = dict()
        app.mouseCoords = [-20, -20]
        app.cameraCoords = [500,500,800]
        app.distanceFromCam = 1
        updatePlaneCoords(app)
        app.rayCastCoords = None
        app.rayCastPoint = None
        projection(app)
        updatePlayerProjection(app)
        updateDoorProjection(app)
        updateButtonProjections(app)
        updateCubeGeneration(app)
        updatePlayerShadowProjection(app)
        updateWallProjections(app)
    elif app.level == 5:
        # Initialize walls
        app.walls = set()
        app.walls.add( createWall(app, 0, 100, 0, 100, 100, 100) )
        app.walls.add( createWall(app, 0, 100, -325 , 50, 100, 175) )
        app.wallPoints = dict()
        # Initialize boxes
        app.holdingBox = False
        app.boxes = set()
        app.boxPoints = []
        app.gravity = 30
        # Initialize player
        x, y, z, w, h = 200, 0, 200, 20, 40
        app.player = Player(x, y, z, w, h, 0, time.time(), h)
        app.playerPoints = []
        app.playerPoints = dict()
        app.playerUnitVecs = getPlayerNormalVec(app)
        app.teleportDelay = time.time()
        app.playerShadowPoints = []
        app.moveUp = False
        app.moveLeft = False
        app.moveDown = False
        app.moveRight = False
        # Initialize buttons 
        app.buttons = []
        app.buttonPoints = []
        app.cubeGenerationPoints = dict()
        createButton(app, 0, 200, 0, [])
        createButton(app, 0, 0, 300, [300, 0, 0])
        # Initialize portals
        w, h = 30, 60
        bluePortal = Portal(None, None, None, w, h, 'blue', False, 'y')
        orangePortal = Portal(None, None, None, w, h, 'orange', False, 'y')
        app.portals = [bluePortal, orangePortal]
        app.portalPoints = []
        # Initialize exit
        app.door = Exit(-500, 50, 0, 50, 50, 'x', False)
        app.doorPoints = dict()
        app.mouseCoords = [-1, -1]
        updatePlayerProjection(app)
        updateDoorProjection(app)
        updateButtonProjections(app)
        updateCubeGeneration(app)
        updatePlayerShadowProjection(app)
        updateWallProjections(app)
    elif app.level >= 6:
        # Game Complete
        app.gameOver = True


def keyPressed(app, event):
    if event.key.lower() == 'r':
        resetLevel(app)
    
    elif event.key == 'Enter' and app.level == 0:
        app.level = 1
        resetLevel(app)
    ################# DEBUG SHORT CUTS #########################################

    elif event.key == '(': 
        if app.level > 0:
            app.level -= 1
            resetLevel(app)
    elif event.key == ')': 
        if not app.gameOver:
            app.level += 1
            resetLevel(app)

    elif app.level == 0 or app.gameOver == True: return
    ################# CONFIGURE MOUSE ##########################################
    

    elif event.key == '[':
        px = app.mouseCoords[0]
        x = px - (app.width // 2)
        app.screenLeftBound = y / (app.height // 2)
    elif event.key == ']':
        py = app.mouseCoords[1]
        y = (app.height // 2) - py
        app.screenBottomBound = y / (app.height // 2)

    ################# MOVING THE CAMERA ########################################

    elif event.key == 'Up':
        app.cameraCoords = numpy.array(app.cameraCoords) + numpy.array([10,0,0])
        projection(app)
        app.playerUnitVecs = getPlayerNormalVec(app)
        # Update projections
        updatePlaneCoords(app)
        updateAllProjections(app)
        # Raycast dot projection
        if app.rayCastCoords != None:
            app.rayCastPoint = project(app, app.rayCastCoords)
    elif event.key == 'Down':
        app.cameraCoords = numpy.array(app.cameraCoords) + numpy.array([-10,0,0])
        projection(app)
        app.playerUnitVecs = getPlayerNormalVec(app)
        # Update projections        
        updatePlaneCoords(app)
        updateAllProjections(app)
        if app.rayCastCoords != None:
            app.rayCastPoint = project(app, app.rayCastCoords)
    elif event.key == 'Right':
        app.cameraCoords = numpy.array(app.cameraCoords) + numpy.array([0,0,10])
        projection(app)
        app.playerUnitVecs = getPlayerNormalVec(app)
        # Update projections        
        updatePlaneCoords(app)
        updateAllProjections(app)
        if app.rayCastCoords != None:
            app.rayCastPoint = project(app, app.rayCastCoords)
    elif event.key == 'Left':
        app.cameraCoords = numpy.array(app.cameraCoords) + numpy.array([0,0,-10])
        projection(app)
        app.playerUnitVecs = getPlayerNormalVec(app)
        # Update projections        
        updatePlaneCoords(app)
        updateAllProjections(app)
        if app.rayCastCoords != None:
            app.rayCastPoint = project(app, app.rayCastCoords)

    ############################## MOVE PLAYER ################################
    player = app.player
    if event.key.lower() == 'w':
        app.moveUp = True
    elif event.key.lower() == 'a': 
        app.moveLeft = True
    elif event.key.lower() == 's': 
        app.moveDown = True
    elif event.key.lower() == 'd': 
        app.moveRight = True
    elif event.key == 'Space':
        if player.speed != 0: return
        player.y = player.y + 1
        player.speed = 30
        player.start = time.time()
    ######################## SPAWN BOX #########################################
    elif event.key.lower() == 'e':
            pickUpBox(app)

    elif event.key.lower() == 'c':
        x, y, z = app.rayCastCoords
        createBox(app, x, y, z)
    ######################## TOGGLE RAY ########################################
    elif event.key.lower() == 'p':
        app.showRay = not app.showRay

def keyReleased(app, event):
    if event.key.lower() == 'w':
        app.moveUp = False
    elif event.key.lower() == 'a':
        app.moveLeft = False
    elif event.key.lower() == 's':
        app.moveDown = False
    elif event.key.lower() == 'd':
        app.moveRight = False

#################################### MOUSE EVENTS ##############################

def mousePressed(app,event):
    if app.level == 0 or app.gameOver == True: return
    x, y, z = rayCastMouse(app, event.x, event.y)
    app.rayCastCoords = [x, y, z]
    sol = detectWall(app)
    facing = None
    if sol != None:
        x, y, z, facing = sol
        app.rayCastCoords = [x, y, z]
    app.rayCastPoint = project(app, app.rayCastCoords)
    app.prevCameraCoords = app.cameraCoords    
    updateBoxProjections(app)
    createPortal(app, x, y ,z, 'Left', facing)
    teleportBox(app)
    
def mouseMoved(app, event):
    if app.level == 0 or app.gameOver == True: return
    app.mouseCoords = [event.x, event.y]
    x, y, z = rayCastMouse(app, event.x, event.y)
    app.rayCastCoords = [x, y, z]
    sol = detectWall(app)
    if sol != None:
        x, y, z, facing = sol
        app.rayCastCoords = [x, y, z]
    app.rayCastPoint = project(app, app.rayCastCoords)

def rightClickPressed(app, event):
    if app.level == 0 or app.gameOver == True: return
    x, y, z = rayCastMouse(app, event.x, event.y)
    app.rayCastCoords = [x, y, z]
    sol = detectWall(app)
    facing = None
    if sol != None:
        x, y, z, facing = sol
        app.rayCastCoords = [x, y, z]
    app.rayCastPoint = project(app, app.rayCastCoords)
    createPortal(app, x, y ,z, 'Right', facing)
    app.prevCameraCoords = app.cameraCoords
    teleportBox(app)

########################### RAYCASTING #########################################

# Returns legal point in 3D space that comes from the ray that connects the camera
def rayCastMouse(app, x, y):
    # Scale x vector
    m = x - (app.width // 2)
    rMin = (app.width // 2) * -1
    rMax = app.width // 2
    dx = scaledVector(app, m, rMin, rMax, app.screenLeftBound, app.screenLeftBound * -1)
    # Scale y vector
    m = (app.height // 2) - y
    rMin = (app.height // 2) * -1
    rMax = (app.height // 2)
    dy = scaledVector(app, m, rMin, rMax, app.screenBottomBound, app.screenBottomBound * -1)
    iHat, jHat = rayCastProject(app)
    scaledX, scaledY = iHat * dx, jHat * dy
    mouseProjection = numpy.array(app.planeCoords) + scaledX + scaledY
    return findLegalPosition(app, mouseProjection, app.cameraCoords)

# Scale input (with given range) to an output (within a given range)
def scaledVector(app, m, rMin, rMax, a, b):
    return (((m - rMin) / (rMax - rMin)) * (b - a)) + a

# Returns the iHat and jHat unit vectors of the ray casting plane
def rayCastProject(app):
    # Convert vector into unit vector
    planeNormal = numpy.array(app.cameraCoords) - numpy.array(app.lookAtCoords)
    planeNormal = planeNormal / numpy.linalg.norm(planeNormal)
    d, e ,f = app.planeCoords[0], app.planeCoords[1], app.planeCoords[2]
    a, b, c = planeNormal[0], planeNormal[1], planeNormal[2]
    x, y, z = app.planeCoords[0], app.planeCoords[1] + 1, app.planeCoords[2]
    t = (a*d - a*x + b*e - b*y + c*f - c*z) / (a**2 + b**2 + c**2)
    planeVerticalPoint = numpy.array([x + t*a, y + t*b, z + t*c])
    jVec = planeVerticalPoint - numpy.array(app.planeCoords)
    jHat = jVec / numpy.linalg.norm(jVec)
    iHat = numpy.cross(jHat, planeNormal)
    return iHat, jHat * -1

# find t where y = 0 (In real game, will be if point hits any wall and not just the floor)
def findLegalPosition(app, projectedPoint, cameraCoords):
    x1, x2 = cameraCoords[0], projectedPoint[0]
    y1, y2 = cameraCoords[1], projectedPoint[1]
    z1, z2 = cameraCoords[2], projectedPoint[2]
    xBound = -500
    yBound = 0
    zBound = -500
    t = -y1 / (y2 - y1)
    x = x1 + (x2 - x1) * t
    y = yBound
    z = z1 + (z2 - z1) * t
    if x < xBound:
        t = (xBound - x1) / (x2 - x1)
        x = xBound
        y = y1 + (y2 - y1) * t
        z = z1 + (z2 - z1) * t
    if z < zBound:
        t = (zBound - z1) / (z2 - z1)
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        z = zBound
    return x, y, z

# Detects if raycast intersects a wall, updates coordinates accordingly
def detectWall(app):
    if app.rayCastCoords == None: return
    player = app.player
    x1, y1, z1 = player.x, player.y, player.z
    x2, y2, z2 = app.rayCastCoords
    for wall in app.walls:
        closest = None
        facing = None
        ############################### X FACING WALLS #########################
        xBound = wall.x + wall.l
        t = (xBound - x1) / (x2 - x1)
        y = y1 + (y2 - y1) * t
        z = z1 + (z2 - z1) * t
        if z >= (wall.z - wall.w) and z <= (wall.z + wall.w):
            distance = getDistance(app, [x1, 0, y1], [wall.x + wall.l, 0, z])
            if closest == None or distance < closest: 
                if y <= wall.y + wall.h and y >= wall.h - wall.h:
                    closest = distance
                    facing = 'x'
                    projX, projZ, projY = x1 + (x2 - x1) * t, z, y
        xBound = wall.x - wall.l
        t = (xBound - x1) / (x2 - x1)
        y = y1 + (y2 - y1) * t
        z = z1 + (z2 - z1) * t
        if z >= (wall.z - wall.w) and z <= (wall.z + wall.w):
            distance = getDistance(app, [x1, 0, y1], [wall.x - wall.l, 0, z])
            if closest == None or distance < closest: 
                if y <= wall.y + wall.h and y >= wall.h - wall.h:
                    closest = distance
                    facing = '-x'
                    projX, projZ, projY = x1 + (x2 - x1) * t, z, y
        ################################ Z FACING WALLS ########################
        zBound = wall.z + wall.w
        t = (zBound - z1) / (z2 - z1)
        x = x1 + (x2 - x1) * t
        if x >= (wall.x - wall.l) and x <= (wall.x + wall.l):
            distance = getDistance(app, [x1, 0, y1], [x, 0, wall.z + wall.w])
            if closest == None or distance < closest: 
                if y <= wall.y + wall.h and y >= wall.h - wall.h:
                    closest = distance
                    facing = 'z'
                    projX, projZ, projY = x, z1 + (z2 - z1) * t, y
        zBound = wall.z - wall.w
        t = (zBound - z1) / (z2 - z1)
        x = x1 + (x2 - x1) * t
        if x >= (wall.x - wall.l) and x <= (wall.x + wall.l):
            distance = getDistance(app, [x1, 0, y1], [x, 0, wall.z - wall.w])
            if closest == None or distance < closest: 
                if y <= wall.y + wall.h and y >= wall.h - wall.h:
                    facing = '-z'
                    projX, projZ, projY = x, z1 + (z2 - z1) * t, y
        #################################### Y FACING WALLS ####################
        yBound = wall.y + wall.h
        if player.y > yBound:
            t = (yBound - y1) / (y2 - y1)
            x = x1 + (x2 - x1) * t
            z = z1 + (z2 - z1) * t
            if x <= wall.x + wall.l and x >= wall.x - wall.l and z <= wall.z + wall.w and z >= wall.z - wall.w:
                projX, projY, projZ = x, yBound, z
                closest = ':)'
                facing = 'y'
        if closest != None: 
            return [projX, projY, projZ, facing]
    return None

# Gets player [x,z] unit vectors in direction of camera to lookAt points
def getPlayerNormalVec(app):
    x0, z0 = app.lookAtCoords[0], app.lookAtCoords[2]
    x1, z1 = app.cameraCoords[0], app.cameraCoords[2]
    camToLookAtVec = numpy.array([x0, 0, z0]) - numpy.array([x1, 0, z1])
    jHat = camToLookAtVec / numpy.linalg.norm(camToLookAtVec)
    iHat = numpy.cross(jHat, numpy.array([0, 1, 0]))
    return iHat, jHat

def getBoxPlacementNormalVecs(app):
    player = app.player
    x0, z0 = app.rayCastCoords[0], app.rayCastCoords[2]
    x1, z1 = player.x, player.z
    camToLookAtVec = numpy.array([x0, 0, z0]) - numpy.array([x1, 0, z1])
    jHat = camToLookAtVec / numpy.linalg.norm(camToLookAtVec)
    iHat = numpy.cross(jHat, numpy.array([0, 1, 0]))
    return iHat, jHat

######################### CREATE OBJECTS #######################################

def createBox(app, x, y, z):
    height = 200
    r = 30
    initialSpeed = 0
    newBox = Box(x, y + r + height, z, r, initialSpeed, 20, time.time(), 0, 0, False)
    checkLegelBoxMove(app, newBox)
    app.boxes.add(newBox)

def createPortal(app, x, y, z, click, facing):
    if click == 'Right':
        app.portals[1].color = 'orange'
        app.portals[1].x, app.portals[1].y, app.portals[1].z = x, y, z
        app.portals[1].active = True
        # Along xy plane
        if x == -500 or facing == 'x':
            app.portals[1].facing = 'x'
        # Along yx plane
        elif y == 0:
            app.portals[1].facing = 'y'
        # Along yz plane
        elif z == -500 or facing == 'z':
            app.portals[1].facing = 'z'
        else: app.portals[1].facing = facing
    elif click == 'Left':
        app.portals[0].color = 'blue'        
        app.portals[0].x, app.portals[0].y, app.portals[0].z = x, y, z
        app.portals[0].active = True
        if x == -500 or facing == 'x':
            app.portals[0].facing = 'x'
        # Along yx plane
        elif y == 0:
            app.portals[0].facing = 'y'
        # Along yz plane
        elif z == -500 or facing == 'z':
            app.portals[0].facing = 'z'
        else: app.portals[1].facing = facing
    updatePortalCoords(app)
    updatePortalProjections(app)

def createButton(app, x, y, z, boxCoords):
    r = 30
    h = 15
    newButton = Button(x, y, z, r, h, False, boxCoords, False)
    app.buttons.append(newButton)

def createWall(app, x, y, z, l, h, w):
    newWall = Wall(x, y, z, l, h, w)
    return newWall

######################### UPDATE COORDS ########################################

# Fix portal to stay in bounds
def updatePortalCoords(app):
    xBound = -500
    yBound = 0
    zBound = -500
    for portal in app.portals:
        if portal.active:
            if portal.facing == 'x':
                if portal.y - portal.h < yBound: portal.y = portal.h + yBound
                if portal.z - portal.w < zBound: portal.z = portal.w + zBound
            elif portal.facing == 'y':
                if portal.x - portal.h < xBound: portal.x = portal.h + xBound
                if portal.z - portal.w < zBound: portal.z = portal.w + zBound
            elif portal.facing == 'z':
                if portal.y - portal.h < yBound: portal.y = portal.h + yBound
                if portal.x - portal.w < xBound: portal.x = portal.w + xBound
            
# Find the center point of the ray casting plane
def updatePlaneCoords(app):
    direction = numpy.array(app.lookAtCoords) - numpy.array(app.cameraCoords)
    magnitude = numpy.linalg.norm(direction)
    unitVec = direction / magnitude
    # Pointing from cam to plane
    camToPlaneVec = unitVec * app.distanceFromCam
    app.planeCoords = numpy.array(app.cameraCoords) - numpy.array(camToPlaneVec) 

########################### PROJECTIONS ########################################
# Takes [x, y, z] coords of object and converts them into [x, y] projections

def updateAllProjections(app):
    updateBoxProjections(app)
    updatePlayerProjection(app)
    updatePortalProjections(app)
    updateButtonProjections(app)
    updateDoorProjection(app)
    updatePlayerShadowProjection(app)
    updateCubeGeneration(app)
    updateWallProjections(app)

def updateBoxProjections(app):
    app.boxPoints = []
    for box in app.boxes:
        boxCorners = []
        x, y, z, r = box.x, box.y, box.z, box.r
        # Front Side
        x0, y0 = project(app, [x - r, y + r, z + r])
        x1, y1 = project(app, [x + r, y + r, z + r])
        x2, y2 = project(app, [x - r, y - r, z + r])
        x3, y3 = project(app, [x + r, y - r, z + r])
        boxCorners += [[x0, y0, x1, y1, x2, y2, x3, y3]]
        # Top Side
        x0, y0 = project(app, [x - r, y + r, z + r])
        x1, y1 = project(app, [x - r, y + r, z - r])
        x2, y2 = project(app, [x + r, y + r, z + r])
        x3, y3 = project(app, [x + r, y + r, z - r])
        boxCorners += [[x0, y0, x1, y1, x2, y2, x3, y3]]
        # Right Side
        x0, y0 = project(app, [x + r, y + r, z + r])
        x1, y1 = project(app, [x + r, y + r, z - r])
        x2, y2 = project(app, [x + r, y - r, z + r])
        x3, y3 = project(app, [x + r, y - r, z - r])
        boxCorners += [[x0, y0, x1, y1, x2, y2, x3, y3]]
        # Bottom Side
        x0, y0 = project(app, [x - r, y - r, z + r])
        x1, y1 = project(app, [x - r, y - r, z - r])
        x2, y2 = project(app, [x + r, y - r, z + r])
        x3, y3 = project(app, [x + r, y - r, z - r])
        boxCorners += [[x0, y0, x1, y1, x2, y2, x3, y3]]
        # Left Side
        x0, y0 = project(app, [x - r, y + r, z + r])
        x1, y1 = project(app, [x - r, y + r, z - r])
        x2, y2 = project(app, [x - r, y - r, z + r])
        x3, y3 = project(app, [x - r, y - r, z - r])
        boxCorners += [[x0, y0, x1, y1, x2, y2, x3, y3]]
        # Back Side
        x0, y0 = project(app, [x - r, y + r, z - r])
        x1, y1 = project(app, [x - r, y - r, z - r])
        x2, y2 = project(app, [x + r, y + r, z - r])
        x3, y3 = project(app, [x + r, y - r, z - r])
        boxCorners += [[x0, y0, x1, y1, x2, y2, x3, y3]]
        app.boxPoints += [boxCorners]

def updatePlayerProjection(app):
    player = app.player
    x, y, z, w, h = player.x, player.y, player.z, player.width, player.height
    # Front Side
    x0, y0 = project(app, [x - w, y + h, z + w])
    x1, y1 = project(app, [x + w, y + h, z + w])
    x2, y2 = project(app, [x - w, y - h, z + w])
    x3, y3 = project(app, [x + w, y - h, z + w])
    app.playerPoints['front'] = [x0, y0, x1, y1, x2, y2, x3, y3]
    # Top Side
    x0, y0 = project(app, [x - w, y + h, z + w])
    x1, y1 = project(app, [x - w, y + h, z - w])
    x2, y2 = project(app, [x + w, y + h, z + w])
    x3, y3 = project(app, [x + w, y + h, z - w])
    app.playerPoints['top'] = [x0, y0, x1, y1, x2, y2, x3, y3]
    # Right Side
    x0, y0 = project(app, [x + w, y + h, z + w])
    x1, y1 = project(app, [x + w, y + h, z - w])
    x2, y2 = project(app, [x + w, y - h, z + w])
    x3, y3 = project(app, [x + w, y - h, z - w])
    app.playerPoints['right'] = [x0, y0, x1, y1, x2, y2, x3, y3]
    # Bottom Side
    x0, y0 = project(app, [x - w, y - h, z + w])
    x1, y1 = project(app, [x - w, y - h, z - w])
    x2, y2 = project(app, [x + w, y - h, z + w])
    x3, y3 = project(app, [x + w, y - h, z - w])
    app.playerPoints['bottom'] = [x0, y0, x1, y1, x2, y2, x3, y3]
    # Left Side
    x0, y0 = project(app, [x - w, y + h, z + w])
    x1, y1 = project(app, [x - w, y + h, z - w])
    x2, y2 = project(app, [x - w, y - h, z + w])
    x3, y3 = project(app, [x - w, y - h, z - w])
    app.playerPoints['left'] = [x0, y0, x1, y1, x2, y2, x3, y3]
    # Back Side
    x0, y0 = project(app, [x - w, y + h, z - w])
    x1, y1 = project(app, [x - w, y - h, z - w])
    x2, y2 = project(app, [x + w, y + h, z - w])
    x3, y3 = project(app, [x + w, y - h, z - w])
    app.playerPoints['back'] = [x0, y0, x1, y1, x2, y2, x3, y3]

def updatePlayerShadowProjection(app):
    player = app.player
    app.playerShadowPoints = []
    y = player.restingY - player.height
    x, z, w = player.x, player.z, player.width
    x0, y0 = project(app, [x - w, y, z + w])
    x1, y1 = project(app, [x - w, y, z - w])
    x2, y2 = project(app, [x + w, y, z - w])
    x3, y3 = project(app, [x + w, y, z + w])
    app.playerShadowPoints += [x0, y0, x1, y1, x2, y2, x3, y3]

def updatePortalProjections(app):
    app.portalPoints = []
    for portal in app.portals:
        if portal.active:
            color = portal.color
            if portal.facing == 'x' or portal.facing == '-x':
                # Top
                y, z = portal.y + portal.h, portal.z - (portal.w // 2)
                x0, y0 = project(app, [portal.x, y, z])
                y, z = portal.y + portal.h, portal.z + (portal.w // 2)
                x1, y1 = project(app, [portal.x, y, z])
                # Right Side
                y, z = portal.y + (portal.h // 2), portal.z + portal.w
                x2, y2 = project(app, [portal.x, y, z])
                y, z = portal.y - (portal.h // 2), portal.z + portal.w
                x3, y3 = project(app, [portal.x, y, z])
                # Bottom
                y, z = portal.y - portal.h, portal.z + (portal.w // 2)
                x4, y4 = project(app, [portal.x, y, z])
                y, z = portal.y - portal.h, portal.z - (portal.w // 2)
                x5, y5 = project(app, [portal.x, y, z])
                # Left Side
                y, z = portal.y - (portal.h // 2), portal.z - portal.w
                x6, y6 = project(app, [portal.x, y, z])
                y, z = portal.y + (portal.h // 2), portal.z - portal.w
                x7, y7 = project(app, [portal.x, y, z])
            elif portal.facing == 'y':
                # Top
                x, z = portal.x + portal.h, portal.z - (portal.w // 2)
                x0, y0 = project(app, [x, portal.y, z])
                x, z = portal.x + portal.h, portal.z + (portal.w // 2)
                x1, y1 = project(app, [x, portal.y, z])
                # Right Side
                x, z = portal.x + (portal.h // 2), portal.z + portal.w
                x2, y2 = project(app, [x, portal.y, z])
                x, z = portal.x - (portal.h // 2), portal.z + portal.w
                x3, y3 = project(app, [x, portal.y, z])
                # Bottom
                x, z = portal.x - portal.h, portal.z + (portal.w // 2)
                x4, y4 = project(app, [x, portal.y, z])
                x, z = portal.x - portal.h, portal.z - (portal.w // 2)
                x5, y5 = project(app, [x, portal.y, z])
                # Left Side
                x, z = portal.x - (portal.h // 2), portal.z - portal.w
                x6, y6 = project(app, [x, portal.y, z])
                x, z = portal.x + (portal.h // 2), portal.z - portal.w
                x7, y7 = project(app, [x, portal.y, z])
            elif portal.facing == 'z' or portal.facing == '-z':
                # Top
                y, x = portal.y + portal.h, portal.x - (portal.w // 2)
                x0, y0 = project(app, [x, y, portal.z])
                y, x = portal.y + portal.h, portal.x + (portal.w // 2)
                x1, y1 = project(app, [x, y, portal.z])
                # Right Side
                y, x = portal.y + (portal.h // 2), portal.x + portal.w
                x2, y2 = project(app, [x, y, portal.z])
                y, x = portal.y - (portal.h // 2), portal.x + portal.w
                x3, y3 = project(app, [x, y, portal.z])
                # Bottom
                y, x = portal.y - portal.h, portal.x + (portal.w // 2)
                x4, y4 = project(app, [x, y, portal.z])
                y, x = portal.y - portal.h, portal.x - (portal.w // 2)
                x5, y5 = project(app, [x, y, portal.z])
                # Left Side
                y, x = portal.y - (portal.h // 2), portal.x - portal.w
                x6, y6 = project(app, [x, y, portal.z])
                y, x = portal.y + (portal.h // 2), portal.x - portal.w
                x7, y7 = project(app, [x, y, portal.z])
            app.portalPoints += [[x0, y0, x1, y1, x2, y2, x3, y3, 
                              x4, y4, x5, y5, x6, y6, x7, y7, color]]
                
def updateButtonProjections(app):
    app.buttonPoints= []
    for button in app.buttons:
        x, y, z = button.x, button.y, button.z
        r, h = button.r, button.h
        # Bottom
        x0, y0 = project(app, [x - r, y, z - r])
        x1, y1 = project(app, [x - r, y, z + r])
        x2, y2 = project(app, [x + r, y, z + r])
        x3, y3 = project(app, [x + r, y, z - r])
        bottom = [x0, y0, x1, y1, x2, y2, x3, y3]
        if not button.buttonPressed:
            x0, y0 = project(app, [x - r, y + h, z - r])
            x1, y1 = project(app, [x - r, y + h, z + r])
            x2, y2 = project(app, [x + r, y + h, z + r])
            x3, y3 = project(app, [x + r, y + h, z - r])
            top = [x0, y0, x1, y1, x2, y2, x3, y3]
        else: 
            x0, y0 = project(app, [x - r, y + h // 2, z - r])
            x1, y1 = project(app, [x - r, y + h // 2, z + r])
            x2, y2 = project(app, [x + r, y + h // 2, z + r])
            x3, y3 = project(app, [x + r, y + h // 2, z - r])
            top =[x0, y0, x1, y1, x2, y2, x3, y3]
        app.buttonPoints += [ (bottom, top) ]

def updateDoorProjection(app):
    door = app.door
    x, y, z = door.x, door.y - door.h, door.z
    x0, y0 = project(app, [x, y, z])
    y = door.y + door.h
    x1, y1 = project(app, [x, y, z])
    app.doorPoints['split'] = [x0, y0, x1, y1]
    if door.facing == 'x':
        # Top
        y, z = door.y + door.h, door.z - (door.w // 2)
        x0, y0 = project(app, [door.x, y, z])
        y, z = door.y + door.h, door.z + (door.w // 2)
        x1, y1 = project(app, [door.x, y, z])
        # Right Side
        y, z = door.y + (door.h // 2), door.z + door.w
        x2, y2 = project(app, [door.x, y, z])
        # Bottom
        y, z = door.y - door.h, door.z
        x3, y3 = project(app, [door.x, y, z + door.w])
        y, z = door.y - door.h, door.z
        x4, y4 = project(app, [door.x, y, z - door.w])
        # Left Side
        y, z = door.y + (door.h // 2), door.z - door.w
        x5, y5 = project(app, [door.x, y, z])
        app.doorPoints['frame'] = [x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5]
        x0, y0 = project(app, [door.x, door.y + door.h + door.w, door.z - (door.w // 2)])
        x1, y1 = project(app, [door.x, door.y + door.h + door.w, door.z + (door.w // 2)])
        x2, y2 = project(app, [door.x, door.y + door.h + door.w // 2, door.z + (door.w // 2)])
        x3, y3 = project(app, [door.x, door.y + door.h + door.w // 2, door.z - (door.w // 2)])
        app.doorPoints['sign'] = [x0, y0, x1, y1, x2, y2, x3, y3]
    elif door.facing == 'z':
        # Top
        y, x = door.y + door.h, door.x - (door.w // 2)
        x0, y0 = project(app, [x, y, door.z])
        y, x = door.y + door.h, door.x + (door.w // 2)
        x1, y1 = project(app, [x, y, door.z])
        # Right Side
        y, x = door.y + (door.h // 2), door.x + door.w
        x2, y2 = project(app, [x, y, door.z])
        # Bottom
        y, x = door.y - door.h, door.x + door.w
        x3, y3 = project(app, [x, y, door.z])
        y, x = door.y - door.h, door.x - door.w
        x4, y4 = project(app, [x, y, door.z])
        # Left Side
        y, x = door.y + (door.h // 2), door.x - door.w
        x5, y5 = project(app, [x, y, door.z])
        app.doorPoints['frame'] = [x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5]
        x0, y0 = project(app, [door.x + (door.w // 2), door.y + door.h + door.w, door.z])
        x1, y1 = project(app, [door.x - (door.w // 2), door.y + door.h + door.w, door.z])
        x2, y2 = project(app, [door.x - (door.w // 2), door.y + door.h + door.w // 2, door.z])
        x3, y3 = project(app, [door.x + (door.w // 2), door.y + door.h + door.w // 2, door.z])
        app.doorPoints['sign'] = [x0, y0, x1, y1, x2, y2, x3, y3]

def updateWallProjections(app):
    for wall in app.walls:
        dWall = dict()
        x, y, z, l, h, w = wall.x, wall.y, wall.z, wall.l, wall.h, wall.w
        # Front Side
        x0, y0 = project(app, [x - l, y + h, z + w])
        x1, y1 = project(app, [x + l, y + h, z + w])
        x2, y2 = project(app, [x - l, y - h, z + w])
        x3, y3 = project(app, [x + l, y - h, z + w])
        dWall['front'] = [x0, y0, x1, y1, x2, y2, x3, y3]
        # Top Side
        x0, y0 = project(app, [x - l, y + h, z + w])
        x1, y1 = project(app, [x - l, y + h, z - w])
        x2, y2 = project(app, [x + l, y + h, z + w])
        x3, y3 = project(app, [x + l, y + h, z - w])
        dWall['top'] = [x0, y0, x1, y1, x2, y2, x3, y3]
        # Right Side
        x0, y0 = project(app, [x + l, y + h, z + w])
        x1, y1 = project(app, [x + l, y + h, z - w])
        x2, y2 = project(app, [x + l, y - h, z + w])
        x3, y3 = project(app, [x + l, y - h, z - w])
        dWall['right'] = [x0, y0, x1, y1, x2, y2, x3, y3]
        # Bottom Side
        x0, y0 = project(app, [x - l, y - h, z + w])
        x1, y1 = project(app, [x - l, y - h, z - w])
        x2, y2 = project(app, [x + l, y - h, z + w])
        x3, y3 = project(app, [x + l, y - h, z - w])
        dWall['bottom'] = [x0, y0, x1, y1, x2, y2, x3, y3]
        # Left Side
        x0, y0 = project(app, [x - l, y + h, z + w])
        x1, y1 = project(app, [x - l, y + h, z - w])
        x2, y2 = project(app, [x - l, y - h, z + w])
        x3, y3 = project(app, [x - l, y - h, z - w])
        dWall['left'] = [x0, y0, x1, y1, x2, y2, x3, y3]
        # Back Side
        x0, y0 = project(app, [x - l, y + h, z - w])
        x1, y1 = project(app, [x - l, y - h, z - w])
        x2, y2 = project(app, [x + l, y + h, z - w])
        x3, y3 = project(app, [x + l, y - h, z - w])
        dWall['back'] = [x0, y0, x1, y1, x2, y2, x3, y3]
        app.wallPoints[wall] = dWall

def updateCubeGeneration(app):
    r = 20
    for button in app.buttons:
        if button.generationCoords != []:
            x, y, z = button.generationCoords
            x0, y0 = project(app, [x - r, y, z - r])
            x1, y1 = project(app, [x - r, y, z + r])
            x2, y2 = project(app, [x + r, y, z + r])
            x3, y3 = project(app, [x + r, y, z - r])
            app.cubeGenerationPoints[button] = [x0, y0, x1, y1, x2, y2, x3, y3]

############################### LOGISTICS ######################################

def timerFired(app):
    if app.level == 0 or app.gameOver == True: return

    player = app.player
    iHat, jHat = app.playerUnitVecs[0], app.playerUnitVecs[1]
    step = 15
    if app.moveUp == True:
        if time.time() - app.teleportDelay > .5: 
            translate = step * numpy.array(jHat)
            newPlayerCoords = numpy.array([player.x, 0, player.z]) + translate
            if checkLegalMove(app, newPlayerCoords):
                player.x, player.z = newPlayerCoords[0], newPlayerCoords[2]
            playerMove(app)
    if app.moveLeft == True:
        if time.time() - app.teleportDelay > .5: 
            translate = step * numpy.array(iHat)
            newPlayerCoords = numpy.array([player.x, 0, player.z]) + translate
            if checkLegalMove(app, newPlayerCoords):
                player.x, player.z = newPlayerCoords[0], newPlayerCoords[2]
            playerMove(app)
    if app.moveDown == True:
        if time.time() - app.teleportDelay > .5: 
            translate = step * numpy.array(jHat)
            newPlayerCoords = numpy.array([player.x, 0, player.z]) - translate
            if checkLegalMove(app, newPlayerCoords):
                player.x, player.z = newPlayerCoords[0], newPlayerCoords[2]
            playerMove(app)
    if app.moveRight == True:
        if time.time() - app.teleportDelay > .5: 
            translate = step * numpy.array(iHat)
            newPlayerCoords = numpy.array([player.x, 0, player.z]) - translate
            if checkLegalMove(app, newPlayerCoords):
                player.x, player.z = newPlayerCoords[0], newPlayerCoords[2]
            playerMove(app)
    for box in app.boxes:
        if not box.pickedUp:
            if time.time() - box.start >= .1:
                if box.bounceCount == 0: # box is still falling
                    checkLegelBoxMove(app, box)
                    box.updateSpeed(app)
                    box.drop(app)
                    checkLegelBoxMove(app, box)
                    updateBoxProjections(app)
                else:
                    if box.bounceCount <= 3:
                        box.bounce(app)
                        checkLegelBoxMove(app, box)
                        updateBoxProjections(app)
        else:
            box.x = player.x
            box.y = player.y + player.height + box.r + 20
            box.z = player.z
            updateBoxProjections(app)
    if time.time() - player.start >= .1:
        player.updateSpeed(app)
        player.drop(app)
        updatePlayerShadowProjection(app)
        updatePlayerProjection(app)

# Collection of functions to update player projections and detect obejects
def playerMove(app):
    teleport(app)
    player = app.player
    detectPress(app)
    detectWin(app)
    updatePlayerShadowProjection(app)
    updatePlayerProjection(app)

# Detect if player is in portal, teleports them to other portal
def teleport(app):
    player = app.player
    x0 = player.x
    y0 = player.y
    z0 = player.z
    bluePortal = True # i = 0
    if app.portals[0].active and app.portals[1].active: # Both portals must be active
        for portal in app.portals:
            x1 = portal.x 
            y1 = portal.y
            z1 = portal.z
            force = 30
            distance = getDistance(app, [x0, y0, z0], [x1, y1, z1])
            spaces =  [[player.width + 30, 0, 0],[0, player.height + 10,0],
                          [0, 0, player.width + 30], [player.width - 30, 0, 0], [0, 0, player.width - 30]
                          ]
            ############# TELEPORT TO ORANGE PORTAL ############################
            if bluePortal:
                i = ['x', 'y', 'z', '-x', '-z'].index(app.portals[1].facing)
                xSpace, ySpace, zSpace = spaces[i]
                if portal.facing == 'x':
                    if distance <= player.width + portal.w:
                        player.x = app.portals[1].x + xSpace
                        player.y = app.portals[1].y + ySpace
                        player.z = app.portals[1].z + zSpace
                        checkLegalMove(app, [player.x, player.y, player.z])
                        app.teleportDelay = time.time()
                elif portal.facing == 'y':
                    if distance <= player.height + portal.h: 
                        thrust(app, app.portals[1].facing, force)
                        player.x = app.portals[1].x + xSpace
                        player.y = app.portals[1].y + ySpace
                        player.z = app.portals[1].z + zSpace
                        checkLegalMove(app, [player.x, player.y, player.z])
                        app.teleportDelay = time.time()
                elif portal.facing == 'z':
                    if distance <= player.width + portal.w:
                        player.x = app.portals[1].x + xSpace
                        player.y = app.portals[1].y + ySpace
                        player.z = app.portals[1].z + zSpace
                        checkLegalMove(app, [player.x, player.y, player.z])
                        app.teleportDelay = time.time()
                elif portal.facing == '-x':
                    if distance <= player.width + portal.w:
                        thrust(app, app.portals[1].facing, force)
                        player.x = app.portals[1].x + xSpace
                        player.y = app.portals[1].y + ySpace
                        player.z = app.portals[1].z + zSpace
                        checkLegalMove(app, [player.x, player.y, player.z])
                        app.teleportDelay = time.time()
                elif portal.facing == '-z':    
                    if distance <= player.width + portal.w:
                        thrust(app, app.portals[1].facing, force)
                        player.x = app.portals[1].x + xSpace
                        player.y = app.portals[1].y + ySpace
                        player.z = app.portals[1].z + zSpace
                        checkLegalMove(app, [player.x, player.y, player.z])
                        app.teleportDelay = time.time()
            ################### TELEPORT TO BLUE PORTAL ########################
            else:
                i = ['x', 'y', 'z', '-x', '-z'].index(app.portals[0].facing)
                xSpace, ySpace, zSpace = spaces[i]  
                if portal.facing == 'x':
                    if distance <= player.width + portal.w:
                        thrust(app, app.portals[0].facing, force)
                        player.x = app.portals[0].x + xSpace
                        player.y = app.portals[0].y + ySpace
                        player.z = app.portals[0].z + zSpace
                        checkLegalMove(app, [player.x, player.y, player.z])
                        app.teleportDelay = time.time()
                elif portal.facing == 'y':
                    if distance <= player.height + portal.h: 
                        thrust(app, app.portals[0].facing, force)
                        player.x = app.portals[0].x + xSpace
                        player.y = app.portals[0].y + ySpace
                        player.z = app.portals[0].z + zSpace
                        checkLegalMove(app, [player.x, player.y, player.z])
                        app.teleportDelay = time.time()
                elif portal.facing == 'z':
                    if distance <= player.width + portal.w:
                        thrust(app, app.portals[0].facing, force)
                        player.x = app.portals[0].x + xSpace
                        player.y = app.portals[0].y + ySpace
                        player.z = app.portals[0].z + zSpace
                        checkLegalMove(app, [player.x, player.y, player.z])
                        app.teleportDelay = time.time()
                elif portal.facing == '-x':
                    if distance <= player.width + portal.w:
                        thrust(app, app.portals[1].facing, force)
                        player.x = app.portals[1].x + xSpace
                        player.y = app.portals[1].y + ySpace
                        player.z = app.portals[1].z + zSpace
                        checkLegalMove(app, [player.x, player.y, player.z])
                        app.teleportDelay = time.time()
                elif portal.facing == '-z':  
                    if distance <= player.width + portal.w:
                        thrust(app, app.portals[1].facing, force)
                        player.x = app.portals[1].x + xSpace
                        player.y = app.portals[1].y + ySpace
                        player.z = app.portals[1].z + zSpace
                        checkLegalMove(app, [player.x, player.y, player.z])
                        app.teleportDelay = time.time()
            bluePortal = not bluePortal

# Detect if box is in portal, teleports it to other portal
def teleportBox(app):
    for box in app.boxes:
        x0 = box.x
        y0 = box.y
        z0 = box.z
        bluePortal = True # i = 0
        if app.portals[0].active and app.portals[1].active: # Both portals must be active
            for portal in app.portals:
                x1 = portal.x 
                y1 = portal.y
                z1 = portal.z
                force = 30
                distance = getDistance(app, [x0, y0, z0], [x1, y1, z1])
                spaces =  [[box.r + 2, 0, 0],[0, box.r + 2,0],[0, 0, box.r + 2], [box.r - 2, 0, 0], [0, 0, box.r - 2]]
                ############# TELEPORT TO ORANGE PORTAL ############################
                if bluePortal:
                    i = ['x', 'y', 'z', '-x', '-z'].index(app.portals[1].facing)
                    xSpace, ySpace, zSpace = spaces[i]
                    if portal.facing == 'x':
                        if distance <= box.r + portal.w:
                            thrustBox(app, app.portals[1].facing, force, box)
                            box.x = app.portals[1].x + xSpace
                            box.y = app.portals[1].y + ySpace
                            box.z = app.portals[1].z + zSpace
                            box.speed = 0
                            box.force = 0
                            box.bounceCount = 0
                            checkLegelBoxMove(app, box)
                            app.teleportDelay = time.time()
                    elif portal.facing == 'y':
                        if distance <= box.r + portal.h: 
                            thrustBox(app, app.portals[1].facing, force, box)
                            box.x = app.portals[1].x + xSpace
                            box.y = app.portals[1].y + ySpace
                            box.z = app.portals[1].z + zSpace
                            app.teleportDelay = time.time()
                            checkLegelBoxMove(app, box)
                    elif portal.facing == 'z':
                        if distance <= box.r + portal.w:
                            thrustBox(app, app.portals[1].facing, force, box)
                            box.x = app.portals[1].x + xSpace
                            box.y = app.portals[1].y + ySpace
                            box.z = app.portals[1].z + zSpace
                            box.speed = 0
                            box.force = 0
                            box.bounceCount = 0
                            app.teleportDelay = time.time()
                            checkLegelBoxMove(app, box)
                    elif portal.facing == '-x':
                        if distance <= box.r + portal.w:
                            thrustBox(app, app.portals[1].facing, force, box)
                            box.x = app.portals[1].x + xSpace
                            box.y = app.portals[1].y + ySpace
                            box.z = app.portals[1].z + zSpace
                            box.speed = 0
                            box.force = 0
                            box.bounceCount = 0
                            app.teleportDelay = time.time()
                            checkLegelBoxMove(app, box)
                    elif portal.facing == '-z':
                        if distance <= box.r + portal.w:
                            thrustBox(app, app.portals[1].facing, force, box)
                            box.x = app.portals[1].x + xSpace
                            box.y = app.portals[1].y + ySpace
                            box.z = app.portals[1].z + zSpace
                            box.speed = 0
                            box.force = 0
                            box.bounceCount = 0
                            app.teleportDelay = time.time()
                            checkLegelBoxMove(app, box)
                ################### TELEPORT TO BLUE PORTAL ########################
                else:
                    i = ['x', 'y', 'z', '-x', '-z'].index(app.portals[0].facing)
                    xSpace, ySpace, zSpace = spaces[i]  
                    if portal.facing == 'x':
                        if distance <= box.r + portal.w:
                            thrustBox(app, app.portals[0].facing, force, box)
                            box.x = app.portals[0].x + xSpace
                            box.y = app.portals[0].y + ySpace
                            box.z = app.portals[0].z + zSpace
                            box.speed = 0
                            box.force = 0
                            box.bounceCount = 0
                            app.teleportDelay = time.time()
                            checkLegelBoxMove(app, box)
                    elif portal.facing == 'y':
                        if distance <= box.r + portal.h: 
                            thrustBox(app, app.portals[0].facing, force, box)
                            box.x = app.portals[0].x + xSpace
                            box.y = app.portals[0].y + ySpace
                            box.z = app.portals[0].z + zSpace
                            app.teleportDelay = time.time()
                            checkLegelBoxMove(app, box)
                    elif portal.facing == 'z':
                        if distance <= box.r + portal.w:
                            thrustBox(app, app.portals[0].facing, force, box)
                            box.x = app.portals[0].x + xSpace
                            box.y = app.portals[0].y + ySpace
                            box.z = app.portals[0].z + zSpace
                            box.speed = 0
                            box.force = 0
                            box.bounceCount = 0
                            app.teleportDelay = time.time()
                            checkLegelBoxMove(app, box)
                    elif portal.facing == '-x':
                        if distance <= box.r + portal.w:
                            thrustBox(app, app.portals[1].facing, force, box)
                            box.x = app.portals[1].x + xSpace
                            box.y = app.portals[1].y + ySpace
                            box.z = app.portals[1].z + zSpace
                            box.speed = 0
                            box.force = 0
                            box.bounceCount = 0
                            app.teleportDelay = time.time()
                            checkLegelBoxMove(app, box)
                    elif portal.facing == '-z':
                        if distance <= box.r + portal.w:
                            thrustBox(app, app.portals[1].facing, force, box)
                            box.x = app.portals[1].x + xSpace
                            box.y = app.portals[1].y + ySpace
                            box.z = app.portals[1].z + zSpace
                            box.speed = 0
                            box.force = 0
                            box.bounceCount = 0
                            app.teleportDelay = time.time()
                            checkLegelBoxMove(app, box)
                bluePortal = not bluePortal

# Detects if box is near player, picks it up
def pickUpBox(app):
    player = app.player
    x0 = player.x
    y0 = player.y
    z0 = player.z
    for box in app.boxes:
        x1 = box.x 
        y1 = box.y
        z1 = box.z
        distance = getDistance(app, [x0, y0, z0], [x1, y1, z1])
        if (distance < (box.r + player.width + 10)) and (not app.holdingBox):
            box.pickedUp = True
            app.holdingBox = True
            box.speed = 0
            box.bounceCount = 0
            box.force = 15
            updateBoxProjections(app)
            return
    step = player.width + 10 + 40
    iHat, jHat = getBoxPlacementNormalVecs(app)
    translateZ = step * numpy.array(iHat)
    translateX = step * numpy.array(jHat)
    for box in app.boxes:
        if box.pickedUp and app.holdingBox:
            box.pickedUp = False
            app.holdingBox = False
            box.bounceCount = 0
            box.force = 15
            box.speed = 0
            newBoxCoords = numpy.array([box.x, 0, box.z]) + translateX
            box.x, box.z = newBoxCoords[0], newBoxCoords[2]
            updateBoxProjections(app)

# Checks if player move is legal (In bounds, not inside a wall)
def checkLegalMove(app, newCoords):
    x, y, z = newCoords
    player = app.player
    xBound = -500
    yBound = 0
    zBound = -500
    if x - player.width < xBound or x + player.width >= xBound * -1:
        return False
    elif z - player.width < zBound or z + player.width >= zBound * -1:
        return False
    for wall in app.walls:
        w = player.width
        if player.y - player.height >= wall.y + wall.h:
            if x - w <= wall.x + wall.l and x + w >= wall.x - wall.l and z - w <= wall.z + wall.w and z + w >= wall.z - wall.w:
                player.restingY = wall.y + wall.h + player.height
                return True
        else:
            if x - w <= wall.x + wall.l and x + w >= wall.x - wall.l and z - w <= wall.z + wall.w and z + w >= wall.z - wall.w: 
                return False
    player.restingY = player.height
    return True

# Checks if boxes are in legal position (on ground, on top of walls)
def checkLegelBoxMove(app, box):
    x, y, z = box.x, box.y, box.z
    w = box.r
    for wall in app.walls:
        if box.y - box.r <= wall.y + wall.h:
            if x - w <= wall.x + wall.l and x + w >= wall.x - wall.l and z - w <= wall.z + wall.w and z + w >= wall.z - wall.w: 
                box.restingY = wall.y + wall.h + w
                box.force = 0
        else: 
            if x - w <= wall.x + wall.l and x + w >= wall.x - wall.l and z - w <= wall.z + wall.w and z + w >= wall.z - wall.w: 
                box.restingY = wall.y + wall.h + w
                box.force = 0
            else: box.restingY = box.r

# Detects if button has player or box on top of it
def detectPress(app):
    player = app.player
    x0, y0, z0 = player.x, player.y, player.z
    d = dict()
    r = 0
    for box in app.boxes:
        d[box] = [box.x, box.y, box.z]
        r = box.r
    for button in app.buttons:
        pressedFlag = False
        x1, y1, z1 = button.x, button.y, button.z
        distance = getDistance(app, [x0, y0, z0], [x1, y1, z1])
        if distance <= math.sqrt((player.width + button.r)**2 + (player.height ** 2)):
            button.buttonPressed = True
            pressedFlag = True
            button.generateCube(app)
            button.generationFlag = True
            unlockDoor(app)
        for key in d:
            x2, y2, z2 = d[key]
            distance = getDistance(app, [x2, y2, z2], [x1, y1, z1])
            if distance <= math.sqrt((r + button.r) ** 2 + (r ** 2)):
                button.buttonPressed = True
                pressedFlag = True
                button.generateCube(app)
                button.generationFlag = True
                unlockDoor(app)
                break
        if not pressedFlag: 
            button.buttonPressed = False
            unlockDoor(app)
    updateButtonProjections(app)

# Detects if player is in door while it is unlocked
def detectWin(app):
    player, door = app.player, app.door
    if not door.unlocked: return
    x0, y0, z0 = player.x, player.y, player.z
    x1, y1, z1 = door.x, door.y, door.z
    distance = getDistance(app, [x0, y0, z0], [x1, y1, z1])
    if distance <= math.sqrt( abs(player.y - door.y) ** 2 + (player.width * 2) ** 2 ):
        app.level += 1
        resetLevel(app)

# Unlocks door if button is being pressed
def unlockDoor(app):
    door = app.door
    button = app.buttons[0] # First button opens door
    if app.buttons == []: door.unlocked = True 
    elif button.buttonPressed: 
        door.unlocked = True
    else: door.unlocked = False
    updateDoorProjection(app)

# Returns distance from 2 points
def getDistance(app, p1, p2):
    x1, x2 = p1[0], p2[0]
    y1, y2 = p1[1], p2[1]
    z1, z2 = p1[2], p2[2]
    return math.sqrt( ((x1 - x2) ** 2) + ((y1 - y2) ** 2) + ((z1 - z2) ** 2) )

# Updates the box's speed and sends it upward
def thrustBox(app, face, thrust, box):
    if face == 'y':
        box.speed = 0
        box.force = thrust
        box.start = time.time()
        box.bounceCount = 0
        box.restingY = box.y

# Updates the player's speed and sends it upward
def thrust(app, face, thrust):
    player = app.player
    if face == 'y':
        player.speed = thrust
        player.start = time.time()

############################### PROJECTION MATH ################################

# CITATION: Formulas for projection and project from 3DGraphicsDemo.py from TA led mini lecture
def projection(app):
    vecLookAtToCamera = numpy.array(app.cameraCoords) - numpy.array(app.lookAtCoords)
    # Convert vector into unit vector
    vecLookAtToCamera = vecLookAtToCamera / numpy.linalg.norm(vecLookAtToCamera)
    jHat = numpy.cross(vecLookAtToCamera, numpy.array([0, 1, 0]))
    iHat = numpy.cross(vecLookAtToCamera, jHat)
    app.M = numpy.array([
    [  jHat[0],   jHat[1],   jHat[2],                                  0]   ,
    [  iHat[0],   iHat[1],   iHat[2],                                  0]   ,
    [vecLookAtToCamera[0], vecLookAtToCamera[1], vecLookAtToCamera[2], 0]   ,
    [app.cameraCoords[0],  app.cameraCoords[1],  app.cameraCoords[2],  1]])

# Matrix multiply projection matrix with point coords
def project(app, point):
    projection = app.M @ numpy.array([point[0], point[1], point[2], 1])
    # Map 2D point to pixel in window
    projectedX = projection[0] + app.width / 2
    projectedY = projection[1] + app.height / 2
    return [projectedX, projectedY]

################################## DRAW ########################################

def drawRayCastPoint(app, canvas):
    if app.rayCastCoords != None:
        cx, cy = app.rayCastPoint[0], app.rayCastPoint[1]
        r = 10
        # canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill = 'orange')
        canvas.create_line(cx -r, cy, cx + r, cy, fill = 'black', width = 1)
        canvas.create_line(cx, cy - r, cx, cy + r, fill = 'black', width = 1)

def drawAxis(app, canvas):
    for point1, point2 in app.roomLines:
        x0, y0 = project(app, point1)
        x1, y1 = project(app, point2)
        canvas.create_line(x0, y0, x1, y1)

def drawWalls(app, canvas):
    for wall in app.walls:
        d = app.wallPoints[wall]
        x1, y1, x0, y0, x2, y2, x3, y3 = d['front']
        canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')
        x1, y1, x0, y0, x2, y2, x3, y3 = d['top']
        canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')
        x1, y1, x0, y0, x2, y2, x3, y3 = d['right']
        canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')
        x1, y1, x0, y0, x2, y2, x3, y3 = d['bottom']
        canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')
        x1, y1, x0, y0, x2, y2, x3, y3 = d['left']
        canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')
        x1, y1, x0, y0, x2, y2, x3, y3 = d['back']
        canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')

def drawPortalMouseHover(app, canvas):
    cx, cy = app.mouseCoords
    w = 25
    h = 1.5*w
    width = 6
    canvas.create_arc(cx - w, cy - h, cx + w, cy + h, style = 'arc',
        start = '90', extent = '160', width = width, outline = 'dodger blue')
    canvas.create_arc(cx - w, cy - h, cx + w, cy + h, style = 'arc',
        start = '270', extent = '160', width = width, outline = 'orange')
    if app.portals[0].active: # Check if blue portal is active
        canvas.create_arc(cx - w, cy - h, cx + w, cy + h, style = 'arc',
        start = '95', extent = '150', width = 2, outline = 'white')
    if app.portals[1].active: # Check if orange portal is active
        canvas.create_arc(cx - w, cy - h, cx + w, cy + h, style = 'arc',
        start = '275', extent = '150', width = 2, outline = 'white')

def drawBox(app, canvas):
    for box in app.boxPoints:
        for side in box:
            x0, y0 = side[0], side[1]
            x1, y1 = side[2], side[3]
            x3, y3 = side[4], side[5]
            x2, y2 = side[6], side[7]
            canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
            outline = 'black')

def drawButtons(app, canvas):
    counter = -1
    for bottom, top in app.buttonPoints:
        color = 'red'
        counter += 1
        if counter > 0:
            color = 'blue'
        # BOTTOM
        x0, y0 = bottom[0], bottom[1]
        x1, y1 = bottom[2], bottom[3]
        x2, y2 = bottom[4], bottom[5]
        x3, y3 = bottom[6], bottom[7]
        # TOP
        x4, y4 = top[0], top[1]
        x5, y5 = top[2], top[3]
        x6, y6 = top[4], top[5]
        x7, y7 = top[6], top[7]
        canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, outline = color, fill = '')
        canvas.create_line(x0, y0, x4, y4, fill = color)
        canvas.create_line(x1, y1, x5, y5, fill = color)
        canvas.create_line(x2, y2, x6, y6, fill = color)
        canvas.create_line(x3, y3, x7, y7, fill = color)
        canvas.create_polygon(x4, y4, x5, y5, x6, y6, x7, y7, outline = color, fill = '')

def drawPortals(app, canvas):
    if app.portalPoints == []: return
    for points in app.portalPoints:
        x0, y0 = points[0], points[1]
        x1, y1 = points[2], points[3]
        x2, y2 = points[4], points[5]
        x3, y3 = points[6], points[7]
        x4, y4 = points[8], points[9]
        x5, y5 = points[10], points[11]
        x6, y6 = points[12], points[13]
        x7, y7 = points[14], points[15]
        color = points[16]
        canvas.create_line(x0, y0 , x1, y1, fill = color, width = 2)
        canvas.create_line(x2, y2 , x1, y1, fill = color, width = 2)
        canvas.create_line(x2, y2 , x3, y3, fill = color, width = 2)
        canvas.create_line(x4, y4 , x3, y3, fill = color, width = 2)
        canvas.create_line(x4, y4 , x5, y5, fill = color, width = 2)
        canvas.create_line(x6, y6 , x5, y5, fill = color, width = 2)
        canvas.create_line(x6, y6 , x7, y7, fill = color, width = 2)
        canvas.create_line(x0, y0 , x7, y7, fill = color, width = 2)

def drawExit(app, canvas):
    door = app.door
    frame = app.doorPoints['frame']
    sign = app.doorPoints['sign']
    split = app.doorPoints['split']
    doorColor = 'snow2'
    signColor = 'brown1'
    signOutline = 'brown2'
    splitOn = True
    if door.unlocked:
        doorColor = 'MistyRose3'
        signColor = 'SeaGreen2'
        signOutline = 'SeaGreen3'
        splitOn = False
    x0, y0, x1, y1 = frame[0], frame[1], frame[2], frame[3]
    x2, y2, x3, y3 = frame[4], frame[5], frame[6], frame[7]
    x4, y4, x5, y5 = frame[8], frame[9], frame[10], frame[11]
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, 
                            fill = doorColor, outline = 'black')
    x0, y0, x1, y1 = sign[0], sign[1], sign[2], sign[3]
    x2, y2, x3, y3 = sign[4], sign[5], sign[6], sign[7]
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, 
                            fill = signColor, outline = signOutline)
    if splitOn: canvas.create_line(split[0], split[1], split[2], split[3])
    
def drawPlayer(app, canvas):
    x0, y0, x1, y1, x3, y3, x2, y2 = app.playerPoints['front']
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')
    x0, y0, x1, y1, x3, y3, x2, y2 = app.playerPoints['top']
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')
    x0, y0, x1, y1, x3, y3, x2, y2 = app.playerPoints['back']
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')
    x0, y0, x1, y1, x3, y3, x2, y2 = app.playerPoints['right']
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')
    x0, y0, x1, y1, x3, y3, x2, y2 = app.playerPoints['left']
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')
    x0, y0, x1, y1, x3, y3, x2, y2 = app.playerPoints['bottom']
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, fill = '',
        outline = 'black')

def drawPlayerShadow(app, canvas):
    if app.playerShadowPoints == []: return
    points = app.playerShadowPoints
    color = 'gray90'
    outline = 'snow2'
    x0, y0, x1, y1 = points[0], points[1], points[2], points[3]
    x2, y2, x3, y3 = points[4], points[5], points[6], points[7]
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, 
                            outline = outline, fill = color)

def drawCubeGeneration(app, canvas):
    for button in app.buttons:
        if button.generationCoords != []:
            x0, y0, x1, y1, x2, y2, x3, y3 = app.cubeGenerationPoints[button] 
            canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3,
             fill = 'wheat1', outline = 'gold', width = 1)

def redrawAll(app, canvas):
    if app.level == 0:
        canvas.create_text(app.width // 2, app.height // 3, 
                text = 'Portal', font = 'Magneto 60')
        cx, cy = app.width // 2.5, app.height // 3
        w = 50
        h = 1.5*w
        width = 10
        canvas.create_arc(cx - w - 20, cy - h, cx + w - 20, cy + h, style = 'chord',
        start = '110', extent = '180', outline = '', fill = 'white')
        canvas.create_arc(cx - w - 20, cy - h, cx + w - 20, cy + h, style = 'arc',
        start = '30', extent = '280', width = width, outline = 'dodger blue')
        cx, cy = app.width * .6, app.height // 3
        canvas.create_arc(cx - w + 20, cy - h, 20 + cx + w, cy + h, style = 'chord',
        start = '290', extent = '180', outline = '', fill = 'white')
        canvas.create_arc(cx - w + 20,  cy - h, cx + w + 20, cy + h, style = 'arc',
        start = '210', extent = '290', width = width, outline = 'orange')
        
        canvas.create_text(app.width // 2, app.height * .75, 
        text = "Press 'Enter' to begin", font = 'Courier 20')
        canvas.create_text(app.width // 6, app.height * .9, 
        text = "Aim: Mouse\nJump: 'Space'\nMove player: 'WASD'\nPan camera: arrow keys\nShoot portals: Left and Right click\nPick up and place down boxes: 'E'",
        font = 'Ubuntu 15', fill = 'gray42')
        canvas.create_text(app.width * .85, app.height * .9, 
        text = 'Objective: Get to the exit', font = 'Ubuntu 15')
        canvas.create_text(app.width * .85, app.height * .9, 
        text = '\n\nRed Buttons unlock the exit', font = 'Ubuntu 15', 
        fill = 'red')
        canvas.create_text(app.width * .85, app.height * .9, 
        text = '\n\n\n\nBlue Buttons generate a box', font = 'Ubuntu 15', 
        fill = 'dodger blue')

        canvas.create_rectangle(-5, app.height // 2, app.width,
         app.height // 2 + 15, fill = 'dodger blue', outline = '')
        canvas.create_rectangle(-5, app.height // 2 + 25, 
        app.width, app.height // 2 + 40, fill = 'orange', outline = '')
        return
    elif app.gameOver == True:
        canvas.create_text(app.width // 2, app.height // 3, 
                text = "Game Complete!", font = 'Lato 50')
        cx, cy = app.width // 2, app.height // 2
        w = 50
        h = 1.5*w
        width = 10
        canvas.create_arc(cx - w, cy - h, cx + w, cy + h, style = 'arc',
        start = '90', extent = '160', width = width, outline = 'dodger blue')
        canvas.create_arc(cx - w, cy - h, cx + w, cy + h, style = 'arc',
        start = '270', extent = '160', width = width, outline = 'orange')
        canvas.create_text(app.width // 2, app.height * .75, 
                text = "You've successfully escaped the Aperture testing chambers!", font = 'Courier 30')
        canvas.create_text(app.width // 2, app.height * .8, 
                text = "Thank you for playing", font = 'Modern 20')
        canvas.create_text(app.width // 2, app.height * .9, 
                text = "Created By: Justin Soza-Soto", font = 'Modern 20')
        return
    if app.level > 0 and (not app.gameOver):
        canvas.create_text(app.width//2, app.height * .95, 
        text = f'Chamber {app.level}',
        font = 'Courier 20')
    drawAxis(app, canvas)
    drawCubeGeneration(app, canvas)
    drawWalls(app, canvas)
    drawPlayerShadow(app, canvas)
    drawBox(app, canvas)
    drawButtons(app, canvas)
    drawExit(app, canvas)
    drawPortals(app, canvas)
    drawPlayer(app, canvas)
    drawRayCastPoint(app, canvas)
    drawPortalMouseHover(app, canvas)
    if app.rayCastPoint != None:
        player = app.player
        x1, y1 = app.rayCastPoint
        xP, yP = project(app, [player.x, player.y, player.z])
        canvas.create_line(xP, yP, x1, y1, fill = 'red')
        if app.showRay:
            x, y, z = app.prevCameraCoords
            xP, yP = project(app, [x, y, z])
            canvas.create_line(xP, yP, x1, y1, fill = 'blue')

def runTermProject():
    runApp(width = 1000, height = 800)
runTermProject()