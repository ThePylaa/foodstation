// Necessary libraries for sensors and components
#include "HX711.h"
#include "DHT.h"
#include <Rfid134.h>
#include <ArduinoJson.h>
#include <SharpDistSensor.h>

// HX711 (Weight sensor) setup
#define DOUT  36
#define CLK  34
HX711 scale;
float calibration_factor = -2150;

// DHT11 (Temperature & Humidity sensor) setup
#define DHTPIN 30
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Stepper motor setup
#define MOTOR_IN1 22
#define MOTOR_IN2 23
#define MAGNETSWITCHPIN 47

// Light barrier sensor setup
#define LIGHTBARRIERPIN A0
#define MEDIANFILTERWINDOWSIZE 5
SharpDistSensor sensor(LIGHTBARRIERPIN, MEDIANFILTERWINDOWSIZE);

// RFID setup
#define RFIDRESET 28

// Global variables
String inputBuffer;
JsonDocument payload;
String rfidString;

void setup() {
  // Motor and sensor pin configuration
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MAGNETSWITCHPIN, INPUT);

  // Serial communication setup
  Serial.begin(9600);
  Serial2.begin(9600); // For RFID sensor

  // Scale setup
  scale.begin(DOUT, CLK);
  scale.tare();
  scale.set_scale(calibration_factor);

  // DHT11 sensor initialization
  dht.begin();

  // Set light barrier sensor model
  sensor.setModel(SharpDistSensor::GP2Y0A41SK0F_5V_DS);

  // Initialize RFID scanner
  pinMode(RFIDRESET, OUTPUT);
  resetRFID();
}

void loop() {
  // Check for commands from Raspberry Pi
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    
    // For double-digit dispense commands
    if (isDigit(inChar)) {
      inputBuffer += inChar;
      inputBuffer += (char)Serial.read();
      serialFlush();
    } else {
      inputBuffer += inChar;
    }

    // Process "dispense" command
    if (inputBuffer != "" && inputBuffer.startsWith("dispense ")) {
      String numStr = inputBuffer.substring(9); 
      int amount = numStr.toInt();
      
      // Dispense food portions
      for (int i = 0; i < amount; i++) {
        dispenseFood();
        delay(260);
      }
    }
  }

  // Handle RFID reading and sensor data
  char rfidRaw[14] = "----NORFID----";
  getRfid(rfidRaw);
  rfidString = "----NORFID----";
  for (int i = 0; i < 14; i++) {
    if ((rfidRaw[i] != NULL) && (rfidRaw[i] != '\0')) {
      rfidString[i] = rfidRaw[i];
    } else {
      rfidString = "----NORFID----"; 
      break;
    }
  }
  
  // Prepare and send JSON payload
  payload["rfid"] = rfidString;
  payload["weight"] = getFoodbowlWeight();
  payload["humidity"] = getHumidity();
  payload["temp"] = getCelcius();
  payload["broken"] = isFoodHigh();
  serializeJson(payload, Serial);

  // Ensure Raspberry Pi recognizes end of the payload
  Serial.print("\n");

  inputBuffer = "";
  
  delay(990);
}

