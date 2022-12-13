#!/usr/bin/env python
# cd /home/paddy/Documents/Mushrooms/Code && python3 data_rx_control_room_09.py

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
# import ftputil
import urllib.request

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
error_utf8_decode = False
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

ytempGlass = []
ymoisGlass = []

# ytempGlass, ymoisGlass,

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
def animate(i, xs, yhum, ytempCon, ycoTwo, ypmA, ypmB, ypmC, ytempGlass, ymoisGlass, data_y_hum, data_y_tempCon, data_y_coTwo, data_y_pmA, data_y_pmB, data_y_pmC, data_y_tempGlass, data_y_moisGlass, threeDArray, counter, counter2, delta_time, errorCount,error_utf8_decode):
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
    try:
        char_data = char_data.decode("utf-8")
    except NameError:
        print("ATTENTION: A utf-8 decode problem was encountered.")
        error_utf8_decode = True

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
        # print("Glasshouse header was detected !!!")
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

        # print("threeDArray 3: ")
        # print(threeDArray)
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
        g = 0
        h = 0

        for i in range(4):
            if str(threeDArray[0][1][i]) == ":":
                break
            myStringLabel = myStringLabel + str(threeDArray[0][1][i])

        for i in range(6):
            myStringValue = "" + myStringValue + str(threeDArray[1][1][i])

        # print("myStringLabel:",myStringLabel)
        # print("myStringValue:",myStringValue)

        if headerGlassTest == True:
            # print("Glasshouse header was detected !!!")
            if (myStringLabel == "mois"):
                data_y_moisGlass[0] = float(myStringValue)
                data_y_moisGlass[0] = data_y_moisGlass[0]/100
                # print("mois detected !!")
            if (myStringLabel == "temp"):
                data_y_tempGlass[0] = float(myStringValue)
                # print("temp detected !!")

        if headerContainerTest == True:
            if (myStringLabel == "hum"):
                data_y_hum[0] = float(myStringValue)
                # print("hum detected !!")
            if (myStringLabel == "temp"):
                data_y_tempCon[0] = float(myStringValue)
                # print("temp detected !!")
            if (myStringLabel == "coTw"):
                data_y_coTwo[0] = float(myStringValue)
                # print("coTwo detected !!")
            if (myStringLabel == "pmA"):
                data_y_pmA[0] = float(myStringValue)
                # print("pmA detected !!")
                # print("data_y_pmA = ",data_y_pmA)
            if (myStringLabel == "pmB"):
                data_y_pmB[0] = float(myStringValue)
                # print("pmB detected !!")
            if (myStringLabel == "pmC"):
                data_y_pmC[0] = float(myStringValue)
                # print("pmC detected !!")

            # temp is the last chunk of data to be received:
            if error_utf8_decode == True:
                print("error_utf8_decode detected !!")
                error_utf8_decode == False
            else:
                if myStringLabel == "temp":
                    print("")
                    yhum.append(data_y_hum[0])
                    ytempCon.append(data_y_tempCon[0])
                    ycoTwo.append(data_y_coTwo[0])
                    ypmA.append(data_y_pmA[0])
                    ypmB.append(data_y_pmB[0])
                    ypmC.append(data_y_pmC[0])

                    ytempGlass.append(data_y_tempGlass[0])
                    ymoisGlass.append(data_y_moisGlass[0])

                    # session = ftplib.FTP('185.65.237.84','paddygoat2@goatindustries.co.uk','Whales1966!')
                    # dir = 'bat_detector/results'
                    # session.mkd(dir)

                    sendPath2 = 'http://###########################.php?temp='+str(data_y_tempCon[0])+'&hum='+str(data_y_hum[0])+'&cotwo='+str(data_y_coTwo[0])+'&pma='+str(data_y_pmA[0])+'&pmb='+str(data_y_pmB[0])+'&pmc='+str(data_y_pmC[0])
                    webUrl2 = urllib.request.urlopen(sendPath2)
                    print("Result code: " + str(webUrl2.getcode()))

                    a = len(yhum)
                    b = len(ytempCon)
                    c = len(ycoTwo)
                    d = len(ypmA)
                    e = len(ypmB)
                    f = len(ypmC)
                    g = len(ytempGlass)
                    h = len(ymoisGlass)

                    # Check the shapes of the data are coherent:
                    xs = range(len(yhum))
                    # print("Length of xs = ",xs)
                    # print("Length of yhum = ",a)
                    # print("Length of ytempCon = ",b)
                    # print("Length of ycoTwo = ",c)
                    # print("Length of ypmA = ",d)
                    # print("Length of ypmB = ",e)
                    # print("Length of ypmC = ",f)
                    # print("Length of ytempGlass = ",g)
                    # print("Length of ymoisGlass = ",h)
                    # print("ytempGlass = ",ytempGlass)
                    # print("ymoisGlass = ",ymoisGlass)
                    # print("")
                    print("Humidity = ",data_y_hum[0])
                    print("Temperature container = ",data_y_tempCon[0])
                    print("CO2/10 = ",data_y_coTwo[0])
                    print("pmA = ",data_y_pmA[0])
                    print("pmB = ",data_y_pmB[0])
                    print("pmC = ",data_y_pmC[0])
                    print("Glasshouse temp = ",data_y_tempGlass[0])
                    print("Glasshouse soil mois = ",data_y_moisGlass[0])

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
                    # print("Now make the plot ..... ")


                    # Draw x and y lists
                    ax.clear()
                    ax.plot(xs, yhum, label="Container humidity")
                    ax.plot(xs, ytempCon, label="Container temp")
                    ax.plot(xs, ycoTwo, label="Container CO2/10")
                    ax.plot(xs, ypmA, label="Container pmA")
                    ax.plot(xs, ypmB, label="Container pmB")
                    ax.plot(xs, ypmC, label="Container pmC")
                    ax.plot(xs, ytempGlass, label="Glasshouse temp")
                    ax.plot(xs, ymoisGlass, label="Glasshouse soil moisture")

                    # print(".... 1 ....")

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
                    # print(".... 2 ....")

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


        # print("")
  
        # print("char_data:",char_data)

        # Limit x and y lists to 2880 items (? hours)
        if len(xs) > 2880:
            xs = xs[1:]    # gets rid of the 1st item
            yhum = yhum[1:]
            ytempCon = ytempCon[1:]
            ycoTwo = ycoTwo[1:]
            ypmA = ypmA[1:]
            ypmB = ypmB[1:]
            ypmC = ypmC[1:]
            ytempGlass = ytempGlass[1:]
            ymoisGlass = ymoisGlass[1:]


        # Make a call back:
        # print(".... 1 ....")
        ser.write(b'D\n')
        delta_time[0] = round(time.time() - start_time, 5)
        # print("delta_time[0]: ",delta_time[0])
        if delta_time[0] < 1.0:
            delta_time[1] = delta_time[0] + delta_time[1]
            # print("--- %s seconds ---" % round(time.time() - start_time, 5), " Counter[0]:  ",counter[0])
            print("Average process time = ",round(delta_time[1]/counter[0],5), " Counter[0]:  ",counter[0])
            counter[0] = counter[0] + 1
            # print("Counter[0]:  ",counter[0])
            print("")

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, yhum, ytempCon, ycoTwo, ypmA, ypmB, ypmC, ytempGlass, ymoisGlass, data_y_hum, data_y_tempCon, data_y_coTwo, data_y_pmA, data_y_pmB, data_y_pmC, data_y_tempGlass, data_y_moisGlass, threeDArray, counter, counter2, delta_time, errorCount,error_utf8_decode), interval=50)
plt.show()


