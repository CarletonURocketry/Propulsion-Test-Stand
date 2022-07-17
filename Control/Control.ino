#include "SerialTransfer.h"


SerialTransfer testStand;
SerialTransfer computer;

//Pin setup
//ASFAS LEDs
int armedLED = 2;          //output
int activeLED = 3;         //output
int abortLED = 4;          //output
int invalidLED = 5;        //output
int contTestLED = 6;       //output
//Error and Warning LEDs
int keySwitch = 9;         //input
int buzzerPin = 10;        //output
int errorLED = 11;         //output
int warnLED = 12;          //output
int packetLED = 13;        //output
int waitingLED = 14;       //output
int mismatchLED = 15;      //output
int cautionLED = 16;       //output
//Valve Control Pins
int CV1Switch = 22;        //input
int CV1LED = 23;           //output

int XV1Switch = 24;        //input
int XV1LED = 25;           //output

int XV2Switch = 26;        //input
int XV2LED = 27;           //output

int XV3Switch = 28;        //input
int XV3LED = 29;           //output

int XV4Switch = 30;        //input
int XV4LED = 31;           //output

int XV5Switch = 32;        //input
int XV5LED = 33;           //output

int XV6Switch = 34;        //input
int XV6LED = 35;           //output

int XV7Switch = 36;        //input
int XV7LED = 37;           //output

int XV8Switch = 38;        //input
int XV8LED = 39;           //output

int XV9Switch = 40;        //input
int XV9LED = 41;           //output

int XV10Switch = 42;       //input
int XV10LED = 43;          //output

int XV11Switch = 44;       //input
int XV11LED = 45;          //output

//ASFAS control and burst disks
int ASFASHandoff = 46;     //input
int valvePower = 47;       //input
int ignitionButton = 48;   //input
int contTestButton = 49;   //input
int RD1Button = 50;        //input
int RD2Button = 51;        //input

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
  //Serial setup
  Serial.begin(115200);
  Serial1.begin(115200);
  computer.begin(Serial);
  testStand.begin(Serial1);

  //Pin mode setup
  {
    //ASFAS LEDs
    pinMode(armedLED, OUTPUT);
    pinMode(activeLED, OUTPUT);
    pinMode(abortLED, OUTPUT);
    pinMode(invalidLED, OUTPUT);
    pinMode(contTestLED, OUTPUT);
    //Error and warning LEDs
    pinMode(keySwitch, INPUT_PULLUP);
    pinMode(buzzerPin, OUTPUT);
    pinMode(errorLED, OUTPUT);
    pinMode(warnLED, OUTPUT);
    pinMode(packetLED, OUTPUT);
    pinMode(waitingLED, OUTPUT);
    pinMode(mismatchLED, OUTPUT);
    pinMode(cautionLED, OUTPUT);
    ////Valve Control Pins
    pinMode(CV1Switch, INPUT_PULLUP);
    pinMode(CV1LED, OUTPUT);
    pinMode(XV1Switch, INPUT_PULLUP);
    pinMode(XV1LED, OUTPUT);
    pinMode(XV2Switch, INPUT_PULLUP);
    pinMode(XV2LED, OUTPUT);
    pinMode(XV3Switch, INPUT_PULLUP);
    pinMode(XV3LED, OUTPUT);
    pinMode(XV4Switch, INPUT_PULLUP);
    pinMode(XV4LED, OUTPUT);
    pinMode(XV5Switch, INPUT_PULLUP);
    pinMode(XV5LED, OUTPUT);
    pinMode(XV6Switch, INPUT_PULLUP);
    pinMode(XV6LED, OUTPUT);
    pinMode(XV7Switch, INPUT_PULLUP);
    pinMode(XV7LED, OUTPUT);
    pinMode(XV8Switch, INPUT_PULLUP);
    pinMode(XV8LED, OUTPUT);
    pinMode(XV9Switch, INPUT_PULLUP);
    pinMode(XV9LED, OUTPUT);
    pinMode(XV10Switch, INPUT_PULLUP);
    pinMode(XV10LED, OUTPUT);
    pinMode(XV11Switch, INPUT_PULLUP);
    pinMode(XV11LED, OUTPUT);
    //ASFAS Input pins
    pinMode(ASFASHandoff, INPUT_PULLUP);
    pinMode(valvePower, INPUT_PULLUP);
    pinMode(ignitionButton, INPUT_PULLUP);
    pinMode(contTestButton, INPUT_PULLUP);
    pinMode(RD1Button, INPUT_PULLUP);
    pinMode(RD2Button, INPUT_PULLUP);
  }
 
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