void dispenseFood() {
  int stuckCounter = 0;

  // Move motor to dispense food (go away from current magnet)
  while (digitalRead(MAGNETSWITCHPIN) == 0) {
    if (stuckCounter < 6) {
      // Attempt soft turns to move away from the magnet
      for (int i = 128; i < 134; i++) {
        analogWrite(MOTOR_IN1, i);
        delay(4);
      }
      digitalWrite(MOTOR_IN1, LOW);
      delay(1000);

      stuckCounter++;
    } else {
      // After 6 attempts: reverse direction
      for (int i = 128; i < 136; i++) {
        analogWrite(MOTOR_IN2, i);  // Use MOTOR_IN2 to reverse direction
        delay(4);
      }
      digitalWrite(MOTOR_IN2, LOW);
      delay(1000);

      // After reversing, try again in the original direction with more power
      for (int i = 128; i < 138; i++) {
        analogWrite(MOTOR_IN1, i);
        delay(4);
      }
      digitalWrite(MOTOR_IN1, LOW);
      delay(1000);

      stuckCounter = 0;  // Reset counter after reversing
    }
  }
  digitalWrite(MOTOR_IN1, LOW);

  delay(500);

  // Move motor to next magnet (stop motor after dispensing)
  stuckCounter = 0;
  while (digitalRead(MAGNETSWITCHPIN) == 1) {
    if (stuckCounter < 6) {
      // Soft turn to move to the next magnet
      for (int i = 128; i < 134; i++) {
        analogWrite(MOTOR_IN1, i);
        delay(4);
      }
      digitalWrite(MOTOR_IN1, LOW);
      delay(1000);

      stuckCounter++;
    } else {
      // After 6 attempts: reverse direction
      for (int i = 128; i < 136; i++) {
        analogWrite(MOTOR_IN2, i);  // Reverse direction with MOTOR_IN2
        delay(4);
      }
      digitalWrite(MOTOR_IN2, LOW);
      delay(1000);

      // After reversing, try again in the original direction
      for (int i = 128; i < 138; i++) {
        analogWrite(MOTOR_IN1, i);
        delay(4);
      }
      digitalWrite(MOTOR_IN1, LOW);
      delay(1000);

      stuckCounter = 0;  // Reset counter after reversing
    }
  }
  digitalWrite(MOTOR_IN1, LOW);
  digitalWrite(MOTOR_IN2, LOW);
}

// Get the weight of the food bowl in grams
int getFoodbowlWeight() {
  return scale.get_units();
}

// Get humidity from DHT11 sensor
float getHumidity() {
  return dht.readHumidity();
}

// Get temperature in °C from DHT11 sensor
float getCelcius() {
  return dht.readTemperature();
}

// Check if light barrier is triggered (food level low)
bool isFoodHigh() {
  unsigned int distance = sensor.getDist();
  return (distance <= 200);
}

// Reset RFID scanner
void resetRFID() {
  digitalWrite(RFIDRESET, LOW);
  delayMicroseconds(1000); // 1ms low pulse
  digitalWrite(RFIDRESET, HIGH);
}

// Read RFID data
void getRfid(char* getString) {
  char asciiRfidCardNum[10];
  char asciiRfidCountry[4];
  int newInt;
  int index = 0;
  int inputBuffer[30];

  // Read from RFID sensor
  while (Serial2.available()) {
    newInt = Serial2.read();
    inputBuffer[index] = newInt;
    index++;
  }

  // Process RFID data if available
  if (index != 0) {

    for (int i = 1; i <= 10; i++) {
      asciiRfidCardNum[i - 1] = decToASCII(inputBuffer[i]);
    }
    for (int i = 11; i <= 14; i++) {
      asciiRfidCountry[i - 11] = decToASCII(inputBuffer[i]);
    }

    // Reverse arrays
    reverseArray(asciiRfidCardNum, 10);
    reverseArray(asciiRfidCountry, 4);

    // Combine RFID data
    for (int i = 0; i < 14; i++) {
      if (i < 10){
        getString[i] = asciiRfidCardNum[i];
      } else {
        getString[i] = asciiRfidCountry[i - 10];
      }
    }
  }
  resetRFID();
}

// Convert decimal to ASCII
char decToASCII(int decimal) {
  return static_cast<char>(decimal);
}

// Reverse array
void reverseArray(char arr[], int length) {
  int temp;
  int start = 0;
  int end = length - 1;

  while (start < end) {
    temp = arr[start];
    arr[start] = arr[end];
    arr[end] = temp;
    start++;
    end--;
  }
}

// Clear the serial input buffer
void serialFlush() {
  while (Serial.available() > 0) {
    char t = Serial.read();
  }
}
