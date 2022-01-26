#include "SerialTransfer.h"


SerialTransfer testStand;

struct STRUCT1 {
  float millisSince = 0;
  float loadcell;
  float tankPres;
  float tankTemp;
  float tankFill;
} data;

struct STRUCT2 {
  bool fire = false;
  bool fill = false;
  bool vent = false;
  bool power = false;
} control;

char errorCode[6];

unsigned long previousMillis = 0;
const long interval = 100;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial1.begin(115200);

  pinMode(8, INPUT_PULLUP);

  testStand.begin(Serial1);
}

void loop() {
  //Buffer Variables
  uint16_t txSize = 0;
  uint16_t rxSize = 0;

  if (testStand.available()) {
    //Fill Recive Buffer
    rxSize = testStand.rxObj(data, rxSize);
    printdata();
    
  }

  if (digitalRead(8) == HIGH) {
    control.fire = false;
  }
  else control.fire = true;

  //Fill Transmit Buffer
  txSize = testStand.txObj(control, txSize);

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
    //Fill Transmit Buffer
    testStand.sendData(txSize);
    //Serial.println(digitalRead(8));

  }
}

void printdata() {
  Serial.print(data.millisSince);
  Serial.print(",");
  Serial.print(data.loadcell);
  Serial.print(",");
  Serial.print(data.tankPres);
  Serial.print(",");
  Serial.print(data.tankTemp);
  Serial.print(",");
  Serial.println(data.tankFill);
}
