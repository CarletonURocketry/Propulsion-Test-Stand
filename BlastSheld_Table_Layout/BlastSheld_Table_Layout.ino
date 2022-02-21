// Python Communication Code derived from: https://www.instructables.com/Arduino-Serial-Communication/

#include "SerialTransfer.h"


SerialTransfer testStand;
SerialTransfer commandPanel;

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

  //pinMode(8, INPUT_PULLUP);
  commandPanel.begin(Serial);
  testStand.begin(Serial1);
}

void loop() {
  //Buffer Variables
  //uint16_t txSize = 0;
  //uint16_t rxSize = 0;

  if (testStand.available()) {
    //Fill Recive Buffer
    testStand.rxObj(data, sizeof(data));
    sendData();
  }

  if (commandPanel.avaliable()) {
    // Fill Recieve Buffer
    // Code is solenoid number 1,2,3,4 and 0 or 1 for off or on
    x = Serial.readString().toInt();
    if (x == 10) {
      control.fire = false;
    } elseif (x == 11) {
      control.fire = true;
    } elseif (x == 20) {
      control.fill = false;
    } elseif (x == 21) {
      control.fill = true;
    } elseif (x == 30) {
      control.vent = false;
    } elseif (x == 31) {
      control.vent = true;
    } elseif (x == 40) {
      control.power = false;
    } elseif (x == 41) {
      control.power = true;
    }
  }
  //if (digitalRead(8) == HIGH) {
  //  control.fire = false;
  //}
  //else control.fire = true;

  //Fill Transmit Buffer
  testStand.txObj(control, sizeof(control));

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
    //Fill Transmit Buffer
    testStand.sendData(txSize);
    //Serial.println(digitalRead(8));
  }
}

void sendData() {
  //Serial.print(data.millisSince);
  //Serial.print(",");
  //Serial.print(data.loadcell);
  //Serial.print(",");
  Serial.println(data.tankPres);
  //Serial.print(",");
  //Serial.print(data.tankTemp);
  //Serial.print(",");
  //Serial.println(data.tankFill);
}
