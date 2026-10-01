#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "7semi_HX711.h" // Используем библиотеку 7Semi

// Пины HX711
#define HX711_DOUT 2
#define HX711_SCK  3

// Калибровочный коэффициент — подберите под свой датчик
#define CALIBRATION_FACTOR -454.5

// Адрес LCD. Если не работает — попробуйте 0x3F
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Создаем объект класса HX711_7semi, как в примере
HX711_7semi scale(HX711_DOUT, HX711_SCK);

void setup() {
  Serial.begin(9600);

  // Инициализация LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Weight:");

  // Инициализация HX711
  scale.begin();
  scale.setGain(GAIN_128); // Установка усиления, как в примере
  scale.setTimeout(1000);  // Тайм-аут для чтения
  scale.setScale(CALIBRATION_FACTOR);

  // Тарирование (сброс в ноль)
  lcd.setCursor(0, 1);
  lcd.print("Taring...");
  delay(2000);
  scale.tare();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Weight:");
}

void loop() {
  // Чтение веса. Метод getWeight() сам усредняет показания
  float weight = scale.getWeight();

  // Вывод на LCD
  lcd.setCursor(0, 1);
  lcd.print("                "); // Очистка строки
  lcd.setCursor(0, 1);
  lcd.print(weight, 1);
  lcd.print(" g");

  // Дублирование в монитор порта
  Serial.print("Weight: ");
  Serial.print(weight, 2);
  Serial.println(" g");

  delay(500);
}