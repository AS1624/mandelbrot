import time
import numpy as np
import pygame
import math
import threading
import sys
from PIL import Image
import random
import os
import json
from numba import jit, njit, prange

width = 150
height = math.floor( width / 16 * 9 )
scale = 1
wheelCount = 30
winScale = 10
maxReps = 820
dataType = np.complex128

transX = -0.7477818340495408 
transY = 0.07254637450717176

# transX, transY = (0, 0)
running = True
explore = True
min = -20
step = 0.5
max = 372

halfW = width / 2
halfH = height / 2
xDenom =  1 / (width * scale) 
yDenom =  1 / (height * scale)

@njit
def _two_sum_quick(x, y):
    r = x + y
    e = y - (r - x)
    return r, e

@njit
def _two_product(x, y):
    r = x*y
    e = 1#fma(x, y, -r)
    return r, e

@njit(fastmath=True)
def lerp(c1, c2, t) -> tuple[int]:
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return (
            r2 * t + r1 * ( 1 - t ),
            g2 * t + g1 * ( 1 - t ),
            b2 * t + b1 * ( 1 - t )
           )

@njit(fastmath=True)
def col(mag) -> tuple[int]:
    colors = [
            (166, 124, 0),
            (128, 128, 255),
            (255, 0, 255),
            (255, 255, 255),
    ]
    mag = math.pow(mag, 1/8) * 300

    c1 = colors[  math.floor(mag / 360 * len(colors)) % len(colors)]
    c2 = colors[( math.floor(mag / 360 * len(colors)) + 1 ) % len(colors)]
    
    if mag == 0:
        return ((0, 0, 0))
    return lerp(c1, c2, mag / 360 * len(colors) - math.floor(mag / 360 * len(colors)))

@njit(parallel=True, fastmath=True)
def calculate(width, height, explore, pixels, Z, M, C, maxReps):
    for x in prange(Z.shape[0]):
        for y in range(Z.shape[1]):
            for i in range(maxReps): # pass 1
                if M[x, y]:
                    Z[x, y] = Z[x, y] * Z[x, y] + C[x, y]
                    if np.abs(Z[x, y]) > 2:
                        pixels[x, y] = i
                        M[x, y] = False
    
    Z = np.floor(np.log(np.abs(Z)) / math.log(2))
    Z = Z.astype(np.uint16)

    for x in range(M.shape[0]):
        for y in range(M.shape[1]):
            if not M[x, y]:
                pixels[x, y] += Z[x, y] + 1
    return pixels

@njit(parallel=True)
def doubleCaclulate(width, height, explore, pixels, Za, Zb, M, Ca, Cb, maxReps):
    for x in prange(Za.shape[0]):
        for y in range(Za.shape[1]):
            for i in range(maxReps): # pass 1
                if M[x, y]:
                    
                    r, e = _two_product(Za[x, y], Za[x, y])
                    e += 2 * Za[x, y] * Zb[x, y]
                    r, e = _two_sum_quick(r, e)

                    Za[x, y], Zb[x, y] = r, e
                    
                    if np.abs(Za[x, y]) > 2:
                        pixels[x, y] = i
                        M[x, y] = False
    
    Za = np.floor(np.log(np.abs(Za)) / math.log(2))
    Za = Za.astype(np.uint16)
    # Assuming pixels, M, and Z are 2D arrays of the same shape
    for x in range(M.shape[0]):
        for y in range(M.shape[1]):
            if not M[x, y]:
                pixels[x, y] += Za[x, y] + 1
    return pixels


