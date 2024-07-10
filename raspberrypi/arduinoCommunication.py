import serial
import time
import random
import json

# Open serial connection to arduino
ser = serial.Serial('/dev/ttyACM0', 9600)
# Wait for connection to be established
time.sleep(1)


def dispensePortion(amount):
    # Dispense amount portions of food
    clearBuffer()
    ser.write(f"dispense {amount}".encode("utf-8"))
    clearBuffer()

def getFoodbowlWeight():
    payload = recievePayload()
    return payload["weight"]
    
def isBarrierBroke():
    payload = recievePayload()
    return payload["broken"]
    
def getHumidity():
    payload = recievePayload()
    return payload["humidity"]
   
def getTemperature():
    payload = recievePayload()
    return payload["temp"]

def getRFID():
    payload = recievePayload()
    if payload["rfid"] == "----NORFID----":
        return None
    return payload["rfid"]
    
def recievePayload():
    # Why try catch? Arduino sometimes sends corruptet data
    # If the data is corruptet, the utf-8 decoder will throw an exception
    # The dummy payload is returned and thats tolerable
    try:
        clearBuffer()

        msg = ser.readline().decode("utf-8").strip()
        while(not msg.startswith("{") or not msg.endswith("}")):
            time.sleep(random.randint(0, 4) / 10)
            msg = ser.readline().decode("utf-8").strip()

        #RFID has to be converted to decimal
        jsonPayload = json.loads(msg)
        
        #checks if rfid is present
        if jsonPayload["rfid"] == "----NORFID----":
            return jsonPayload
        
        #splits raw["rfid"] into a list of strings and converts them from hex to decimal
        #first 10 characters are the RFID id
        #last 4 characters are the country code
        rfidID = int(jsonPayload["rfid"][:10], 16)
        rfidCountryCode = int(jsonPayload["rfid"][10:], 16)

        jsonPayload["rfid"] = str(rfidCountryCode)+str(rfidID)

        return jsonPayload
    except Exception as e:
        return {'rfid': '----NORFID----', 'weight': 0, 'humidity': 0, 'temp': 0, 'broken': False}
    
def clearBuffer():
    # Clear the serial buffer
    ser.reset_input_buffer()
    ser.reset_output_buffer()