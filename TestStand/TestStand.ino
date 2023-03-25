#include "SerialTransfer.h"
#include <HX711_ADC.h>
#include <Servo.h>
#include <Wire.h>
#include "Adafruit_MCP9600.h"

//---Pin layout---

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
//D18 Serial1 Tx
//D19 Serial1 Rx

//Presssure Tranducers
const int numOfPt = 4;
int PtPins[numOfPt] = {A0, A1, A2, A3};
//Fire Valve
int fireValvePin = 8;

Servo fireServo;

//Solenoid Valves
const int numOfSolValve = 12;
int SolValvePins[numOfSolValve] = {22,23,24,25,26,27,28,29,30,31,32,33};

//Ignitor
int ignitorPin = 7;

//Keyswitch
int keyPin = 41;

//Thermocouple
#define I2C_ADDRESS (0x67)
Adafruit_MCP9600 mcp;
bool thermC;

//Load Cells
const int HX711_dout = 3; //mcu > HX711 dout pin
const int HX711_sck = 4; //mcu > HX711 sck pin

HX711_ADC LoadCell(HX711_dout, HX711_sck);
bool loadC;

//SerialTransfer
SerialTransfer testStand;

struct STRUCT1 {
  uint16_t L1; //Loadcell
  uint16_t P1; //Don't know
  uint16_t P2; //Tank Pressure Bottom
  uint16_t P3; //Tank Pressure Top
  uint16_t P4; //Don't know
  uint16_t T1; //Tank Temperature
  uint32_t status = 0; //Status int
} data; //16 bytes


//Commands recived from the control box
uint32_t control_int;

//Actuall state of the valves
uint32_t state_int; 
//should only be different from the control_int if the ASFAS is perfoming and abort.

//Sensor Variables
float L1Raw;
float P1Raw;
float P2Raw;
float P3Raw;
float P4Raw; 
float T1Raw;

//Other Variables and constants
uint32_t millisAtStart = 0;
uint32_t previousMillis = 0;
uint32_t lastPacket = 0;
const uint8_t sendInterval = 1000;
uint8_t badPackets = 0; 
bool previousState = 0;


//ASFAS variables
bool ASFASArmed = false;
bool ASFASActive = false;
bool ASFASAbort = false;
const uint32_t validState = 340289;
bool stateValid = false;

//ASFAS Abort conditions
const int maxP1 = 1000;
const int minP1 = 0;

const int maxP2 = 1000;
const int minP2 = 0;

const int maxP3 = 1000;
const int minP3 = 0;

const int maxP4 = 1000;
const int minP4 = 0;

const int maxT1 = 30;
const int minT1 = 5;

void setup() {
  //Serial Setup
  Serial.begin(115200);
  Serial1.begin(115200);
  testStand.begin(Serial1);
  
  //Load Cell Start up and Calibration
  LoadCell.begin();
  float calibrationValue = -10015; // calibration value (see example file "Calibration.ino")
  uint16_t stabilizingtime = 2000; // preciscion right after power-up can be improved by adding a few seconds of stabilizing time

  LoadCell.start(stabilizingtime, true);

  if (LoadCell.getTareTimeoutFlag()) {
    loadC = false;
  }
  else {
    LoadCell.setCalFactor(calibrationValue); // set calibration value (float)
    loadC = true;
  }

  //Servo
  fireServo.attach(fireValvePin);

  //Thermocouple startup
  if (! mcp.begin(I2C_ADDRESS)) {
    thermC = false;
  } else {
    mcp.setADCresolution(MCP9600_ADCRESOLUTION_18);
    mcp.setThermocoupleType(MCP9600_TYPE_T);
    mcp.setFilterCoefficient(1);
    mcp.enable(true);
    thermC = true;
  }

  //Pin mode setup
  
  //Solenoid Valves
  for (int i = 0; i < numOfSolValve; i++) {
    pinMode(SolValvePins[i], OUTPUT);
  }
  
  //Pressure Tranducers
  for (int i = 0; i < numOfPt; i ++) {
    pinMode(PtPins[i], INPUT);
  }

  //Other Pins
  pinMode(fireValvePin, OUTPUT);
  pinMode(ignitorPin, OUTPUT);
  pinMode(keyPin,INPUT_PULLUP);
}

