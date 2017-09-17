// Note: it's a code from some years ago, cannot test it right now,
// hopefully it works for you.

#include <LiquidCrystal.h>
#include <Stepper.h>

// Connections:
// rs (LCD pin 4) to Arduino pin 12
// rw (LCD pin 5) to Arduino pin 11
// enable (LCD pin 6) to Arduino pin 10
// LCD pin 15 to Arduino pin 13
// LCD pins d4, d5, d6, d7 to Arduino pins 5, 4, 3, 2
LiquidCrystal lcd(12, 11, 10, 5, 4, 3, 2);

int backLight = 13;    // pin 13 will control the backlight

const int stepsPerRevolution = 200;
int stepperPos = 0;
int desStepperPos;
Stepper myStepper(stepsPerRevolution, 46, 49, 45, 42);

float data[40] = {0};

/*
 * Function:  setup 
 * ----------------
 * initializes serial port and LCD
 */
void setup(void)
{
    Serial.begin(9600);
    pinMode(backLight, OUTPUT);
    digitalWrite(backLight, HIGH);
    lcd.begin(16,2);
    lcd.clear();
    //myStepper.setSpeed(60);
}

/*
 * Function:  loop 
 * ---------------
 * reads data frame, adjusts stepper motor position
 * and prints desired vs actual position on the LCD
 */
void loop(void)
{
    read_frame(data);
    desStepperPos = get_stepper_pos(1);
    if(stepperPos < desStepperPos)
    {
        myStepper.step(1);
        stepperPos ++;
    }
    else if(stepperPos > desStepperPos)
    {
        myStepper.step(-1);
        stepperPos --;
    }
    lcd.setCursor(0,0);
    lcd.print(stepperPos);
    lcd.setCursor(0,1);
    lcd.print(desStepperPos);
}

/*
 * Function:  get_stepper_pos 
 * --------------------------
 * gets desired stepper motor position
 * 
 * p: index of the variable in the data frame
 * 
 * returns: desired stepper motor position
 */
int get_stepper_pos(int p)
{
    float rev;
    float s = data[p];
    switch(p) {
        case 1: // airspeed
            if(s*3.6 < 40.80435) rev = 0.00612*s;
            else if(s*3.6 < 171.2) rev = 0.02268*s-0.1877;
            else rev = 0.01368*s+0.2403;
            break;
        case 2: // altitude
            rev = s/1000;
            break;
        case 3: // vario
            if(s > 5) s = 5;
            else if(s < -5) s = -5;
            rev = s*0.075;
            break;
        default:
            rev = 0;
    }
    return (int)(rev*stepsPerRevolution);
}

/*
 * Function:  read_frame 
 * ---------------------
 * reads data frame to data array
 * 
 * data: data array
 */
void read_frame(float *data)
{
    int n;
    float w;
    if (Serial.available())
    {
        while(Serial.available() < 5);
        n = (int)Serial.read();
        w = read_from_bytes();
        data[n] = w;
    }
}

/*
 * Function:  read_from_bytes 
 * --------------------------
 * reads incoming bytes on the serial port
 * 
 * return: received value (float)
 */
float read_from_bytes(void)
{
    union u_tag {
        byte b[4];
        float ulval;
    } u;
    u.b[0] = Serial.read();
    u.b[1] = Serial.read();
    u.b[2] = Serial.read();
    u.b[3] = Serial.read();
    return u.ulval;
}

