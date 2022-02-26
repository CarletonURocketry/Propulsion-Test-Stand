#include "SerialTransfer.h"
#include <HX711_ADC.h>
#include <Servo.h>

//---------------------------------------------------------------------------------------------------
//In its current state this sketch has code that is required for the load cell that is commented out.
//---------------------------------------------------------------------------------------------------


//Pin layout
//A1 Pressure transducer 1
//A2 Pressure transducer 2
//A3 Pressure transducer 3
//A4 Pressure transducer 4
//D2 XV-1
//D3 XV-2
//D4 XV-3
//D5 XV-4
//D6 XV-5
//D7 XV-6
//D8 XV-7
//D9 XV-8
//D10 XV-9
//D11 XV-10
//D13 Fire valve (CV-1) serve PWM
//D18 Serial1 Tx
//D19 Serial1 Rx



// load cell pins:
const int HX711_dout = 3; //mcu > HX711 dout pin
const int HX711_sck = 2; //mcu > HX711 sck pin

//HX711(Load cell amp) constructor:
//HX711_ADC LoadCell(HX711_dout, HX711_sck);

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
  bool Safety; 
} data; //29 bytes

int control_int;

Servo fireServo;

unsigned long millisAtStart = 0;
unsigned long previousMillis = 0;
const long sendInterval = 50;
int controlTest = 0;

bool previousState = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial1.begin(115200);
  testStand.begin(Serial1);
  //LoadCell.begin();
  float calibrationValue = -10015; // calibration value (see example file "Calibration.ino")
  long stabilizingtime = 2000; // preciscion right after power-up can be improved by adding a few seconds of stabilizing time

  //LoadCell.start(stabilizingtime, true);
  /**
  if (LoadCell.getTareTimeoutFlag()) {
    Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
    while (1);
  }
  else {
    LoadCell.setCalFactor(calibrationValue); // set calibration value (float)
    Serial.println("HX711 Startup is complete");
  }
  **/
  fireServo.attach(9);

  
}

void loop() {

  //HX711 Amp Variable
  static boolean newDataReady = 0;

  //Buffer Variables
  uint16_t txSize = 0;
  uint16_t rxSize = 0;

  
  unsigned long currentMillis = millis();
  
  //Check Recieve Buffer
  if (testStand.available()) {
    //Fill Recive Buffer
    rxSize = testStand.rxObj(control_int, rxSize);
    controlTest = control_int;
    //Fire valve control and time since Start
    if ((control_int & 1) & (control_int & ~previousState )) { //Fire valve opens
      millisAtStart = currentMillis;
      fireServo.write(90);
      previousState = (control_int & 1);
      
    } else if (control_int & ~previousState) { //fire valve closes
      data.millisSince = 0;
      fireServo.write(180);
      previousState = (control_int & 1);
      
    } else if (control_int & 1) { //fire valve is open
      data.millisSince = currentMillis - millisAtStart;
      }
  //Do Stuff with control input
  Serial.println(control_int & 1);
  //Send Data Back   
  } else {
    if (currentMillis - previousMillis >= sendInterval) {
      
      previousMillis = currentMillis;
     /**
      // check for new from load cell
      if (LoadCell.update()) {
        data.L1= LoadCell.getData();
        newDataReady = 0;
      }
      **/

      data.P1 = ((analogRead(1)-205)*4.9*0.295);
      data.P2 = ((analogRead(2)-205)*4.9*0.295);
      data.P3 = ((analogRead(3)-205)*4.9*0.295);
      data.P4 = ((analogRead(4)-205)*4.9*0.295);
      txSize = testStand.txObj(data, txSize);
      testStand.sendData(txSize);
      //Serial.println(control_int);
    }
  }
  //do stuff
  if ((control_int & 1 ) == 1){
    digitalWrite(22,HIGH);
  } else {
    digitalWrite(22,LOW);
  }
}
