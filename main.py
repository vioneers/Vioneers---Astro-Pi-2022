from pathlib import Path
from logzero import logger, logfile
from sense_hat import SenseHat
from picamera import PiCamera
from orbit import ISS
from time import sleep
from datetime import datetime, timedelta
import csv
import cv2 as cv

def createFile(outputFile):
    with open(outputFile, 'w') as file:
        writer = csv.writer(file)
        header = ("Counter", "Date/time", "Latitude", "Longitude", "Temperature", "Humidity")
        writer.writerow(header)

TIME_MAX = 178 #minutes - maximum run time, in order not to exceed the 3-hour time limit

imgCnt = 0

# main program

baseFolder = Path(__file__).parent.resolve()

# choosing a log file name
logfile(baseFolder/"vioneers.log")

# establishing Sense Hat
sense = SenseHat()

# configuring the CSV file
dataFile = baseFolder/"vioneers.csv"
createFile(dataFile)

# fixating the start and current time
start_time = datetime.now()
now_time = datetime.now()

def writeData(outputFile, data):
    with open(outputFile, 'a') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def converter(angle):
    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    return sign < 0, exif_angle

def takePicture(camera, image):
    location = ISS.coordinates()
    south, exif_latitude = converter(location.latitude)
    west, exif_longitude = converter(location.longitude)
    camera.exif_tags['GPS.GPSLatitude'] = exif_latitude
    camera.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
    camera.exif_tags['GPS.GPSLongitude'] = exif_longitude
    camera.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"
    camera.capture(image)
  
def capture():
    imageFile = f"{baseFolder}/photo{imgCnt:03d}.jpg"
    takePicture(cam, imageFile)

threshold = 60
width = 4056
height = 3040

cam = PiCamera()
cam.resolution = (width, height)

#Running a loop for approximately 3 hours
while now_time < start_time + timedelta(minutes = TIME_MAX):
    try:
        humidity = round(sense.humidity, 4)
        temperature = round(sense.temperature, 4)

        #Getting the coordinates of the location of the ISS
        location = ISS.coordinates()

        #Adding the data to the csv file:
        imgCnt =  imgCnt+1
        row = ( imgCnt,
                datetime.now(),
                location.latitude.degrees, location.longitude.degrees,
                temperature, humidity )
        writeData(dataFile, row)

        # Taking an image
        capture()

        #Log event
        logger.info(f"iteration {imgCnt}")

        sleep(30)

        #Updating the current time
        now_time = datetime.now()

    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}')