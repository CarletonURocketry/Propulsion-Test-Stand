//these variables are only here so that there aren't red squiggly lines everywhere (there are still a few tho)
unsigned short control_int;
Servo fireServo;
unsigned long millisAtStart = 0;
bool previousState = 0;

void testStandControls()
{
    int bitCounter = 2;

    // Fire valve control and time since Start
    //  This should be tested to see if its still working as intented
    if ((control_int & 1)) { // Fire valve opens
        fireServo.writeMicroseconds(1000);
        previousState = (control_int & 1);
    } else {
        fireServo.writeMicroseconds(2250);
        previousState = (control_int & 1);
    }

    for (int i = 22; i <=33; ++i) {
        if (control_int & bitCounter) {
            digitalWrite(i, HIGH);
         } else {
            digitalWrite(i, LOW);
        }
        bitCounter*=2;
    }
}