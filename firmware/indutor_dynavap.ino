/*
 * Indutor DIY para Dynavap — v1 desktop
 *
 * Botão pressionado = aquece. Soltou = para.
 * Timeout 60 s (YLL 3.0) mesmo com o botão preso.
 * Potenciómetro = duty LENTO (120–500 ms). Não é analogWrite no ZVS.
 * TMP36 no dissipador do ZVS: bloqueia em >= 60 °C, libera abaixo de 55 °C.
 *
 * Pinos (Nano): ver BOM_E_FIACAO.md
 *   D2 botão (pull-up, ativo LOW)
 *   D3 TRIG MOSFET
 *   D5 LED status
 *   D6 LED câmara
 *   A0 pot 10k
 *   A1 TMP36
 *
 * Se o MOSFET ligar o ZVS com TRIG em GND, mude MOSFET_ACTIVE_HIGH para 0.
 */

const uint8_t PIN_BUTTON = 2;
const uint8_t PIN_MOSFET = 3;
const uint8_t PIN_LED_STATUS = 5;
const uint8_t PIN_LED_CHAMBER = 6;
const uint8_t PIN_POT = A0;
const uint8_t PIN_TMP36 = A1;

const uint8_t MOSFET_ACTIVE_HIGH = 1;

const unsigned long TIMEOUT_MS = 60000UL;
const unsigned long DEBOUNCE_MS = 30UL;
const unsigned long PULSE_PERIOD_MS = 500UL;
const unsigned long PULSE_ON_MIN_MS = 120UL;  // ZVS precisa arrancar a oscilação
const int FULL_POWER_ADC = 48;                // ~5% do curso: potência cheia
const int TEMP_CUTOFF_C = 60;
const int TEMP_REARM_C = 55;
const int TEMP_VALID_MIN_C = -10;
const int TEMP_VALID_MAX_C = 100;
const unsigned long SERIAL_MS = 500UL;

bool thermalLock = false;
bool timedOut = false;
unsigned long heatStartMs = 0;
unsigned long lastButtonChangeMs = 0;
bool buttonStable = false;              // true = pressionado (ativo)
bool buttonRawPrev = false;
unsigned long lastSerialMs = 0;

void mosfetWrite(bool on) {
  uint8_t level;
  if (MOSFET_ACTIVE_HIGH) {
    level = on ? HIGH : LOW;
  } else {
    level = on ? LOW : HIGH;
  }
  digitalWrite(PIN_MOSFET, level);
}

bool readButtonPressed() {
  bool raw = (digitalRead(PIN_BUTTON) == LOW);
  unsigned long now = millis();
  if (raw != buttonRawPrev) {
    lastButtonChangeMs = now;
    buttonRawPrev = raw;
  }
  if ((now - lastButtonChangeMs) >= DEBOUNCE_MS) {
    buttonStable = raw;
  }
  return buttonStable;
}

int readTempC() {
  int adc = analogRead(PIN_TMP36);
  float volts = adc * (5.0f / 1023.0f);
  return (int)((volts - 0.5f) * 100.0f);
}

bool tempSensorValid(int tempC) {
  return (tempC >= TEMP_VALID_MIN_C && tempC <= TEMP_VALID_MAX_C);
}

bool heatWantedThisCycle(int potAdc, unsigned long now) {
  if (potAdc <= FULL_POWER_ADC) {
    return true;
  }
  unsigned long onMs = map(
      (long)potAdc,
      FULL_POWER_ADC,
      1023L,
      (long)PULSE_PERIOD_MS,
      (long)PULSE_ON_MIN_MS);
  if (onMs < PULSE_ON_MIN_MS) {
    onMs = PULSE_ON_MIN_MS;
  }
  if (onMs > PULSE_PERIOD_MS) {
    onMs = PULSE_PERIOD_MS;
  }
  return ((now % PULSE_PERIOD_MS) < onMs);
}

void setup() {
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_MOSFET, OUTPUT);
  pinMode(PIN_LED_STATUS, OUTPUT);
  pinMode(PIN_LED_CHAMBER, OUTPUT);
  mosfetWrite(false);
  digitalWrite(PIN_LED_STATUS, LOW);
  digitalWrite(PIN_LED_CHAMBER, LOW);
  Serial.begin(9600);
}

void loop() {
  unsigned long now = millis();
  bool pressed = readButtonPressed();
  int potAdc = analogRead(PIN_POT);
  int tempC = readTempC();

  if (tempSensorValid(tempC)) {
    if (tempC >= TEMP_CUTOFF_C) {
      thermalLock = true;
    } else if (tempC <= TEMP_REARM_C) {
      thermalLock = false;
    }
  } else {
    thermalLock = false;
  }

  if (!pressed) {
    timedOut = false;
    heatStartMs = 0;
  } else {
    if (heatStartMs == 0) {
      heatStartMs = now;
    }
    if ((now - heatStartMs) >= TIMEOUT_MS) {
      timedOut = true;
    }
  }

  bool allowHeat = pressed && !thermalLock && !timedOut;
  bool zvsOn = allowHeat && heatWantedThisCycle(potAdc, now);

  mosfetWrite(zvsOn);
  digitalWrite(PIN_LED_CHAMBER, zvsOn ? HIGH : LOW);

  if (thermalLock) {
    digitalWrite(PIN_LED_STATUS, ((now / 120) % 2) ? HIGH : LOW);
  } else if (timedOut) {
    digitalWrite(PIN_LED_STATUS, ((now / 400) % 2) ? HIGH : LOW);
  } else if (zvsOn) {
    digitalWrite(PIN_LED_STATUS, HIGH);
  } else if (allowHeat) {
    digitalWrite(PIN_LED_STATUS, ((now / 80) % 2) ? HIGH : LOW);
  } else {
    digitalWrite(PIN_LED_STATUS, LOW);
  }

  if ((now - lastSerialMs) >= SERIAL_MS) {
    lastSerialMs = now;
    Serial.print(F("btn="));
    Serial.print(pressed ? 1 : 0);
    Serial.print(F(" pot="));
    Serial.print(potAdc);
    Serial.print(F(" T="));
    Serial.print(tempC);
    Serial.print(F(" Ts="));
    Serial.print(tempSensorValid(tempC) ? 1 : 0);
    Serial.print(F(" lock="));
    Serial.print(thermalLock ? 1 : 0);
    Serial.print(F(" to="));
    Serial.print(timedOut ? 1 : 0);
    Serial.print(F(" zvs="));
    Serial.println(zvsOn ? 1 : 0);
  }
}
