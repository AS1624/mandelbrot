import png
import numpy as np
import pygame
import math
import threading


width = 200
height = width
scale = 1
wheelCount = 0
winScale = math.floor(600 / width)
maxReps = 30
dataType = np.complex128

transX = 0
transY = 0

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
    return (255 - mag, 128, 0)

def create(name):
    pixels = np.zeros((width, height), dtype=np.integer)

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

    for i in range(maxReps):
        Z[M] = Z[M] * Z[M] + C[M]
        overWrite = M + np.abs(Z) > 2
        pixels[overWrite] = i
        M[np.abs(Z) > 2] = False
    
    for y in range(len(pixels)):
        for x in range(len(pixels[y])):
            counts[pixels[y, x]] += 1
    

    for y in range(len(pixels)):
        for x in range(len(pixels[y])):
            pygame.draw.rect(win, (col(0) if M[y, x] else col(255)), (x * winScale, y * winScale, winScale, winScale))


pygame.init()

win = pygame.display.set_mode((width * winScale, height * winScale))
clock = pygame.time.Clock()

running = True
while running:
    print(maxReps, clock.get_fps())
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            wheelCount += event.y
            scale = math.exp(wheelCount / 10)

            xDenom = 1 / (width * scale)
            yDenom = 1 / (height * scale)
    x, y = (0, 0)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x -= 1
    if keys[pygame.K_RIGHT]:
        x += 1
    if keys[pygame.K_UP]:
        y -= 1
    if keys[pygame.K_DOWN]:
        y += 1
    if keys[pygame.K_EQUALS]:
        maxReps += 1
    if keys[pygame.K_MINUS]:
        maxReps -= 1

        
    transX += x / (width ) / scale
    transY += y / (height ) / scale
    # print(transX, transY)

    halfW = width / 2
    halfH = height / 2
    
    create("")
    pygame.draw.line(win, 0x888888, (width * winScale / 2, 0), (width * winScale / 2, height * winScale))
    pygame.draw.line(win, 0x888888, (0, height * winScale / 2), ( width * winScale, height * winScale / 2))

    pygame.display.update()