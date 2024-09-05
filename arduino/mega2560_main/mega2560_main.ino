#include "HX711.h"
#include "DHT.h"
#include <Rfid134.h>
#include <ArduinoJson.h>
#include <SharpDistSensor.h>


//for HX711
#define DOUT  36
#define CLK  34
HX711 scale;
float calibration_factor = 2180;
//---------

//for DHT11
#define DHTPIN 30
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
//----------

//for stepper motor
#define MOTOR_IN1 22
#define MAGNETSWITCHPIN 47
//----------------

//for lightbarrier
#define LIGHTBARRIERPIN A0
#define MEDIANFILTERWINDOWSIZE 5
SharpDistSensor sensor(LIGHTBARRIERPIN, MEDIANFILTERWINDOWSIZE);
//----------------

//for RFID
#define RFIDRESET 28
//----------------

//global variables
String inputBuffer;
JsonDocument payload;
String rfidString;
//-----------------

void setup() {
  //Motor Pin
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MAGNETSWITCHPIN, INPUT);

  //USB communivcation with raspi
  Serial.begin(9600);

  //Serial2 is used for the RFID sensor
  Serial2.begin(9600);

  //Setup for scale
  scale.begin(DOUT, CLK);
  scale.tare();
  scale.set_scale(calibration_factor);

  //Humidity / Celcius sensor
  dht.begin();

  // Set sensor model for light barrier
  sensor.setModel(SharpDistSensor::GP2Y0A41SK0F_5V_DS);

  //RFID scanner setup
  pinMode(RFIDRESET, OUTPUT);
  resetRFID();
}

void loop() {
  //checks for instructions from the raspi
  while(Serial.available() > 0){
    char inChar = (char)Serial.read();
    
    //for double digit dispenses
    if (isDigit(inChar)){
      inputBuffer += inChar;
      inputBuffer += (char)Serial.read();
      serialFlush();
    }else{
      inputBuffer += inChar;
    }

    //if instructions were send, process them
    if(inputBuffer != "" && inputBuffer.startsWith("dispense ")){
      
      String numStr = inputBuffer.substring(9); // extracts part after "dispense "
      int amount = numStr.toInt(); // convert extracted String to int
      
      for (int i = 0; i< amount; i++) {
        dispenseFood();
        delay(260);
      }
    }
  }

  char rfidRaw[14] = "----NORFID----";
  getRfid(rfidRaw);
  rfidString = "----NORFID----";
  for (int i = 0; i < 14; i++) {
    if((rfidRaw[i] != NULL) && (rfidRaw[i] != '\0')){
      rfidString[i] = rfidRaw[i];
    }else{
      rfidString = "----NORFID----"; 
      break;
    }
  }
  
  payload["rfid"]     = rfidString;
  payload["weight"]   = getFoodbowlWeight();
  payload["humidity"] = getHumidity();
  payload["temp"]     = getCelcius();
  payload["broken"]   = isFoodHigh();
  serializeJson(payload, Serial);
  //!!! It's impoortant that the Serial terminates the data with \n otherwise the
  //raspberry can't recognize the end of the payload -> code freezes
  Serial.print("\n");

  inputBuffer = "";
  
  delay(990); 
}

void dispenseFood(){
  // go away from current magnet
  while(digitalRead(MAGNETSWITCHPIN) == 0){
    for (int i=128; i<132; i++) {
      analogWrite(MOTOR_IN1, i);
      delay(4);
    }
    digitalWrite(MOTOR_IN1, LOW);
    delay(1500);
  }
  digitalWrite(MOTOR_IN1, LOW);

  delay(1000);
  
  //got to next magnet
  while(digitalRead(MAGNETSWITCHPIN) == 1){
    for (int i=128; i<132; i++) {
      analogWrite(MOTOR_IN1, i);
      delay(4);
    }
    digitalWrite(MOTOR_IN1, LOW);
    delay(1500);
  }
  digitalWrite(MOTOR_IN1, LOW);
  Serial.println("Duispensed portion");
}

//gets weight of the foodbowl in gramms 
int getFoodbowlWeight(){
  return scale.get_units();
}

//get humidity of DHT11
float getHumidity(){
  return dht.readHumidity();
}

//get degrees in °C from DHT11
float getCelcius(){
  return dht.readTemperature();
}

//checks if light barrier is broken
bool isFoodHigh(){
  unsigned int distance = sensor.getDist();
  if(distance > 200){
    return false;
  }

  return true;
}

void resetRFID() {
  digitalWrite(RFIDRESET, LOW);
  delayMicroseconds(1000); // 1ms Low-Puls
  digitalWrite(RFIDRESET, HIGH);
}

void getRfid(char* getString){
  char asciiRfidCardNum[10];
  char asciiRfidCountry[4];
  int newInt;
  int index = 0;
  int inputBuffer[30];

  //read input from rfid sensor module
  while (Serial2.available()) {
    newInt = Serial2.read();
    inputBuffer[index] = newInt;
    index = index + 1;
  }

  //when there was an input
  if (index > 1 && inputBuffer[0] == 0) {
    
    for (int i = 2; i <= 11; i++) {
      asciiRfidCardNum[i - 2] = decToASCII(inputBuffer[i]);
    }
    for (int i = 12; i <= 15; i++) {
      asciiRfidCountry[i - 12] = decToASCII(inputBuffer[i]);
    }

    //reverse arrays
    reverseArray(asciiRfidCardNum, 10);
    reverseArray(asciiRfidCountry, 4);

    for (int i = 0; i < 14; i++) {
      if (i<10){
        getString[i] = asciiRfidCardNum[i];
      }else{
        getString[i] = asciiRfidCountry[i-10];
      }

    }
  }
  resetRFID();
}

char decToASCII(int decimal) {
  return static_cast<char>(decimal);
}

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

void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}

