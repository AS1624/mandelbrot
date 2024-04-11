import os
import math
import psutil
"""
"wheelCount": 381, "maxReps": 2020, "transX": -0.7490100649853734, "transY": 0.07266128258601036}
"""
min = -20
max = 380
step = 0.5

max_processes = 4

transX = -0.7490100649853734,
transY = 0.07266128258601036
maxReps = 2020

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
