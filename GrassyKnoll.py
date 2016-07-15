#!/usr/bin/env python
 
# pixel mapping for a grid of LED matrix panels
def gen_map_2x2():
    matrix = (32, 32)
    top = []
    bot = []
    cur_index = 0
    for y in range(matrix[1]):
        row_top = [x+cur_index for x in range(matrix[0]*2)]
        cur_index = row_top[len(row_top)-1] + 1
        top.append(row_top)
        row_bot = [x+cur_index for x in reversed(range(matrix[0]*2))]
        cur_index = row_bot[0] + 1
        bot.insert(0,row_bot)
    matrix_map = top + bot
    return matrix_map

# LED panel constants
PANEL_ARRAY_WIDTH = 2
PANEL_ARRAY_HEIGHT = 2
CHAIN_LENGTH = PANEL_ARRAY_WIDTH * PANEL_ARRAY_HEIGHT
SQUARE_SIZE = 32
WIDTH = PANEL_ARRAY_WIDTH * SQUARE_SIZE
HEIGHT = PANEL_ARRAY_HEIGHT * SQUARE_SIZE

# initialize LED matrix
from ada_matrix import DriverAdaMatrix
driver = DriverAdaMatrix(rows=SQUARE_SIZE, chain=CHAIN_LENGTH)
driver.SetPWMBits(6) #decrease bit-depth for better performance
from bibliopixel import *
led = LEDMatrix(driver, WIDTH, HEIGHT, coordMap = gen_map_2x2())

# anemometer constants
DELAY = 100 # in milliseconds
AVG_WIDTH = 20 # how many time intervals of anemometer readings to store
# max total anemometer revolutions we want to count in DELAY*AVG_WIDTH ms
MAX_READING = 20 
 
# global variables for anemometer
import time
lastTime = time.time()
current_reading = 0
readings_pos = 0
# array of readings provides time-averaging of the measurement
readings = [0 for i in range(0,AVG_WIDTH)]

# set up GPIO pin to read anemometer.
# anemometer should be connected to channel pin (as labeled on matrix hat) and ground.
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
channel = 18
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# set up callback to add a new reading to the current tally each time there's a signal
def my_callback(channel):
 global readings
 readings[readings_pos] = readings[readings_pos] + 1

# add edge detection on the anemometer channel
GPIO.add_event_detect(channel, GPIO.FALLING, callback=my_callback)  

def circle_mask(radius):
    radius_sq = radius ** 2
    diameter = radius * 2
    mask = [[0 for k in xrange(diameter)] for j in xrange(diameter)]
    for x in xrange(diameter):
        for y in xrange(diameter):
            xc = x - radius + 0.5
            yc = y - radius + 0.5
            if xc ** 2 + yc ** 2 > radius_sq:
                mask[x][y] = 0
            else:
                mask[x][y] = 1
    return mask

mask = circle_mask(WIDTH / 2)

# create noise animation
from noise import pnoise3, snoise3
coords = range(WIDTH)
Bt = [[[0 for k in xrange(WIDTH)] for j in xrange(WIDTH)] for i in xrange(WIDTH)]
Sat = [[[0 for k in xrange(WIDTH)] for j in xrange(WIDTH)] for i in xrange(WIDTH)]
Hue = [[[0 for k in xrange(WIDTH)] for j in xrange(WIDTH)] for i in xrange(WIDTH)]
scale = 1/5.0 # smaller scale = bigger pattern
for z in coords:
    for y in coords:
        for x in coords:
            vBt = snoise3(x * scale, y * scale, z * scale)
            if mask[y][z]:
                Bt[x][y][z] = int((vBt + 3) * 64.0)
            vSat = snoise3(x * scale + 100, y * scale + 100, z * scale + 100)
            Sat[x][y][z] = int((vSat + 1.2) * 115.0)
            vHue = snoise3(x * scale/4 + 200, y * scale/4 + 200, z * scale/4 + 200)
            Hue[x][y][z] = int(vHue * 100.0)

# animation pattern implementation
from bibliopixel.animation import *
class SimplexNoise(BaseMatrixAnim):

    def __init__(self, led):
        super(SimplexNoise, self).__init__(led, width=WIDTH, height=HEIGHT)
        self._step = 1
        self._frame_portion = 1
    
    def step(self, amt=1):
        self._frame_portion = (self._frame_portion + 1) % 4
        irange = self._frame_portion % 2
        jrange = int(self._frame_portion > 1)
        if self._frame_portion == 0:
            self._step = (self._step + amt) % WIDTH 
        current_Bt = Bt[self._step]
        current_Sat = Sat[self._step]
        for i in xrange(irange, WIDTH, 2):
            for j in xrange(jrange, WIDTH, 2):
                self._led.setHSV(i, j, ((110 + (current_reading * Hue[self._step][i][j] / MAX_READING)) % 255,Sat[self._step][i][j],Bt[self._step][i][j])) 

# get animation running
anim = SimplexNoise(led)
anim.run(fps=30, threaded=True)

# poll the sensor indefinitely
while 1:
    current_reading = sum(readings) if sum(readings) < MAX_READING else MAX_READING - 1
    readings_pos = (readings_pos + 1) % AVG_WIDTH
    readings[readings_pos] = 0
    time.sleep(DELAY / 1000.0)

 
# kill animation (fyi)
anim.stopThread()
led.all_off()
led.update()
GPIO.cleanup()
 