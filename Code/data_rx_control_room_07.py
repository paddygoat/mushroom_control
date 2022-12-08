#!/usr/bin/env python
# cd /home/paddy/Documents/Mushrooms && python3 data_rx_control_room_06.py

import warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings( "ignore", module = "matplotlib\..*" )

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import random
import serial
import sys
import math
import time

end = "\n"
RED = "\x1b[1;31m"
BLUE="\e[44m"
F_LightGreen = "\x1b[92m"
F_Green = "\x1b[32m"
F_LightBlue = "\x1b[94m"
B_White = "\x1b[107m"
NC = "\x1b[0m" # No Color
Blink = "\x1b[5m"

errorCount = 0
counter = 0

sys.stderr.write("\x1b[94m" + "Start: " + '\x1b[0m' + end) 

#initialize serial port
ser = serial.Serial()
# ser.set_buffer_size(rx_size = 100000, tx_size = 12800)
ser.baudrate = 115200
ser.timeout = 10 #specify timeout when using readline()

try:
    ser.port = '/dev/ttyUSB0' #Arduino serial port
    ser.open()
except:
    ser.port = '/dev/ttyUSB1' #Arduino serial port
    ser.open()

if ser.is_open==True:
        print("\nSerial port now open.\n")
        ser.write(b'Serial port is open.\n')
	# print(ser, "\n") # print serial parameters

# Create figure for plotting
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(1, 1, 1)
xs = [] # time index
yhum = [] # Container humidity values
ytempCon = [] # Container temperature values
ycoTwo = [] # Container CO2/10 values
ypmA = [] # Container particulate values
ypmB = [] # Container particulate values
ypmC = [] # Container particulate values

threeDArray = np.zeros((2, 8, 10), dtype='object')       # fill array with zeros.
# threeDArray = np.select([threeDArray == 0], [""], threeDArray)   # get rid of the zeros.
counter = [10]
counter2 = [1]
delta_time = [2,0]

data_y_hum = [1]
data_y_tempCon = [1]
data_y_coTwo = [1]
data_y_pmA = [1]
data_y_pmB = [1]
data_y_pmC = [1]

data_y_tempGlass = [1]
data_y_moisGlass = [1]

# data_y_hum, data_y_tempCon, data_y_coTwo, data_y_pmA, data_y_pmB, data_y_pmC, data_y_tempGlass, data_y_moisGlass

