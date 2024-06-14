import os
import math
import psutil
from math import exp
"""
"wheelCount": 220, "maxReps": 500, "transX": -0.7558654118335943, "transY": -0.061662310353143644}
"""
min = 220
max = 270
step = 0.5

transX = -0.7558654118335943
transY = -0.061662310353143644
maxReps = 500

def processes():
    running = psutil.process_iter(attrs=['status'])
    
    return sum(1 for p in running if p.info['status'] == 'running') 

for i in range(math.floor( ( max - min ) / step)):
    while processes() > 2 :
        pass
    print(i, "out of", math.floor( ( max - min ) / step))
    maxReps = 600 + int(exp((i+0.5) / 30 + 3) * 4)
    os.popen(
            "python3 mandelbrot.py {} {} {} {} {}"
            .format(
                i * step + min + 0.5,
                maxReps,
                transX,
                transY,
                "movie/" + str(i+0.5) + ".png"
            )
    )
