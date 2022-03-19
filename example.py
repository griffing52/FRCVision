from cscore import CameraServer, MjpegServer
from networktables import NetworkTablesInstance
import cv2
import numpy as np
import json

# video resolution input resolution
width = 680 
height = 480

# compressed video resolution
cWidth = 160 
cHeight = 120

# name of camera
name = "hub-camera"

# lower color threshold in format HSV (Hue, Saturation, Value)--NOT RGB
lower_threshold = np.array([56, 100, 65])
# upper color threshold in format HSV (Hue, Saturation, Value)--NOT RGB
upper_threshold = np.array([74, 255, 255])

# camera settings (found by clicking )
config = {     "fps": 30,     "height": 480,     "pixel format": "mjpeg",     "properties": [         {             "name": "connect_verbose",             "value": 1         },         {             "name": "exposure_auto",             "value": 1         },         {             "name": "exposure_absolute",             "value": 7         },         {             "name": "white_balance_temperature_auto",             "value": False         },         {             "name": "white_balance_temperature",             "value": 2800         },         {             "name": "raw_brightness",             "value": 30         },         {             "name": "brightness",             "value": 0         },         {             "name": "raw_contrast",             "value": 3         },         {             "name": "contrast",             "value": 30         },         {             "name": "raw_saturation",             "value": 100         },         {             "name": "saturation",             "value": 50         },         {             "name": "power_line_frequency",             "value": 2         },         {             "name": "raw_sharpness",             "value": 25         },         {             "name": "sharpness",             "value": 50         },         {             "name": "backlight_compensation",             "value": 0         },         {             "name": "raw_exposure_absolute",             "value": 5         },         {             "name": "pan_absolute",             "value": 0         },         {             "name": "tilt_absolute",             "value": 0         },         {             "name": "zoom_absolute",             "value": 0         }     ],     "width": 680 }
# commented code below gets settings of camera from a file named "camerasettings.json"
# try:
#     with open("camerasettings.json", "rt", encoding="utf-8") as f:
#         j = json.load(f)
# except OSError as err:
#     print("could not open '{}': {}".format(configFile, err), file=sys.stderr)

# initialize network tables
NetworkTablesInstance.getDefault().initialize(server='10.2.94.2')
# get network table of the name of the camera
sd = NetworkTablesInstance.getDefault().getTable(name)

# initialize camera server
cs = CameraServer.getInstance()
cs.enableLogging()

# creates camera instance
camera = cs.startAutomaticCapture()
# sets camera config settings
camera.setConfigJson(json.dumps(config))
# may be helpful?
# camera.setWhiteBalanceManual(2800)
# camera.setExposureManual(7)
#sets camera resolution
camera.setResolution(width, height)

# initialize input and output instances
sink = cs.getVideo()
output = cs.putVideo(name, width, height)
# creates video server on port 8083, which can be accessed by going to "wpilibpi.local:8083" in a browser or by putting its ip address pollowed by ":8083"
mjpeg = MjpegServer("cvhttpserver", "", 8083)
mjpeg.setSource(output)

input_img = np.array([[]])

# vision loop
while True:
    # sets variable input_img to the new frame
    time, input_img = sink.grabFrame(input_img)

    if time == 0: # There is an error
        output.notifyError(sink.getError())
        continue

    # convert BGR image to HSV (Hue, Saturation, Value respectively)
    hsv = cv2.cvtColor(input_img, cv2.COLOR_BGR2HSV)
    
    # gets grayscale image of all pixels within the color threshold
    threshold = cv2.inRange(hsv, lower_threshold, upper_threshold)

    # erodes--remove bordering pixels--and then dilates pixel space by a 3 x 3 kernel of 1s 
    # this helps elminate some noise, more information found here:
    # https://docs.opencv.org/3.4/db/df6/tutorial_erosion_dilatation.html
    kernel = np.ones((3, 3), np.uint8)
    threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)

    # gets contours in the masked grayscale image
    _, contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # init largestContour
    largestContour = np.array([[]])
    
    # initializes final values
    ct = 0 # number of contours found  
    cx = 0 # x-position of largest contour
    cy = 0 # y-position of largest contour
    ca = 0 # area of largest contour

    # if there are any contours found
    if len(contours) > 0:
        largestContour = max(contours, cv2.contourArea)
        
        M = cv2.moments(c)
        if M["m00"] != 0:
            centerX = int(M["m10"] / M["m00"])
            centerY = int(M["m01"] / M["m00"])

        ct = len(contours) # gets the amount of contours found
        cx = centerX # gets contour's x-coord
        cy = centerY # gets contour's y-coord
        ca = cv2.contourArea(largestContour) # gets contour area
        
    # compress image to use less network bandwidth
    output_img = cv2.resize(input_img, (cWidth, cHeight))

    # posts all values to network tables
    sd.putNumber("ct", ct)
    sd.putNumber("cx", cx)
    sd.putNumber("cy", cy)
    sd.putNumber("ca", ca)

    # posts final image to stream
    output.putFrame(output_img)