@jit(forceobj=True, fastmath=True, parallel=True)
def create(name, explore, width, height):
    pixels = np.full((height, width), 0, dtype=np.uint16)

    halfW = width * 0.5
    halfH = height * 0.5

    Z = np.zeros((height, width), dtype=dataType)
    
    x = np.linspace(
        - halfW / scale + transX,
          halfW / scale + transX, 
        num=width
    ).reshape((1, width))
    y = np.linspace(
        - halfH / scale + transY, 
          halfH / scale + transY, 
        num=height
    ).reshape((height, 1))
    
    C = np.tile(y, (1, width)) * 1j + np.tile(x, (height, 1))
    
    M = np.full((height, width), True, dtype=bool)
    
    pixels = calculate(width, height, explore, pixels, Z, M, C, maxReps)

    if not explore:
        # png.from_array(pixels, 'L').save(name)
        out = np.full((height, width, 3), 0, dtype=np.uint8)
        for y in range(len(pixels)):
            for x in range(len(pixels[0])):
                out[y, x] = col(pixels[y, x])
        Image.fromarray(out).save(name)
    else:
        for y in range(len(pixels)):
            for x in range(len(pixels[y])):
                #print(y, x)
                pygame.draw.rect(win, col(pixels[y, x]), (x * winScale, y * winScale, winScale, winScale))

if(len(sys.argv) == 2):
    with open(sys.argv[1], "r") as f:
        d = json.load(f)
        

        wheelCount = d["wheelCount"]
        maxReps = d["maxReps"]
        transX = d["transX"]
        transY = d["transY"]


        scale = math.exp(wheelCount / 10)
        xDenom = 1 / (width * scale)
        yDenom = 1 / (height * scale)
        halfW = width / 2
        halfH = height / 2

        height = 2160
        width = 3840

        create(sys.argv[1] + ".png", False, width, height)
    exit()

elif(len(sys.argv) > 1):
    wheelCount = float(sys.argv[1])
    maxReps = int(sys.argv[2])
    transX = float(sys.argv[3])
    transY = float(sys.argv[4])


    scale = math.exp(wheelCount / 10)
    xDenom = 1 / (width * scale)
    yDenom = 1 / (height * scale)
    halfW = width / 2
    halfH = height / 2

    create(sys.argv[5], False, 1920, 1080)
    exit()

if explore:
    pygame.init()

    win = pygame.display.set_mode((width * winScale, height * winScale))
    clock = pygame.time.Clock()

while running:
    x, y = (0, 0)
    if not explore:
        print("wheelCount: ", wheelCount)
    if explore:
        shift = False
        print("fps: {:0.1f}".format(clock.get_fps()))
        print(wheelCount, maxReps, transX, transY)
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                wheelCount += event.y
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
            maxReps += 100
        if keys[pygame.K_MINUS]:
            maxReps -= 100
        if keys[pygame.K_LSHIFT]:
            shift = True
        if keys[pygame.K_s]:
            # create("save{}.png".format(random.randint(0, 1000)), False, 1000, 1000)
            os.popen(
                    "python3 "
                    + "mandelbrot.py "
                    + str(wheelCount) + " "
                    + str(maxReps) + " "
                    + str(transX) + " "
                    + str(transY) + " "
                    + "save{}.png".format(random.randint(0, 1000))   
            )
        if keys[pygame.K_p]:
            jsonFile = json.dumps(
                    {
                        "wheelCount": wheelCount,
                        "maxReps": maxReps,
                        "transX": transX,
                        "transY": transY,
                    }
            )
            with open(input("name, no file extention"), "w") as outFile:
                outFile.write(jsonFile)
        
    transX += x / scale
    transY += y / scale
    scale = math.exp(wheelCount / 10)

    xDenom = 1 / (width * scale)
    yDenom = 1 / (height * scale)

    halfW = width / 2
    halfH = height / 2
    
    create("movie/{:03d}.png".format(int( 
        (wheelCount - min ) 
        / (step)
    )),
    explore,
    width,
    height
    )
    if not explore:
        wheelCount += step
        if wheelCount > max:
            running = False
    if explore:
        pygame.draw.line(win, 0x888888, (width * winScale / 2, 0), (width * winScale / 2, height * winScale))
        pygame.draw.line(win, 0x888888, (0, height * winScale / 2), ( width * winScale, height * winScale / 2))

        pygame.display.update()
