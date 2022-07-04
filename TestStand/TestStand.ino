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

//SerialTransfer
SerialTransfer testStand;

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

Servo fireServo;

float L1Raw;
float P1Raw;
float P2Raw;
float P3Raw;
float P4Raw; 
float T1Raw;

uint32_t millisAtStart = 0;
uint32_t previousMillis = 0;
uint32_t lastPacket = 0;
const uint8_t sendInterval = 50;
uint8_t badPackets = 0; 



bool previousState = 0;

//ASFAS variables
bool ASFASArmed = false;
bool ASFASActive = false;
bool ASFASAbort = false;
const uint32_t validState = 340289;
bool stateValid = false;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial1.begin(115200);
  testStand.begin(Serial1);
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
          
          if (control_int_incoming & 65536 && not (control_int_incoming & 131072) && control_int_incoming & 262144) {
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

  ASFAS();
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

  //Fire valve control and time since Start
  // This should be tested to see if its still working as intented
  if ((control_int & 1)) { //Fire valve opens
    
    fireServo.writeMicroseconds(1000);
    previousState = (control_int & 1);

  } else {
    fireServo.writeMicroseconds(2250  );
    previousState = (control_int & 1);
  }

  {   //Relay controls
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
    data.T1 = static_cast<uint16_t>((round(T1Raw) + 273) * 10);
  } else {
    data.T1 = 273;
  }

}

void ASFAS() {
  if (control_int & 8192) {
    if (not ASFASAbort) {
      //Determine State
      stateValid = true;
      if (((control_int | 1)) != validState) {
        stateValid = false;
        Serial.println(control_int | 1 );
      }

      //Check state
      if (not ASFASArmed && stateValid) {
        ASFASArmed = true;
      } else if (not stateValid) {
        //Send up Error, ASFAS Invalid State
        data.status = ( data.status | 1 ) | 32;
 
        if (ASFASArmed && not stateValid) {
          ASFASAbort = true;
          //Abort
        }
      }
    
      if (ASFASArmed) {
        // Activation on igniter signal
        if (control_int & 32768) {
          ASFASActive = true;
        }

        //Active check
        if (ASFASActive) {
          // Check abort conditions
          if (ASFASAbort) {
            //Send up Error
            data.status = ( data.status | 1 ) | 32;
            //perform abort
          }
        }
      }
    } else if (not ASFASArmed){
      ASFASAbort = false;
      ASFASActive = false;
      ASFASArmed = false;
    }
  } else {
      ASFASAbort = false;
      ASFASActive = false;
      ASFASArmed = false;
      stateValid = true;
  }

  //Set ASFAS statuses 
  if (ASFASAbort) {
    data.status = data.status | 16;
  }

  if (ASFASActive) {
    data.status = data.status | 8;
  }

  if (ASFASArmed) {
    data.status = data.status | 4;
  }

  
}
