# Import necessary libraries and modules
from arduinoCommunication import *
from rtc import *
import time 
import io
import requests
import json
from datetime import datetime
from picamera2 import Picamera2
import base64

# Load the environment variables from the configuration file
with open("/home/pi/Desktop/feedingstation/raspberrypi/config.json", "r") as file:
    config = json.loads(file.read())
api_host = config["API_HOST"]  # API base URL
station_uuid = config["DEVICE_UUID"]  # Unique identifier for the feeding station
user_id = config["USER_ID"]  # User ID for server requests

# Define global variables for tracking portions dispensed and other state
global dispensedPortions
global lastScheduleRefresh
global picam2

# Initialize and start the Picamera for capturing images
def startPicam():
    global picam2
    picam2 = Picamera2()  # Create a new camera instance
    picam2.configure(picam2.create_still_configuration())  # Set to capture still images
    picam2.start()  # Start the camera
    time.sleep(1)  # Give the camera a second to warm up

# Update the server with current humidity and food level status
def updateServer():
    try:
        hum = getHumidity()  # Retrieve humidity from the sensor
        broken = isBarrierBroke()  # Check if the food barrier is broken (container full)

        # Send humidity data to the server
        res = requests.put(f"{api_host}/feedingstation/update_humidity", json={"feedingstation_id": station_uuid, "humidity": hum})
        # Send food level data to the server
        res = requests.put(f"{api_host}/feedingstation/update_container_foodlevel", json={"feedingstation_id": station_uuid, "container_foodlevel": broken})
    
    except Exception as e:
        print(e)
        print("Failed to update server")  # Error handling if server update fails

# Capture an image and upload it to the server
def sendImage():
    data = io.BytesIO()  # Create an in-memory buffer for the image
    picam2.capture_file(data, format='jpeg')  # Capture an image in JPEG format

    # Convert image data to base64 encoding for transmission
    data = base64.b64encode(data.getvalue())

    try:
        # Send the captured image to the server
        res = requests.post(f"{api_host}/picture/upload_picture", json={
            "user_id":  user_id, 
            "feedingstation_id": station_uuid, 
            "picture": data, 
            "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        if res.status_code == 200:
            print("Picture uploaded to server")  # Log success
    except Exception as e:
        print(e)
        print("Failed to upload picture to server")  # Error handling for upload

# Retrieve the feeding schedule from the server and save it locally
def getSchedule():
    try:
        # Get the schedule from the server
        res = requests.get(f"{api_host}/portion/portions?feedingstation={station_uuid}")
        schedule = res.json()  # Parse the schedule as JSON
        print(schedule)
        
        # Write the schedule to a local file
        with open("/home/pi/Desktop/feedingstation/raspberrypi/schedule.json", "w") as file:
            file.write(json.dumps(schedule))
    except Exception as e:
        print(e)
        print("Failed to get schedule from server")  # Error handling for schedule retrieval

# Check if the device has an internet connection
def hasInternet():
    try:
        # Attempt to connect to Google to test internet availability
        requests.get("https://www.google.com")
        return True  # Return true if connection is successful
    except:
        return False  # Return false if connection fails
    
# Perform the main routine tasks such as server updates and dispensing food
def doRoutine(lastServerUpdate):
    print("Doing Main Routine")
    global lastScheduleRefresh
    global dispensedPortions

    # If more than 5 minutes (300 seconds) have passed since the last server update
    if getTimeInSeconds() - lastServerUpdate > 300:
        
        if hasInternet():  # Ensure the device has an internet connection
            print("Updating server and getting schedule")
            updateServer()  # Update the server with the current status
            getSchedule()  # Fetch the latest schedule from the server
            setRtcTime()  # Sync the RTC with the server time
        
        lastServerUpdate = getTimeInSeconds()  # Reset the last update time

    # If it's a new day, reset the list of dispensed portions
    if getRtcDateTime().day != lastScheduleRefresh:
        print("New day, resetting dispensed portions")
        dispensedPortions = []  # Clear the dispensed portions
        lastScheduleRefresh = getRtcDateTime().day  # Update the last refresh day

    # Check if an RFID tag is detected
    rfid = getRFID()

    # If an RFID tag is present, check it against the schedule
    if rfid:
        with open("/home/pi/Desktop/feedingstation/raspberrypi/schedule.json", "r") as file:
            schedule = json.loads(file.read())  # Load the schedule from the file
            for animal in schedule:
                if animal["animal_rfid"] == rfid:  # Check if the detected RFID matches
                    print("RFID found in schedule")
                    
                    # If the food bowl's weight is greater than 5g, do not dispense more food
                    if getFoodbowlWeight() > 5:
                        print("Foodbowl is not empty")
                        # TODO: Maybe send a notification to the user here
                        break

                    # Dispense food if the portion time is valid and it hasn't already been dispensed
                    for portion in animal["portions"]:
                        if (getRtcDateTime().time() > datetime.strptime(portion["time"], "%H:%M:%S").time() and 
                                [[portion["time"]], [animal["animal_rfid"]]] not in dispensedPortions):
                            print(f"Dispensing %s portions of food" % portion["size"])                               
                            dispensePortion(portion["size"])  # Dispense the food portion
                            time.sleep(1)  # Pause to allow dispensing
                            sendImage()  # Capture and upload an image of the dispensing
                            
                            # Mark the portion as dispensed
                            dispensedPortions.append([[portion["time"]], [animal["animal_rfid"]]])
                        else:
                            print("False Time or already dispensed for " + portion["time"])  # Log invalid or duplicate dispensing
        
    return lastServerUpdate  # Return the updated last server update time

# Main program execution starts here
if __name__ == "__main__":
    # Initialize the camera
    startPicam()

    if hasInternet():
        setRtcTime()  # Sync the RTC if internet is available
        
    lastServerUpdate = getTimeInSeconds() - 300  # Set last server update time
    lastScheduleRefresh = 0  # Reset schedule refresh time

    # Main loop: run routine every 2 seconds
    while True:
        lastServerUpdate = doRoutine(lastServerUpdate)
        time.sleep(2)  # Wait for 2 seconds between iterations
