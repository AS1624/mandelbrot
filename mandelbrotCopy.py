import png
import numpy as np
import pygame
import math
import threading
import sys


width = 1000
height = width
scale = 1
wheelCount = -20
winScale = math.floor(600 / width)
maxReps = 70
dataType = np.complex128

transX = -0.15748662592470025
transY = 1.0252715546584952

explore = False
min = -20
step = 1
offset = 0.1
this = sys.argv[0]
this = this if type(this) is type(0) else 0
max = 170

wheelCount += this
halfW = width / 2
halfH = height / 2
xDenom =  1 / (width * scale) 
yDenom =  1 / (height * scale) 

def constrain(val, min_val, max_val):
    if math.isnan(val): return max_val
    if val < min_val: return min_val
    if val > max_val: return max_val

    return val
def col(mag):
#    print(mag)
    mag = math.sqrt(mag / maxReps) * 255
    # return (mag, mag, mag)
    return mag

def create(name):
    pixels = np.full((width, height), 0, dtype=np.uint8)

    Z = np.zeros((width, height), dtype=dataType)

    x = np.linspace(
        - halfW * xDenom + transX,
          halfW * xDenom + transX, 
        num=height
    ).reshape((1, height))
    y = np.linspace(
        - halfH * yDenom + transY, 
          halfH * yDenom + transY, 
        num=width
    ).reshape((width, 1))

    C = np.tile(x, (width, 1)) + 1j * np.tile(y, (1, height))
    C.dtype = dataType

    M = np.full((width, height), True, dtype=bool)

    counts = np.zeros(maxReps)
    total = 0

    for i in range(maxReps): # pass 1
        Z[M] = Z[M] * Z[M] + C[M]
        overWrite = np.logical_and(M, np.abs(Z) > 2)
        pixels[overWrite] = col(i)
        M[np.abs(Z) > 2] = False
    '''    
    for y in range(len(pixels)): # pass 2
        for x in range(len(pixels[y])):
            counts[pixels[y, x]] += 1
    
    for i in range(maxReps): # pass 3
        total += counts[i]

    for y in range(len(pixels)): # pass 4
        for x in range(len(pixels[0])):
            iterations = pixels[y, x]
            pixels[y, x] = 0
            for i in range(iterations + 1):
                pixels[y, x] += counts[i] / total
   '''
    if not explore:
        png.from_array(pixels, 'L').save(name)
    if explore:
        for y in range(len(pixels)):
            for x in range(len(pixels[y])):
                pygame.draw.rect(win, col(pixels[y, x]), (x * winScale, y * winScale, winScale, winScale))
if explore:
    pygame.init()

    win = pygame.display.set_mode((width * winScale, height * winScale))
    clock = pygame.time.Clock()

running = True
while running:
    if not explore:
        print("wheelCount: ", wheelCount)
    if explore:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                wheelCount += event.y
        x, y = (0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            x -= 20 / clock.get_fps()
        if keys[pygame.K_RIGHT]:
            x += 20 / clock.get_fps()
        if keys[pygame.K_UP]:
            y -= 20 / clock.get_fps()
        if keys[pygame.K_DOWN]:
            y += 20 / clock.get_fps()
        if keys[pygame.K_EQUALS]:
            maxReps += 1
        if keys[pygame.K_MINUS]:
            maxReps -= 1

    x, y = (0, 0)
    transX += x / (width ) / scale
    transY += y / (height ) / scale
    scale = math.exp(wheelCount / 10)

    xDenom = 1 / (width * scale)
    yDenom = 1 / (height * scale)

    halfW = width / 2
    halfH = height / 2
    
    create("movie/{:03d}.png".format(int( 
        (wheelCount - min ) 
        / (step * offset) 
        + this
    )))
    if not explore:
        wheelCount += step
        if wheelCount > max:
            running = False
    if explore:
        pygame.draw.line(win, 0x888888, (width * winScale / 2, 0), (width * winScale / 2, height * winScale))
        pygame.draw.line(win, 0x888888, (0, height * winScale / 2), ( width * winScale, height * winScale / 2))

        pygame.display.update()
# create("test.png")
