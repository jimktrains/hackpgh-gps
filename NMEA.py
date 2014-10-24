#!/usr/bin/python3

import functools
import re

class Sentence:
    # There are most definatly more (computationally) efficent
    # ways to parse these sentences. However, I'm going for
    # clairty and besides, it's "good enough"
    #
    # NMEA Sentences have a format of $CMD[,param[,param2[...]]]*CKSUM
    # The checksum, CKSUM, is the hex result of XORing everything between
    # the $ and *
    @staticmethod
    def parse(sentence):

        def xor(a, b):
          return a ^ ord(b)
        sentence = sentence.strip();
        

        parts = re.split('[$*]', sentence, 2)

        # If the sentence doesn't split correctly
        # print a message and return
        # Sometimes this happens right when you connect and get only part
        # of a sentence since the device is just streaming back to us.
        if len(parts) != 3:
            print("Malformed sentence.")
            return


        body = parts[1]
        cksum = parts[2]

        # Computes the checksum (xor of all bytes)
        comp_cksum = functools.reduce(xor, body, 0)
        # Converts the checksum to 2-byte hex string
        hex_comp_cksum = '%02X' % comp_cksum

        # If there is a mismatch the data has been corrupted
        # Again, this sometimes happens when you first connect
        # and more rarely randomly when data is actually corrupted
        if hex_comp_cksum != cksum:
            print 'Checksum mismatch! ' + \
                  'Computed %s Expected %s' % (hex_comp_cksum, cksum)
            return

        body = body.split(',')

        # Returns and removes the first item in the list: the command
        cmd = body.pop(0)

        if cmd not in globals():
            print ("NMEA Command %s was recieved," % cmd) + \
                  "but it is not known how to process it"
            return

        return globals()[cmd](body)

class GPRMC:
    STATUS_ACTIVE = 'A'
    STATUS_VOID = 'V'

    def __init__(self, params):
        self.hour = int(params[0][0:2])
        self.minute = int(params[0][2:4])
        self.seconds = float(params[0][4:])

        self.status = params[1]

        if self.status != self.STATUS_VOID:
            # Latitude
            self.latitude_degree = int(params[2][0:2])
            self.latitude_minute = float(params[2][2:])
            self.latitude_direction = params[3]

            self.latitude = self.latitude_degree + self.latitude_minute/60
            if self.latitude_direction == 'S':
                self.latitude = -self.latitude

            # Longitude
            self.longitude_degree = int(params[4][0:3])
            self.longitude_minute = float(params[4][3:])
            self.longitude_direction = params[5]

            self.longitude = self.longitude_degree + self.longitude_minute/60
            if self.longitude_direction == 'W':
                self.longitude = -self.longitude

            self.speed = float(params[6]) # Knots
            self.track_angle = float(params[7])

            self.date_day = int(params[8][0:2])
            self.date_month = int(params[8][2:4])
            self.date_year = 2000 + int(params[8][4:])

    def __str__(self):
        return  "%f,%f %f knots %fdeg @ %4d-%02d-%02d %02d:%02d:%f UTC" % (
                self.latitude,
                self.longitude,
                self.speed,
                self.track_angle,
                self.date_year,
                self.date_month,
                self.date_day,
                self.hour,
                self.minute,
                self.seconds,
        )

class GPGGA:
    FIX_QUALITY_INVALID = 0
    FIX_QUALITY_GPS     = 1
    FIX_QUALITY_DGPS    = 2
    FIX_QUALITY_PPS     = 3
    FIX_QUALITY_RTK     = 4 # Real-time Kinetic
    FIX_QUALITY_FRTK    = 5 # Float RTK
    FIX_QUALITY_EST     = 6 # Dead Reckoning
    FIX_QUALITY_MANUAL  = 7
    FIX_QUALITY_SIMULATION = 8

    

    def __init__(self, params):
        # Fix time, in UTC
        self.hour = int(params[0][0:2])
        self.minute = int(params[0][2:4])
        self.seconds = float(params[0][4:])

        self.fix_quality = int(params[5])

        if self.fix_quality != self.FIX_QUALITY_INVALID:
            # Latitude
            self.latitude_degree = int(params[1][0:2])
            self.latitude_minute = float(params[1][2:])
            self.latitude_direction = params[2]

            self.latitude = self.latitude_degree + self.latitude_minute/60
            if self.latitude_direction == 'S':
                self.latitude = -self.latitude

            # Longitude
            self.longitude_degree = int(params[3][0:3])
            self.longitude_minute = float(params[3][3:])
            self.longitude_direction = params[4]

            self.longitude = self.longitude_degree + self.longitude_minute/60
            if self.longitude_direction == 'W':
                self.longitude = -self.longitude

            self.num_satellites = int(params[6])
            self.hdop = float(params[7])
            self.altitude = float(params[8])
            self.altitude_unit = params[9]
            self.altitude_geod = float(params[10])
            self.altitude_geod_unit = params[11]
            self.time_since_dgps = params[12]
            self.dgps_station_id = params[13]

    def __str__(self):
        if self.fix_quality == self.FIX_QUALITY_INVALID:
            return "INVALID"

        return  "%f,%f +-%f Elv %f Q%d N%d @ %02d:%02d:%f UTC" % (
                self.latitude,
                self.longitude,
                self.hdop,
                self.altitude,
                self.fix_quality,
                self.num_satellites,
                self.hour, 
                self.minute, 
                self.seconds)

class GPGSA:
    FIX_3D_NO = 1
    FIX_3D_2D = 2
    FIX_3D_3D = 3

    SELECTION_AUTO = 'A'
    SELECTION_MANUAL = 'M'

    def __init__(self, params):
        self.selection = params[0]
        self.fix_type  = params[1]

        self.sat_prn = []
        for i in range(2, 14):
            self.sat_prn.append(params[i])

        self.pdop = float(params[14])
        self.hdop = float(params[15])
        self.vdop = float(params[16])

    def __str__(self):
        if self.fix_type == self.FIX_3D_NO:
            return "INVALID"
        return "PDOP +-%f HDOP +-%f VDOP +-%f" % (
            self.pdop,
            self.hdop,
            self.vdop
        )
