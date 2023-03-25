#include "SerialTransfer.h"

SerialTransfer testStand;
SerialTransfer computer;

const int numOfLedPins = 22;
String ledPinNames[numOfLedPins] = {"armed", "active", "abort", "invld", "error", "warn", "pckt", "waiting", "mismatch", "caution", "CV1LED", "XV1LED", "XV2LED", "XV3LED", "XV4LED", "XV5LED", "XV6LED", "XV7LED", "XV8LED", "XV9LED", "XV10LED", "XV11LED"};
int ledPinValues[numOfLedPins] = {A1, A0, A3, A2, A5, A4, A7, A6, A11, 22, 24, 26, 28, 30, 32, 36, 38, 40, 42, 44, 46, 48};

const int numOfSwitchPins = 16;
String switchPinNames[numOfSwitchPins] = {"CV1SW", "XV1SW", "XV2SW", "XV3SW", "XV4SW", "XV5SW", "XV6SW", "XV7SW", "XV8SW", "XV9SW", "XV10SW", "XV11SW", "abrtBT", "autoSW", "fireBT", "keySwh"};
int switchPinValues[numOfSwitchPins] = {45, 43, 41, 39, 37, 35, 33, 31, 29, 27, 25, 23, A13, 47, A14, A15};

int buzBut = 0;        //input
int buzPin = 10;       //output

bool buzzer = false;

struct STRUCT1 {
  uint16_t L1; //Loadcell
  uint16_t P1; //Don't know
  uint16_t P2; //Tank Pressure Bottom
  uint16_t P3; //Tank Pressure Top
  uint16_t P4; //Don't know
  uint16_t T1; //Tank Temperature
  uint32_t status = 0; //Status int
} data; //16 bytes

uint32_t control_int;
uint32_t previous_control_int = 0;

uint32_t currentMicros;
uint32_t currentMillis;
uint32_t previousMillis = 0;
const uint16_t interval = 100;
const uint16_t commandInterval = 750;
uint32_t previousCommand = 0;

uint32_t intervalData = 0;
float dataRate = 0;
int32_t delta = 0;


void setup() {
  pinMode(8,INPUT_PULLUP);
  //Serial setup
  Serial.begin(115200);
  Serial1.begin(115200);
  computer.begin(Serial);
  testStand.begin(Serial1);
  pinMode(45,INPUT_PULLUP);
  //Pin mode setup
  for (int i = 0; i < numOfSwitchPins; i++) {
    pinMode(switchPinValues[i], INPUT_PULLUP);
  }

  for (int i = 0; i < numOfLedPins; i ++) {
    pinMode(ledPinValues[i], OUTPUT);
  }

  pinMode(buzBut, INPUT_PULLUP);
  pinMode(buzPin, OUTPUT);
 
}

void loop() {
  control_int = bit(16) | bit(18);
  //Buffer Variables
  uint16_t txSize_t = 0;
  uint16_t rxSize_t = 0;
  uint16_t txSize_c = 0;
  uint16_t rxSize_c = 0;

  //Read Switches
  for (int i = 0; i < numOfSwitchPins; i++) {
    if (digitalRead(switchPinValues[i]) == LOW) {
          control_int = control_int | bit(i);
        }
  }

  //If controls changed update Teststand
  if (control_int != previous_control_int) {
    //Fill TestStand Transmit Buffer
    txSize_t = testStand.txObj(control_int, txSize_t);
    //Send to Teststand
    testStand.sendData(txSize_t);
    previousCommand = millis();
    previous_control_int = control_int;
  }

  //Recieve from teststand
  if (testStand.available()) {
    //Fill Recive Buffer
    rxSize_t = testStand.rxObj(data, rxSize_t);
    intervalData += rxSize_t;
    
  }
  
  //Write to LEDs
  for (int i = 0; i < numOfLedPins; i++) {
    if(data.status & bit(i)) {
      digitalWrite(ledPinValues[i], HIGH);
      if (i == 2) {
        buzzer = true;
      }
    }
  }

  //Buzzer
  if (digitalRead(buzPin) == LOW) {
    buzzer = false;
    digitalWrite(13,LOW);
  } else if (buzzer){
    digitalWrite(13,HIGH);
  }

  //Test Stand Keep Alive
  if (currentMillis - previousCommand >= commandInterval) {
    //Fill TestStand Transmit Buffer
    txSize_t = testStand.txObj(control_int, txSize_t);
    //Send to Teststand
    testStand.sendData(txSize_t);
    previousCommand = millis();
  }

  //Sensor Data Relay
  //currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
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
  Serial.println(data.T1/10);
}

void printInputs() {
  for (int i = 0; i < numOfSwitchPins; i++) {
    if (control_int & bit(i)) {
      
      Serial.print(switchPinNames[i]);
      Serial.print(",");
    }
  }
  Serial.println("");
}
