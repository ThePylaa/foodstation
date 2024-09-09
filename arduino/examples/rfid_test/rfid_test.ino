#include <Arduino.h>
#define RFIDRESET 28

void setup() {
  Serial.begin(9600);
  Serial2.begin(9600);
  Serial.println("RFID");
  pinMode(RFIDRESET, OUTPUT);
  resetRFID();
}

void loop() {
  char rfid[14] = "";
  getRfid(rfid);
  String hs;

  for (int i = 0; i < 14; i++) {
    hs += rfid[i];
  }
  Serial.print(hs);
  Serial.println();

  
  delay(500);
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
  if (index != 0) {

    for (int i = 1; i <= 10; i++) {
      asciiRfidCardNum[i - 1] = decToASCII(inputBuffer[i]);
    }
    for (int i = 11; i <= 14; i++) {
      asciiRfidCountry[i - 11] = decToASCII(inputBuffer[i]);
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

char decToASCII(int dezimal) {
  return static_cast<char>(dezimal);
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

void resetRFID() {
  digitalWrite(RFIDRESET, LOW);
  delayMicroseconds(1000); // 1ms Low-Puls
  digitalWrite(RFIDRESET, HIGH);
}
