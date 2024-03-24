import png
import numpy as np
import pygame
import math
import threading
import sys
from PIL import Image
import random
import os

width = 100
height = width
scale = 1
wheelCount = -20
winScale = math.floor(600 / width)
maxReps = 338
dataType = np.complex128

transX = -0.6373537012997929
transY = 0.40434321082891456

running = True
explore = True
min = -20
step = 0.5
max = 294

halfW = width / 2
halfH = height / 2
xDenom =  1 / (width * scale) 
yDenom =  1 / (height * scale)
'''
colors = [
        (0, 0, 0),
        (66, 30, 15),
        (25, 7, 26),
        (9, 1, 47),
        (4, 4, 73),
        (0, 7, 100),
        (12, 44, 138),
        (24, 82, 177),
        (57, 125, 209),
        (134, 181, 229),
        (211, 236, 248),
        (241, 233, 191),
        (248, 201, 95),
        (255, 170, 0),
        (204, 128, 0),
        (153, 87, 0),
        (106, 52, 3)
        ]
'''
colors = [
        (0, 0, 0),
        (0, 0, 255),
        (255, 255, 255),
        (255, 255, 0)
        ]

def lerp(c1, c2, t):
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return (
            r2 * t + r1 * ( 1 - t ),
            g2 * t + g1 * ( 1 - t ),
            b2 * t + b1 * ( 1 - t )
           )
def constrain(val, min_val, max_val):
    if math.isnan(val): return max_val
    if val < min_val: return min_val
    if val > max_val: return max_val

    return val
    
def hsb_to_rgb(hue, saturation, brightness):
    if saturation == 0:
        r = g = b = int(brightness * 255)
    else:
        h = hue / 60.0
        i = int(h)
        f = h - i
        p = brightness * (1 - saturation)
        q = brightness * (1 - saturation * f)
        t = brightness * (1 - saturation * (1 - f))

        if i == 0:
            r, g, b = brightness, t, p
        elif i == 1:
            r, g, b = q, brightness, p
        elif i == 2:
            r, g, b = p, brightness, t
        elif i == 3:
            r, g, b = p, q, brightness
        elif i == 4:
            r, g, b = t, p, brightness
        else:
            r, g, b = brightness, p, q

        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)

    return r, g, b
    
def col(mag):
    mag = ( mag * 4 )
    #return (mag, mag, mag)
    #return hsb_to_rgb(mag, 0.8, 1)
    c1 = colors[  math.floor(mag / 360 * len(colors)) % len(colors)]
    c2 = colors[( math.floor(mag / 360 * len(colors)) + 1 ) % len(colors)]

    return lerp(c1, c2, mag / 360 * len(colors) - math.floor(mag / 360 * len(colors)))



def create(name, explore, width, height):
    pixels = np.full((width, height), 0, dtype=np.uint16)

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

    counts = np.full((width, height), 1)
    total = 0

    for i in range(maxReps): # pass 1
        Z[M] = Z[M] * Z[M] + C[M]
        overWrite = np.logical_and(M, np.abs(Z) > 2)
        pixels[overWrite] = i
        M[np.abs(Z) > 2] = False
    
    Z = np.floor(np.log(np.abs(Z)) / math.log(2))
    Z = Z.astype(np.uint16)
    pixels[np.logical_not(M)] += Z[np.logical_not(M)] + 1
    
    minPix = np.nanmin(pixels)
    maxPix = np.nanmax(pixels)

    if not explore:
        # png.from_array(pixels, 'L').save(name)
        out = np.full((width, height, 3), 0, dtype=np.uint8)
        for y in range(len(pixels)):
            for x in range(len(pixels[0])):
                out[y, x] = col(pixels[y, x])
        Image.fromarray(out).save(name)
    else:
        for y in range(len(pixels)):
            for x in range(len(pixels[y])):
                #print(y, x)
                pygame.draw.rect(win, col(pixels[y, x]), (x * winScale, y * winScale, winScale, winScale))

if(len(sys.argv) > 1):
    wheelCount = float(sys.argv[1])
    maxReps = int(sys.argv[2])
    transX = float(sys.argv[3])
    transY = float(sys.argv[4])


    scale = math.exp(wheelCount / 10)
    xDenom = 1 / (width * scale)
    yDenom = 1 / (height * scale)
    halfW = width / 2
    halfH = height / 2

    create(sys.argv[5], False, 1000, 1000)
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
            maxReps += 1
        if keys[pygame.K_MINUS]:
            maxReps -= 1
        if keys[pygame.K_s]:
            # create("save{}.png".format(random.randint(0, 1000)), False, 1000, 1000)
            os.popen(
                    "python3 "
                    + "mandelbrotCopy.py "
                    + str(wheelCount) + " "
                    + str(maxReps) + " "
                    + str(transX) + " "
                    + str(transY) + " "
                    + "save{}.png".format(random.randint(0, 1000))   
            )
    transX += x / (width ) / scale
    transY += y / (height ) / scale
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
