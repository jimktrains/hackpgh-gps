#!/usr/bin/python3

import serial
import NMEA

# All of these but the port are the default values
# Included for clairty
ser = serial.Serial(port='/dev/ttyUSB0',
                    baudrate=9600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE)

while True:
    line = ser.readline()
    sentence = NMEA.Sentence.parse(line)
    if sentence:
        print(sentence)
