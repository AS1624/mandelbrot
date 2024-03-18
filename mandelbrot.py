import png
import numpy
import pygame
import math
import threading


width = 50
height = width
scale = 1
wheelCount = 0
winScale = math.floor(600 / width)
maxReps = 30

transX = 0
transY = 0

halfW = width / 2
halfH = height / 2
xDenom =  1 / (width * scale) 
yDenom =  1 / (height * scale) 

class num:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag
        self.real_sq = real * real
        self.imag_sq = imag * imag
    
    def __add__(self, other):
        return num(self.real + other.real, self.imag + other.imag)
    
    def __sub__(self, other):
        return num(self.real - other.real, self.imag - other.imag)
    
    def __mul__(self, other):
        return num(self.real * other.real - self.imag * other.imag,
                   self.imag * other.real + self.real * other.imag)
    
    def sq(self):
        imag = self.real * self.imag
        return num(self.real_sq - self.imag_sq, 
                   imag + imag)
    
    def magSqr(self):
        return self.real_sq + self.imag_sq

def newC(x, y):
    return num(
        (x - halfW ) * xDenom + transX,
        (y - halfH ) * yDenom + transY
    )
def constrain(val, min_val, max_val):
    if math.isnan(val): return max_val
    if val < min_val: return min_val
    if val > max_val: return max_val

    return val
def col(mag):
    return (255 - mag, 128, 0)

def create(name):
    pixels = numpy.zeros((width, height), dtype=numpy.uint8)

    for y in range(len(pixels)):
        # print(str(int(y / len(pixels) * 100)) + "%", flush=True)
        for x in range(len(pixels[y])):
            
            c = newC(x, y)
            z = c + num(0, 0)

            # print(z.real)
            for i in range(maxReps):
                z = z.sq() + c
                if(z.magSqr() >= 4):
                    i = maxReps
                    pixels[y, x] = 255
            
            # mag = constrain(z.magSqr(), 0, 4 - 1 / 64) * 64
            # pixels[y, x] = mag


    for y in range(len(pixels)):
        for x in range(len(pixels[y])):
            pygame.draw.rect(win, col(pixels[y, x]), (x * winScale, y * winScale, winScale, winScale))


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