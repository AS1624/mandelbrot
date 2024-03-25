import os
import math
import psutil

min = -20
max = 300
step = 0.5

max_processes = 4

transX = -0.6373537012997929
transY = 0.40434321082891456
maxReps = 334

def processes():
    running = psutil.process_iter(attrs=['pid', 'name', 'status'])
    
    return sum(1 for p in running if p.info['status'] == 'running') 

for i in range(math.floor( ( max - min ) / step)):
    while processes() > max_processes :
        pass
    print(i, "out of", math.floor( ( max - min ) / step))
    os.popen(
            "python3 mandelbrot.py {} {} {} {} {}"
            .format(
                i * step + min, 
                maxReps,
                transX,
                transY,
                "movie/" + str(i) + ".png"
            )
    )
