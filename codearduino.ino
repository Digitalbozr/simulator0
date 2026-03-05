#include <Keyboard.h>
#include <SoftwareSerial.h>

/* ========================
   NANO CONNECTION
======================== */
SoftwareSerial mySerial(9, 7);

/* ======================== */
#define BAUDRATE 115200 

/* ======================= */
struct Button {
  uint8_t pin;
};

Button localButtons[] = {
  {14}, // ENGINE
  {16},
  {4},
  {2},
  {15},
  {A0},
  {A2},
};

const uint8_t localCount = sizeof(localButtons) / sizeof(localButtons[0]);

bool nanoStates[7] = {0,0,0,0,0,0,0};

bool lastHornState = false;
bool lastFarState  = false;
bool lastEngineState = false;

bool codeGameState = false;

String receivedNano = "";
String receivedPC   = "";

/* ======================= */
void setup() {

  Serial.begin(BAUDRATE);
  mySerial.begin(9600);

  for (uint8_t i = 0; i < localCount; i++) {
    pinMode(localButtons[i].pin, INPUT_PULLUP);
  }

  Keyboard.begin();
  Serial.println("MICRO_READY");
}

/* ======================= */
void loop() {

  // =========================
  // 1️⃣ Receive from Nano
  // =========================
  while (mySerial.available()) {
    char c = mySerial.read();

    if (c == '\n') {
      processNanoData(receivedNano);
      receivedNano = "";
    } else {
      receivedNano += c;
    }
  }

  // =========================
  // 2️⃣ Receive from Python
  // =========================
  while (Serial.available()) {

    char c = Serial.read();

    if (c == '\n') {
      processPCCommand(receivedPC);
      receivedPC = "";
    } else {
      receivedPC += c;
    }
  }

  // =====================================================
  // 🔥 ENGINE HOLD (PIN 14)
  // =====================================================

  bool currentEngineState = (digitalRead(localButtons[0].pin) == LOW);

  if (currentEngineState && !lastEngineState) {
    Keyboard.press('e');
    Serial.println("ENGINE_PRESS");
  }

  if (!currentEngineState && lastEngineState) {
    Keyboard.release('e');
    Serial.println("ENGINE_RELEASE");
  }

  lastEngineState = currentEngineState;

  // =====================================================
  // 🔥 KLAXON HOLD (nanoStates[3])
  // =====================================================

  bool currentHornState = nanoStates[3];

  if (currentHornState && !lastHornState) {
    Keyboard.press('2');
    Serial.println("HORN_PRESS");
  }

  if (!currentHornState && lastHornState) {
    Keyboard.release('2');
    Serial.println("HORN_RELEASE");
  }

  lastHornState = currentHornState;

  // =====================================================
  // 🔥 FAR LOGIC
  // =====================================================

  bool currentFarState = nanoStates[2];

  if (!codeGameState) {

    if (currentFarState && !lastFarState) {
      Keyboard.press('3');
      Serial.println("FAR_PRESS");
    }

    if (!currentFarState && lastFarState) {
      Keyboard.release('3');
      Serial.println("FAR_RELEASE");
    }
  }

  lastFarState = currentFarState;

  // =====================================================
  // SEND STATE TO PYTHON
  // =====================================================

  Serial.print("STATE,");

  for (uint8_t i = 0; i < localCount; i++) {
    bool state = (digitalRead(localButtons[i].pin) == LOW);
    Serial.print(state ? 1 : 0);
    Serial.print(",");
  }

  for (uint8_t i = 0; i < 7; i++) {
    Serial.print(nanoStates[i] ? 1 : 0);
    Serial.print(",");
  }

  Serial.println("END");

  delay(50);
}

/* ======================= */
void processNanoData(String data) {

  if (!data.startsWith("START")) return;

  int nanoIndex = 0;

  for (int i = 0; i < data.length(); i++) {

    if (data[i] == '0' || data[i] == '1') {

      nanoStates[nanoIndex] = (data[i] == '1');

      nanoIndex++;

      if (nanoIndex >= 7) break;
    }
  }
}

/* ======================= */
void processPCCommand(String cmd) {

  cmd.trim();

  if (cmd.startsWith("CODE_STATE,")) {

    char value = cmd.charAt(11);

    if (value == '1')
      codeGameState = true;
    else
      codeGameState = false;

    Serial.print("CODE_GAME=");
    Serial.println(codeGameState);
  }

  else if (cmd.startsWith("PRESS,")) {

    char key = cmd.charAt(6);

    Keyboard.press(key);
    delay(30);
    Keyboard.release(key);

    Serial.print("EXECUTED:");
    Serial.println(key);
  }
}
