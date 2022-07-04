#include "SerialTransfer.h"


SerialTransfer testStand;
SerialTransfer computer;

struct STRUCT1 {
  uint16_t L1; //Loadcell
  uint16_t P1; //Don't know
  uint16_t P2; //Tank Pressure Bottom
  uint16_t P3; //Tank Pressure Top
  uint16_t P4; //Don't know
  uint16_t T1; //Tank Temperature
  uint16_t status = 0; //Status int
} data; //14 bytes

uint32_t control_int;

uint32_t currentMicros;
uint32_t currentMillis;
uint32_t previousMillis = 0;
const uint16_t interval = 100;
const uint16_t commandInterval = 500;
uint32_t previousCommand = 0;

uint32_t intervalData = 0;
float dataRate = 0;
int32_t delta = 0;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial1.begin(115200);

  pinMode(8, INPUT_PULLUP);
  computer.begin(Serial);
  testStand.begin(Serial1);
}

void loop() {
  //Buffer Variables
  uint16_t txSize_t = 0;
  uint16_t rxSize_t = 0;
  uint16_t txSize_c = 0;
  uint16_t rxSize_c = 0;
  
  //Recieve from teststand
  if (testStand.available()) {
    //Fill Recive Buffer
    rxSize_t = testStand.rxObj(data, rxSize_t);
    intervalData += rxSize_t;
    printdata();
  }
  //Recieve Control Input from Computer and Send to Teststand
  if (computer.available()) {
    //Fill Recive Buffer
    rxSize_c = computer.rxObj(control_int, rxSize_c);
    //Fill TestStand Transmit Buffer
    txSize_t = testStand.txObj(control_int, txSize_t);
    //Send to Teststand
    testStand.sendData(txSize_t);

  } else if (currentMillis - previousCommand >= commandInterval) { //Keep Alive signal (sort of)
    //Fill TestStand Transmit Buffer
    txSize_t = testStand.txObj(control_int, txSize_t);
    //Send to Teststand
    testStand.sendData(txSize_t);
    previousCommand = millis();
  }
  
  if (digitalRead(8) == HIGH) {
    //control.CV1 = false;
  }
  //else control.CV1 = true;

  currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;

    //Rx Datarate
    dataRate = intervalData/(float(interval)/1000);
    intervalData = 0;
    //Fill Computer Transmit Buffer
    txSize_c = computer.txObj(data, txSize_c);
    computer.sendData(txSize_c);
  
    

  }
}

void printdata() {
  //Serial.println(data.status);
  //Serial.print(",");
  //Serial.println(data.L1);
  //Serial.print(",");
  //Serial.print(dataRate);
  //Serial.print(",");
  //Serial.println();
  //currentMicros = micros();
  //delta = micros() - currentMicros;
  //Serial.println(delta);
}
