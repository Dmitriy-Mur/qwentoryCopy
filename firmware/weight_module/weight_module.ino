#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "7semi_HX711.h"

// Пины HX711
#define HX711_DOUT 2
#define HX711_SCK  3

// Калибровочный коэффициент — подберите под свой датчик
#define CALIBRATION_FACTOR -454.5

// Протокол Serial 9600: одна строка WEIGHT:<граммы>
// Десктоп и scale-bridge публикуют её в POST /scale

LiquidCrystal_I2C lcd(0x27, 16, 2);
HX711_7semi scale(HX711_DOUT, HX711_SCK);

void setup() {
  Serial.begin(9600);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Weight:");

  scale.begin();
  scale.setGain(GAIN_128);
  scale.setTimeout(1000);
  scale.setScale(CALIBRATION_FACTOR);

  lcd.setCursor(0, 1);
  lcd.print("Taring...");
  delay(2000);
  scale.tare();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Weight:");
}

void loop() {
  float weight = scale.getWeight();

  lcd.setCursor(0, 1);
  lcd.print("                ");
  lcd.setCursor(0, 1);
  lcd.print(weight, 1);
  lcd.print(" g");

  Serial.print("WEIGHT:");
  Serial.println(weight, 2);

  delay(500);
}
