float temp;
int cambien = 4;
int dung = 7;
void setup(){
  Serial.begin(9600);
  pinMode(cambien,INPUT_PULLUP);
   pinMode(dung,OUTPUT);
}
void loop(){
  int reading = analogRead(A0);
  float voltage = reading * 5.0 / 1024.0;
  float temp = voltage*100.0;
  if (digitalRead(cambien)==0){
    Serial.println(String(temp)+String("|")+String(1));
  }
  else{
    Serial.println(String(temp)+String("|")+String(0));
  }
  delay(1000);
}
