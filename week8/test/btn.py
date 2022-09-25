import os
import threading
import multiprocessing as mp 
import queue
import serial
import serial.tools.list_ports as list_ports
import PySimpleGUI as sg

from ahrs.filters import Madgwick
from scipy import signal

import numpy as np
import csv
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import time

ser = serial.Serial("COM9", 9600)
while True:
    if ser.is_open:
        data = ser.readline()
        if None != data:
            #print(data.decode("utf-8"))
            line = data.decode("utf-8").strip().split(", ")
            #print(line)
            block = [float(f) for f in line]
            print(block)
