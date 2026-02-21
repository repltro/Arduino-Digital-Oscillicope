const int potPin = A0;
const int potPin2 = A2;
const int probePin = A1;
const int dataLED = 9;

void setup() {
  pinMode(potPin, INPUT);
  pinMode(potPin2, INPUT);
  pinMode(probePin, INPUT);
  pinMode(dataLED, OUTPUT);
  Serial.begin(115200);
}

void loop(){
  float potValue = analogRead(potPin);
  float potValue2 = analogRead(potPin2);
  int rawProbe = analogRead(probePin);

  float theoreticalVoltage = (rawProbe * 0.05335);
  float experimentalVoltage = (rawProbe * 0.05143) + 0.06;
  float potMap = ceil((potValue/1023)*10);
  float potMap2 = ceil((potValue2/1023)*10);

  if (experimentalVoltage > 1) {
    analogWrite(dataLED, 20);
  }
  else {
    digitalWrite(dataLED, LOW);
  } 

  Serial.print("Potentiometer 1: ");
  Serial.print(potValue);
  Serial.print(" | Potentiometer 2: ");
  Serial.print(potValue2);
  Serial.print(" | Theoretical Voltage Measurement: ");
  Serial.print(theoreticalVoltage);
  Serial.print(" | experimantalVoltage: ");
  Serial.print(experimentalVoltage);
  Serial.print(" | rawProbe readout: ");
  Serial.print(rawProbe);
  Serial.print(" | Pot 1 mapped: ");
  Serial.print(potMap);
  Serial.print(" | Pot 2 mapped: ");
  Serial.println(potMap2);
  
  delay(100);
}