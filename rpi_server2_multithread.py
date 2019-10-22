import time
from neopixel import *
import numpy as np
import math
import random
import socket
import json
import numpy as np
import time
import zlib
import skvideo.io
import multiprocessing
import threading

def applyNumpyColors(strip, frame):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(int(frame[i][0][1]), int(frame[i][0][0]), int(frame[i][0][2])))
    strip.show()
    
def strip_thread(lock, video, strip):
    global index
    this_index = 0
    old_index = 0
    while True:
        with lock:
            this_index = index
        
        if not(this_index == old_index):
            frame = video[this_index]
            applyNumpyColors(strip, frame)
            old_index = this_index

def colorWipe(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

def intToBytes(n):
    b = bytearray([0, 0, 0, 0])   # init
    b[3] = n & 0xFF
    n >>= 8
    b[2] = n & 0xFF
    n >>= 8
    b[1] = n & 0xFF
    n >>= 8
    b[0] = n & 0xFF
    return b

def bytesToInt(b):
    n = (b[0]<<24) + (b[1]<<16) + (b[2]<<8) + b[3]
    return n

def recv_all(conn, size):
    data = conn.recv(size)
    while len(data) < size:
        diff = size - len(data)
        data += conn.recv(diff)
        #print('HEJ')
    return data

if __name__ == '__main__':
    # LED strip configuration:
    LED_COUNT      = 144      # Number of LED pixels.
    LED_PIN        = 17      # GPIO pin connected to the pixels (18 uses PWM!).
    #LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

    strip1 = Adafruit_NeoPixel(144, 12, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0)
    strip2 = Adafruit_NeoPixel(288, 13, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1)
    strip3 = Adafruit_NeoPixel(288, 19, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1)
    strip1.begin()
    strip2.begin()
    strip3.begin()

    print('Loading video...')
    video = skvideo.io.vread('videos/cloudless_lights_3.avi')[:, :288]
    print(video.shape)
    video = video*0.2
    video = video.astype(np.uint8)
    fps = 60
    
    global index
    index = 0
    lock = multiprocessing.Lock()
    t1 = threading.Thread(target=strip_thread, args=(lock, np.copy(video), strip1))
    t2 = threading.Thread(target=strip_thread, args=(lock, np.copy(video), strip2))
    t3 = threading.Thread(target=strip_thread, args=(lock, np.copy(video), strip3))
    
    input('Press enter to continue')
    t1.start()
    t2.start()
    t3.start()
    
    start_time = time.time()
    for i in range(len(video)):
        try:
            t = time.time()
            time_should_be = i / fps
            time_is = time.time() - start_time
        
            if time_should_be > time_is:
                time.sleep(1/300)
            else:
                continue
            
            with lock:
                index = i
            
            print(int(1/(time.time() - t)), 'fps')

        except:
            colorWipe(strip1)
            colorWipe(strip2)
            colorWipe(strip3)
            exit()