'''
Hopefully fixed this one:
Traceback (most recent call last):
  File "/home/paddy/.local/lib/python3.6/site-packages/matplotlib/backend_bases.py", line 1194, in _on_timer
    ret = func(*args, **kwargs)
  File "/home/paddy/.local/lib/python3.6/site-packages/matplotlib/animation.py", line 1442, in _step
    still_going = Animation._step(self, *args)
  File "/home/paddy/.local/lib/python3.6/site-packages/matplotlib/animation.py", line 1173, in _step
    self._draw_next_frame(framedata, self._blit)
  File "/home/paddy/.local/lib/python3.6/site-packages/matplotlib/animation.py", line 1192, in _draw_next_frame
    self._draw_frame(framedata)
  File "/home/paddy/.local/lib/python3.6/site-packages/matplotlib/animation.py", line 1742, in _draw_frame
    self._drawn_artists = self._func(framedata, *self._args)
  File "data_rx_control_room_08.py", line 104, in animate
    char_data = char_data.decode("utf-8")
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92 in position 14: invalid start byte
'''





'''
Traceback (most recent call last):
  File "/usr/lib/python3.6/urllib/request.py", line 1325, in do_open
    encode_chunked=req.has_header('Transfer-encoding'))
  File "/usr/lib/python3.6/http/client.py", line 1285, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/usr/lib/python3.6/http/client.py", line 1331, in _send_request
    self.endheaders(body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.6/http/client.py", line 1280, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.6/http/client.py", line 1046, in _send_output
    self.send(msg)
  File "/usr/lib/python3.6/http/client.py", line 984, in send
    self.connect()
  File "/usr/lib/python3.6/http/client.py", line 956, in connect
    (self.host,self.port), self.timeout, self.source_address)
  File "/usr/lib/python3.6/socket.py", line 704, in create_connection
    for res in getaddrinfo(host, port, 0, SOCK_STREAM):
  File "/usr/lib/python3.6/socket.py", line 745, in getaddrinfo
    for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
socket.gaierror: [Errno -2] Name or service not known

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/paddy/.local/lib/python3.6/site-packages/matplotlib/backend_bases.py", line 1194, in _on_timer
    ret = func(*args, **kwargs)
  File "/home/paddy/.local/lib/python3.6/site-packages/matplotlib/animation.py", line 1442, in _step
    still_going = Animation._step(self, *args)
  File "/home/paddy/.local/lib/python3.6/site-packages/matplotlib/animation.py", line 1173, in _step
    self._draw_next_frame(framedata, self._blit)
  File "/home/paddy/.local/lib/python3.6/site-packages/matplotlib/animation.py", line 1192, in _draw_next_frame
    self._draw_frame(framedata)
  File "/home/paddy/.local/lib/python3.6/site-packages/matplotlib/animation.py", line 1742, in _draw_frame
    self._drawn_artists = self._func(framedata, *self._args)
  File "data_rx_control_room_09.py", line 289, in animate
    webUrl2 = urllib.request.urlopen(sendPath2)
  File "/usr/lib/python3.6/urllib/request.py", line 223, in urlopen
    return opener.open(url, data, timeout)
  File "/usr/lib/python3.6/urllib/request.py", line 526, in open
    response = self._open(req, data)
  File "/usr/lib/python3.6/urllib/request.py", line 544, in _open
    '_open', req)
  File "/usr/lib/python3.6/urllib/request.py", line 504, in _call_chain
    result = func(*args)
  File "/usr/lib/python3.6/urllib/request.py", line 1353, in http_open
    return self.do_open(http.client.HTTPConnection, req)
  File "/usr/lib/python3.6/urllib/request.py", line 1327, in do_open
    raise URLError(err)
urllib.error.URLError: <urlopen error [Errno -2] Name or service not known>
'''