void loop() {

  //HX711 Amp Variable
  //boolean newDataReady = 0;

  //Buffer Variables
  uint16_t txSize = 0;
  uint16_t rxSize = 0;

  //New Time
  uint32_t currentMillis = millis();

  //Check Receive Buffer
  if (testStand.available()) {
    
    //Check packet status and warn 
    if (testStand.status < 1) {
      badPackets++;
      if (badPackets > 10) {
          data.status = ( data.status | 1 ) | 512;
      } else {
          data.status = ( data.status | 2 ) | 512;
      }
    } else {

          //Copy Receive Buffer into control_int
          uint32_t control_int_incoming = 0;
          rxSize = testStand.rxObj(control_int_incoming, rxSize);

          if (bitRead(control_int_incoming,16) && !bitRead(control_int_incoming,17) && bitRead(control_int_incoming,18)) {
            control_int = control_int_incoming;
            lastPacket = currentMillis;
          }
    }
    
  } else {
      //Warn if no packets received in last second
      if(currentMillis - lastPacket >= 5000) {
        data.status = ( data.status | 1 ) | 256;
      } else if (currentMillis - lastPacket >= 1000) {
        data.status = ( data.status | 2 ) | 256;
      }

  }
  
  //ASFAS();
  state_int = control_int;
  testStandControls();

  //Send Data Back
  if (currentMillis - previousMillis >= sendInterval) {

    previousMillis = currentMillis;

    readSensors();
    txSize = testStand.txObj(data, txSize);
    testStand.sendData(txSize);
    data.status = 0;
  }
}

void testStandControls() {

  //Fire valve control
  if (bitRead(state_int,0)) { //Fire valve opens
    fireServo.writeMicroseconds(900);
  } else { // Fire valve closes
    fireServo.writeMicroseconds(1600);
  }

  //Toggle Igniter Relay
  if (bitRead(state_int,14)) {
    digitalWrite(ignitorPin,HIGH);
  } else {
    digitalWrite(ignitorPin,LOW);
  }


  //Toggle Relays According to State_int
  for (int i = 0; i < numOfSolValve; i++) {
    digitalWrite(SolValvePins[i],bitRead(state_int,i));
  }
}

void readSensors() {

  // check for new from load cell
  if (LoadCell.update() and loadC) {
    L1Raw = LoadCell.getData();
    data.L1 = static_cast<uint16_t>(round(L1Raw));
    //newDataReady = 0;
  } else {
    data.L1 = 0;
  }

  P1Raw = ((analogRead(1) - 205) * 4.9 * 0.295);
  P2Raw = ((analogRead(2) - 205) * 4.9 * 0.295);
  P3Raw = ((analogRead(3) - 205) * 4.9 * 0.295);
  P4Raw = ((analogRead(4) - 205) * 4.9 * 0.295);


  data.P1 = static_cast<uint16_t>(round(P1Raw));
  data.P2 = static_cast<uint16_t>(round(P2Raw));
  data.P3 = static_cast<uint16_t>(round(P3Raw));
  data.P4 = static_cast<uint16_t>(round(P4Raw));

  if (thermC) {
    T1Raw = mcp.readThermocouple();
    data.T1 = static_cast<uint16_t>((round(T1Raw)) * 10);
  } else {
    data.T1 = 300;
  }

  //Add the real state of the valves to the status
  for (int i = 0; i < 12; i++) {
    bitWrite(data.status,i+16,bitRead(state_int,i));
  }
}

void ASFAS() { //Remake this shit
  if (control_int & 8192) {
    if (not ASFASAbort) {
      //Determine State
      stateValid = true;
      if (((control_int | 1)) != validState) {
        stateValid = false;
        Serial.println(control_int | 1 );
      } else {
        state_int = control_int;
      }

      //Check state
      if (not ASFASArmed && stateValid) {
        ASFASArmed = true;
      } else if (not stateValid) {
        //Send up Error, ASFAS Invalid State
        data.status = ( data.status | 1 ) | 32;
      }
    
      if (ASFASArmed) {
        // Activation on igniter signal
        if (control_int & 32768) {
          ASFASActive = true;
        }

        //Active check
        if (ASFASActive) {
          // Check abort conditions
          if (not stateValid) {
            ASFASAbort = true;
          }

          if (ASFASAbort) {
            //Send up Error
            data.status = ( data.status | 1 ) | 32;
            //Abort Procedures

          }
        }
      }
    } else if (not ASFASArmed){
      ASFASAbort = false;
      ASFASActive = false;
      ASFASArmed = false;
    }
  } else {
      state_int = control_int;
      ASFASAbort = false;
      ASFASActive = false;
      ASFASArmed = false;
      stateValid = true;
  }

  //Set ASFAS statuses 
  if (ASFASAbort) {
    bitSet(data.status,4);
  }

  if (ASFASActive) {
    bitSet(data.status,3);
  }

  if (ASFASArmed) {
    bitSet(data.status,2);
  }
  
}
