#include <Servo.h>

Servo servos[6];

const int servoPins[6] = {3, 5, 6, 9, 10, 11};

const int NUM_SERVOS = 6;
const int MOVE_STEP = 2; // smoothing step in degrees
const int UPDATE_MS = 20; // update interval

int currentAngle[6];
int targetAngle[6];

void setup() {
  Serial.begin(115200);
  for (int i=0; i<NUM_SERVOS; ++i) {
    servos[i].attach(servoPins[i]);
    currentAngle[i] = 90; // safe midpose; change if needed
    targetAngle[i] = 90;
    servos[i].write(currentAngle[i]);
  }
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    if (line.length() > 2 && line.startsWith("S:")) {
      line = line.substring(2);
      int idx = 0;
      int start = 0;
      for (int i=0; i<NUM_SERVOS; ++i) {
        int comma = line.indexOf(',', start);
        String token;
        if (comma == -1) {
          token = line.substring(start);
        } else {
          token = line.substring(start, comma);
          start = comma + 1;
        }
        token.trim();
        if (token.length() > 0) {
          int ang = token.toInt();
          ang = constrain(ang, 0, 180); // enforce safe range
          targetAngle[i] = ang;
        }
      }
    }
  }


  bool moved = false;
  for (int i=0; i<NUM_SERVOS; ++i) {
    if (currentAngle[i] < targetAngle[i]) {
      currentAngle[i] = min(currentAngle[i] + MOVE_STEP, targetAngle[i]);
      servos[i].write(currentAngle[i]);
      moved = true;
    } else if (currentAngle[i] > targetAngle[i]) {
      currentAngle[i] = max(currentAngle[i] - MOVE_STEP, targetAngle[i]);
      servos[i].write(currentAngle[i]);
      moved = true;
    }
  }
  delay(UPDATE_MS);
}
