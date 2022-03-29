#include "SerialTransfer.h"
#include <HX711_ADC.h>
#include <Servo.h>
#include <Wire.h>
#include "Adafruit_MCP9600.h"

//Pin layout
//A1 Pressure transducer 1
//A2 Pressure transducer 2
//A3 Pressure transducer 3
//A4 Pressure transducer 4
//D13 Fire valve (CV-1) serv0 PWM (1)
//D22 XV-1 (2)
//D23 XV-2 (4)
//D24 XV-3 (8)
//D25 XV-4 (16)
//D26 XV-5 (32)
//D27 XV-6 (64)
//D28 XV-7 (128)
//D29 XV-8 (256)
//D30 XV-9 (512)
//D31 XV-10 (1024)
//D32 XV-11 (2048)
//D33 Power Relay (4096)
//D18 Serial1 Tx
//D19 Serial1 Rx

//stuff for the thrmocouple
#define I2C_ADDRESS (0x67)
Adafruit_MCP9600 mcp;
bool thermC;

// load cell pins:
const int HX711_dout = 3; //mcu > HX711 dout pin
const int HX711_sck = 2; //mcu > HX711 sck pin

//HX711(Load cell amp) constructor:
HX711_ADC LoadCell(HX711_dout, HX711_sck);

bool loadC;

//SerialTransfer Stuff
SerialTransfer testStand;

struct STRUCT1 {
  float millisSince = 0;
  float L1; //Loadcell
  float P1; //Don't know
  float P2; //Tank Pressure Bottom
  float P3; //Tank Pressure Top
  float P4; //Don't know
  float T1; //Tank Temperature
} data; //28 bytes

int control_int;

Servo fireServo;

unsigned long millisAtStart = 0;
unsigned long previousMillis = 0;
const long sendInterval = 50;


bool previousState = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial1.begin(115200);
  testStand.begin(Serial1);
  LoadCell.begin();
  float calibrationValue = -10015; // calibration value (see example file "Calibration.ino")
  long stabilizingtime = 2000; // preciscion right after power-up can be improved by adding a few seconds of stabilizing time

  LoadCell.start(stabilizingtime, true);

  if (LoadCell.getTareTimeoutFlag()) {
    loadC = false;
  }
  else {
    LoadCell.setCalFactor(calibrationValue); // set calibration value (float)
    loadC = true;
  }
  fireServo.attach(13);

  //Setup the IC2 link to the thermocouple
  if (! mcp.begin(I2C_ADDRESS)) {
    thermC = false;
  } else {
    mcp.setADCresolution(MCP9600_ADCRESOLUTION_18);
    mcp.setThermocoupleType(MCP9600_TYPE_T);
    mcp.setFilterCoefficient(1);
    mcp.enable(true);
    thermC = true;
  }
}

void loop() {

  //HX711 Amp Variable
  // boolean newDataReady = 0;

  //Buffer Variables
  uint16_t txSize = 0;
  uint16_t rxSize = 0;

  unsigned long currentMillis = millis();

  //Check Recieve Buffer
  if (testStand.available()) {
    //Fill Recive Buffer
    rxSize = testStand.rxObj(control_int, rxSize);

    testStandControls();
  }

  //Send Data Back
  if (currentMillis - previousMillis >= sendInterval) {

    previousMillis = currentMillis;

    readSensors();

    txSize = testStand.txObj(data, txSize);
    testStand.sendData(txSize);
  }
}

void testStandControls() {

  //Fire valve control and time since Start
  // This should be tested to see if its still working as intented
  if ((control_int & 1)) { //Fire valve opens
    
    fireServo.writeMicroseconds(1000);
    previousState = (control_int & 1);

  } else {
    fireServo.writeMicroseconds(2250  );
    previousState = (control_int & 1);
  }

  //Relay controls
  //D22 XV-1 (2)
  if (control_int & 2) {
    digitalWrite(22, HIGH);
  } else {
    digitalWrite(22, LOW);
  }
  //D23 XV-2 (4)
  if (control_int & 4) {
    digitalWrite(23, HIGH);
  } else {
    digitalWrite(23, LOW);
  }
  //D24 XV-3 (8)
  if (control_int & 8) {
    digitalWrite(24, HIGH);
  } else {
    digitalWrite(24, LOW);
  }
  //D25 XV-4 (16)
  if (control_int & 16) {
    digitalWrite(25, HIGH);
  } else {
    digitalWrite(25, LOW);
  }
  //D26 XV-5 (32)
  if (control_int & 32) {
    digitalWrite(26, HIGH);
  } else {
    digitalWrite(26, LOW);
  }
  //D27 XV-6 (64)
  if (control_int & 64) {
    digitalWrite(27, HIGH);
  } else {
    digitalWrite(27, LOW);
  }
  //D28 XV-7 (128)
  if (control_int & 128) {
    digitalWrite(28, HIGH);
  } else {
    digitalWrite(28, LOW);
  }
  //D29 XV-8 (256)
  if (control_int & 256) {
    digitalWrite(29, HIGH);
  } else {
    digitalWrite(29, LOW);
  }
  //D30 XV-9 (512)
  if (control_int & 512) {
    digitalWrite(30, HIGH);
  } else {
    digitalWrite(30, LOW);
  }
  //D31 XV-10 (1024)
  if (control_int & 1024) {
    digitalWrite(31, HIGH);
  } else {
    digitalWrite(31, LOW);
  }
  //D32 XV-11 (2048)
  if (control_int & 2048) {
    digitalWrite(32, HIGH);
  } else {
    digitalWrite(32, LOW);
  }
  //D33 Power Relay (4096)
  if (control_int & 4096) {
    digitalWrite(33, HIGH);
  } else {
    digitalWrite(33, LOW);
   }
}

void readSensors() {

  // check for new from load cell
  if (LoadCell.update() and loadC) {
    data.L1 = LoadCell.getData();
    //newDataReady = 0;
  } else {
    data.L1 = 12345;
  }

  data.P1 = ((analogRead(1) - 205) * 4.9 * 0.295);
  data.P2 = ((analogRead(2) - 205) * 4.9 * 0.295);
  data.P3 = ((analogRead(3) - 205) * 4.9 * 0.295);
  data.P4 = ((analogRead(4) - 205) * 4.9 * 0.295);
  if (thermC) {
    data.T1 = mcp.readThermocouple();
  } else {
    data.T1 = 12345;
  }

}
