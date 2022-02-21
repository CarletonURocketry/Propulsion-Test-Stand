#include "SerialTransfer.h"
//#include <HX711_ADC.h>
#include <Servo.h>

//---------------------------------------------------------------------------------------------------
//In its current state this sketch has code that is required for the load cell that is commented out.
//---------------------------------------------------------------------------------------------------

// load cell pins:
const int HX711_dout = 3; //mcu > HX711 dout pin
const int HX711_sck = 2; //mcu > HX711 sck pin

//HX711(Load cell amp) constructor:
//HX711_ADC LoadCell(HX711_dout, HX711_sck);

//SerialTransfer Stuff
SerialTransfer testStand;

struct STRUCT1 {
  float millisSince = 0;
  float loadcell = 0;
  float tankPres = 0;
  float tankTemp = 0;
  float tankFill = 0;
} data;

struct STRUCT2 {
  bool fire;
  bool fill;
  bool vent;
  bool power;
} control;

char errorCode[] = "NOER";

Servo fireServo;

unsigned long millisAtStart = 0;
unsigned long previousMillis = 0;
const long sendInterval = 100;

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
    rxSize = testStand.rxObj(control, rxSize);
    //Fire valve control and time since Start
    
    if (control.fire and control.fire != previousState) { //Fire valve opens
      millisAtStart = currentMillis;
      fireServo.write(90);
      previousState = control.fire;
      
    } else if (control.fire != previousState) { //fire valve closes
      data.millisSince = 0;
      fireServo.write(180);
      previousState = control.fire;
      
    } else if (control.fire) { //fire valve is open
      data.millisSince = currentMillis - millisAtStart;
      }
      
  } else {
    if (currentMillis - previousMillis >= sendInterval) {
      
      previousMillis = currentMillis;
     
     /**
      // check for new from load cell
      if (LoadCell.update()) {
        data.loadcell = LoadCell.getData();
        newDataReady = 0;
      }
      **/
      data.loadcell = sin(currentMillis);

      txSize = testStand.txObj(data, txSize);
      testStand.sendData(txSize);
    }
  }




  //txSize = testStand.txObj(errorCode, txSize); //not sure what this is for



}
