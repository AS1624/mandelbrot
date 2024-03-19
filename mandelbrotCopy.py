import png
import numpy as np
import pygame
import math
import threading
import sys


width = 100
height = width
scale = 1
wheelCount = -20
winScale = math.floor(600 / width)
maxReps = 70
dataType = np.complex128

transX = -0.15748662592470025
transY = 1.0252715546584952

explore = True
min = -20
step = 1
max = 170

halfW = width / 2
halfH = height / 2
xDenom =  1 / (width * scale) 
yDenom =  1 / (height * scale) 

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
    
def col(mag, min, max):
    mag = math.floor( (mag - min ) / (max - min) * 255)
    # print(mag)
    if explore: return (mag, mag, mag)
    else:       return mag

def create(name, explore, width, height):
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

    counts = np.full((width, height), 1)
    total = 0

    for i in range(maxReps): # pass 1
        Z[M] = Z[M] * Z[M] + C[M]
        overWrite = np.logical_and(M, np.abs(Z) > 2)
        pixels[overWrite] = i
        M[np.abs(Z) > 2] = False
    
    Z = np.floor(np.log(np.abs(Z)) / math.log(2))
    Z = Z.astype(np.uint8)
    pixels += Z 
    pixels.astype(np.uint8)
    
    minPix = np.nanmin(pixels)
    maxPix = np.nanmax(pixels)

    if not explore:
        png.from_array(pixels, 'L').save(name)
    else:
        for y in range(len(pixels)):
            for x in range(len(pixels[y])):
                #print(y, x)
                pygame.draw.rect(win, col(pixels[y, x], minPix, maxPix), (x * winScale, y * winScale, winScale, winScale))
if explore:
    pygame.init()

    win = pygame.display.set_mode((width * winScale, height * winScale))
    clock = pygame.time.Clock()

running = True
while running:
    if not explore:
        print("wheelCount: ", wheelCount)
    if explore:
        print("fps: {:0.1f}".format(clock.get_fps()))
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
        if keys[pygame.K_s]:
            create("save.png", False, 1000, 1000)
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