# This function is called periodically from FuncAnimation
def animate(i, xs, yhum, ytempCon, ycoTwo, ypmA, ypmB, ypmC, data_y_hum, data_y_tempCon, data_y_coTwo, data_y_pmA, data_y_pmB, data_y_pmC, data_y_tempGlass, data_y_moisGlass, threeDArray, counter, counter2, delta_time, errorCount):
    # Make a call back:
    # ser.write(b'S\n')
    start_time = time.time()
    arrayExists = False
    try:
        threeDArray
    except NameError:
        arrayExists = False
        # print("well, threeDArray WASN'T defined after all!")
    else:
        arrayExists = True
        # print("sure, threeDArray was defined.")

    #Aquire and parse data from serial port
    char_data=ser.readline()      # ascii
    char_data = char_data.decode("utf-8")
    # char_data = char_data[0:-2]
    len_char_data = len(char_data)

    detectionHeader = "@>#"
    ContainerHeader = "#*&"
    testGlassHeader = ""
    testDetectHeader = ""
    testContainerHeader = ""
    desiredHeader = "#<~"
    headerGlassTest = False
    headerDetectTest = False
    headerContainerTest = False
    myStringLabel = ""


    if len_char_data >2:
        for i in range(3):
            testGlassHeader = "" + testGlassHeader + str(char_data[i])
            # testDetectHeader = "" + testDetectHeader + str(char_data[i])
            testContainerHeader = "" + testContainerHeader + str(char_data[i])

    # if testDetectHeader == detectionHeader:
        # headerDetectTest = True

    if testGlassHeader == desiredHeader:
        headerGlassTest = True
    else:
        headerGlassTest = False

    if testContainerHeader == ContainerHeader:
        headerContainerTest = True
    else:
        headerContainerTest = False

    if len_char_data >2 and len_char_data <50:
        # Make a call back:
        ser.write(b'C\n')

        # Empty the array:
        for k in range(2):
            for j in range(8):
                for i in range(10):
                    threeDArray[k][j][i] = ""

        digit = 0
        space = 0
        period = 0
        brackets = 0
        colons = 0
        underScore = 0

        i = 0
        j = 0
        k = 0
        jAdjust = 0
        iAdjust = 0
        underScoreCount = 0

        if headerDetectTest == True:
            jAdjust = 4
        for i in range(len_char_data):

            period = 0
            brackets = 0
            colons = 0
            underScore = 0
            digit = char_data[i].isdigit()

            # s.find("r")
            if char_data[i]=='.':period = 1
            if char_data[i]=='_':underScore = 1

            if underScore == 1:
                # print("underScore_i: ",i)
                underScoreCount = underScoreCount +1
                iAdjust = i+1

            if (digit == 0)and(period == 0):
                if underScoreCount == 0:j=0+jAdjust
                if underScoreCount == 1:j=1+jAdjust
                if underScoreCount == 3:j=2+jAdjust
                if underScoreCount == 5:j=3+jAdjust
                if underScore == 0:
                    threeDArray[k][j][i-iAdjust] = char_data[i]

            if (digit == 1)or(period == 1):
                if underScoreCount == 1:j=0+jAdjust
                if underScoreCount == 3:j=1+jAdjust
                if underScoreCount == 5:j=2+jAdjust
                if underScore == 0:
                    threeDArray[k+1][j][i-iAdjust] = char_data[i]

        print("threeDArray 3: ")
        print(threeDArray)
        hum = ""
        tempCon = ""
        coTwo = ""
        pmA = ""
        pmB = ""
        pmC = ""
        myStringLabel = ""
        myStringValue = ""

        a = 0
        b = 0
        c = 0
        d = 0
        e = 0
        f = 0

        for i in range(4):
            if str(threeDArray[0][1][i]) == ":":
                break
            myStringLabel = myStringLabel + str(threeDArray[0][1][i])

        for i in range(6):
            myStringValue = "" + myStringValue + str(threeDArray[1][1][i])

        print("myStringLabel:",myStringLabel)
        print("myStringValue:",myStringValue)

        print("")

        if headerContainerTest == True:
            if (myStringLabel == "hum"):
                data_y_hum[0] = float(myStringValue)
                print("hum detected !!")
            if (myStringLabel == "temp"):
                data_y_tempCon[0] = float(myStringValue)
                print("temp detected !!")
            if (myStringLabel == "coTw"):
                data_y_coTwo[0] = float(myStringValue)
                print("coTwo detected !!")
            if (myStringLabel == "pmA"):
                data_y_pmA[0] = float(myStringValue)
                print("pmA detected !!")
                print("data_y_pmA = ",data_y_pmA)
            if (myStringLabel == "pmB"):
                data_y_pmB[0] = float(myStringValue)
                print("pmB detected !!")
            if (myStringLabel == "pmC"):
                data_y_pmC[0] = float(myStringValue)
                print("pmC detected !!")

            # temp is the last chunk of data to be received:
            if myStringLabel == "temp":
                yhum.append(data_y_hum[0])
                ytempCon.append(data_y_tempCon[0])
                ycoTwo.append(data_y_coTwo[0])
                ypmA.append(data_y_pmA[0])
                ypmB.append(data_y_pmB[0])
                ypmC.append(data_y_pmC[0])

                a = len(yhum)
                b = len(ytempCon)
                c = len(ycoTwo)
                d = len(ypmA)
                e = len(ypmB)
                f = len(ypmC)

                # Check the shapes of the data are coherent:
                xs = range(len(yhum))
                print("Length of xs = ",xs)
                print("Length of yhum = ",a)
                print("Length of ytempCon = ",b)
                print("Length of ycoTwo = ",c)
                print("Length of ypmA = ",d)
                print("Length of ypmB = ",e)
                print("Length of ypmC = ",f)
                print("")

        if headerGlassTest == True:

                # if (a!=b) or (a!=c) or (a!=d) or (a!=e) or (a!=f):
                    # yhum = yhum[(a-2):]
                    # ytempCon = ytempCon[(a-2):]
                    # ycoTwo = ycoTwo[(a-2):]
                    # ypmA = ypmA[(a-2):]
                    # ypmB = ypmB[(a-2):]
                    # ypmC = ypmC[(a-2):]

                # Check the shapes of the data are coherent once more:
                # print("Length of yhum = ",len(yhum))
                # print("Length of ytempCon = ",len(ytempCon))
                # print("Length of ycoTwo = ",len(ycoTwo))
                # print("Length of ypmA = ",len(ypmA))
                # print("Length of ypmB = ",len(ypmB))
                # print("Length of ypmC = ",len(ypmC))

                # errorCount = errorCount +1
                # print("Error count = ",errorCount)
                print("Now make the plot ..... ")


                # Draw x and y lists
                ax.clear()
                ax.plot(xs, yhum, label="Humidity")
                ax.plot(xs, ytempCon, label="Temperature")
                ax.plot(xs, ycoTwo, label="CO2/10")
                ax.plot(xs, ypmA, label="pmA")
                ax.plot(xs, ypmB, label="pmB")
                ax.plot(xs, ypmC, label="pmC")

                print(".... 1 ....")

                # Format plot
                plt.xticks(rotation=45, ha='right')
                plt.subplots_adjust(bottom=0.30)
                plt.title('Container Environmentals')
                plt.ylabel('Values')
                plt.xlabel('Time (minutes)')
                # plt.legend()
                plt.legend(loc = "upper left")
                # plt.axis([1, None, 0, 50]) # Use for arbitrary number of trials
                plt.axis() # Use for arbitrary number of trials
                # plt.axis([1, 100, 0, 1.1]) # Use for 100 trial demo
                print(".... 2 ....")

        '''
        ===============   =============
        Location String   Location Code
        ===============   =============
        'best'            0
        'upper right'     1
        'upper left'      2
        'lower left'      3
        'lower right'     4
        'right'           5
        'center left'     6
        'center right'    7
        'lower center'    8
        'upper center'    9
        'center'          10
        ===============   =============
        '''


        print("")
  
        print("char_data:",char_data)

        # Limit x and y lists to 2880 items (48 hours)
        xs = xs[-2880:]
        yhum = yhum[-2880:]
        ytempCon = ytempCon[-2880:]
        ycoTwo = ycoTwo[-2880:]
        ypmA = ypmA[-2880:]
        ypmB = ypmB[-2880:]
        ypmC = ypmC[-2880:]

        # Make a call back:
        print(".... 1 ....")
        ser.write(b'D\n')
        delta_time[0] = round(time.time() - start_time, 5)
        # print("delta_time[0]: ",delta_time[0])
        if delta_time[0] < 1.0:
            delta_time[1] = delta_time[0] + delta_time[1]
            # print("--- %s seconds ---" % round(time.time() - start_time, 5), " Counter[0]:  ",counter[0])
            print("Average process time = ",round(delta_time[1]/counter[0],5), " Counter[0]:  ",counter[0])
            counter[0] = counter[0] + 1
            # print("Counter[0]:  ",counter[0])

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, yhum, ytempCon, ycoTwo, ypmA, ypmB, ypmC, data_y_hum, data_y_tempCon, data_y_coTwo, data_y_pmA, data_y_pmB, data_y_pmC, data_y_tempGlass, data_y_moisGlass, threeDArray, counter, counter2, delta_time, errorCount), interval=50)
plt.show()



