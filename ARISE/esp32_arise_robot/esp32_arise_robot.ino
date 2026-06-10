/*
 * ============================================================
 *   A.R.I.S.E  —  ESP32 Robot Firmware
 *   Autonomous Robot Inventory Scanning ERP System
 * ============================================================
 *
 * HARDWARE WIRING:
 * ─────────────────────────────────────────────────────────────
 *  ULTRASONIC SENSOR (HC-SR04):
 *    VCC  → 5V  (or 3.3V with voltage divider on ECHO)
 *    GND  → GND
 *    TRIG → GPIO 5
 *    ECHO → GPIO 18
 *
 *  MQ-135 GAS SENSOR:
 *    VCC  → 5V
 *    GND  → GND
 *    AOUT → GPIO 34  (Analog pin — ADC1)
 *
 *  MOTOR DRIVER (L298N) — optional for movement tracking:
 *    ENA  → GPIO 25  (PWM)
 *    IN1  → GPIO 26
 *    IN2  → GPIO 27
 *    ENB  → GPIO 14  (PWM)
 *    IN3  → GPIO 12
 *    IN4  → GPIO 13
 *
 * NETWORK SETUP:
 * ─────────────────────────────────────────────────────────────
 *  The ESP32 can run in TWO modes (change MODE below):
 *
 *  MODE 1 — ACCESS POINT (default, no router needed)
 *    ESP32 creates its own WiFi network.
 *    Connect PC to:  SSID: "ARISE-Robot"  Pass: "arise2024"
 *    Dashboard URL:  http://192.168.4.1/telemetry
 *
 *  MODE 2 — STATION (connect to existing WiFi)
 *    ESP32 joins your home/lab WiFi.
 *    Set STA_SSID and STA_PASS below, then read IP from Serial.
 *    Dashboard URL:  http://<IP_SHOWN_IN_SERIAL>/telemetry
 *
 * LIBRARY DEPENDENCIES (install via Arduino Library Manager):
 *  • WiFi          (built-in with ESP32 board package)
 *  • WebServer     (built-in with ESP32 board package)
 *  • ArduinoJson   (v6)  — search "ArduinoJson" by Benoit Blanchon
 *
 * BOARD SETUP (Arduino IDE):
 *  Tools → Board → "ESP32 Dev Module" (or your specific variant)
 *  Upload Speed: 921600
 *  Flash Size: 4MB
 *  CPU Frequency: 240MHz
 * ============================================================
 */

#include <ArduinoJson.h>
#include <WebServer.h>
#include <WiFi.h>

// ─── CONFIGURATION ───────────────────────────────────────────

// Network Mode: "AP" = Access Point, "STA" = Station (join WiFi)
#define NETWORK_MODE "AP"

// AP Mode credentials (ESP32 creates this network)
const char *AP_SSID = "ARISE-Robot";
const char *AP_PASS = "arise2024";

// STA Mode credentials (only used if NETWORK_MODE = "STA")
const char *STA_SSID = "YourWiFiName";
const char *STA_PASS = "YourWiFiPassword";

// ─── PIN DEFINITIONS ─────────────────────────────────────────
#define TRIG_PIN 5  // HC-SR04 Trigger
#define ECHO_PIN 18 // HC-SR04 Echo
#define GAS_PIN 34  // MQ-135 Analog Out (ADC1_CH6)

// ─── GLOBALS ─────────────────────────────────────────────────
WebServer server(80);

float lastDist = 0.0;
int lastGas = 0;
float lastVolt = 0.0;
unsigned long scanCount = 0;
unsigned long lastScanTime = 0;

// Moving average buffers for smoother readings
#define SMOOTH_SAMPLES 5
float distBuffer[SMOOTH_SAMPLES] = {0};
int gasBuffer[SMOOTH_SAMPLES] = {0};
int smoothIdx = 0;

// ─── SENSOR FUNCTIONS ────────────────────────────────────────

float measureDistance() {
  // Send 10µs pulse
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Read echo pulse duration (timeout = 25000µs ≈ ~4.3m max range)
  long duration = pulseIn(ECHO_PIN, HIGH, 25000);
  if (duration == 0)
    return 400.0; // Out of range → treat as empty shelf

  float dist = (duration * 0.034) / 2.0; // Convert to cm
  return constrain(dist, 2.0, 400.0);
}

int measureGas() {
  // Read raw 12-bit ADC value (0–4095)
  int raw = analogRead(GAS_PIN);
  return raw;
}

float getSmoothedDistance() {
  float total = 0;
  for (int i = 0; i < SMOOTH_SAMPLES; i++)
    total += distBuffer[i];
  return total / SMOOTH_SAMPLES;
}

int getSmoothedGas() {
  long total = 0;
  for (int i = 0; i < SMOOTH_SAMPLES; i++)
    total += gasBuffer[i];
  return total / SMOOTH_SAMPLES;
}

// ─── HTTP HANDLERS ───────────────────────────────────────────

// CORS helper — allows browser to call from any origin
void addCORSHeaders() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.sendHeader("Cache-Control", "no-cache, no-store");
}

// OPTIONS preflight (browser sends before cross-origin GET)
void handleOptions() {
  addCORSHeaders();
  server.send(200, "text/plain", "OK");
}

/*
 * GET /telemetry
 * Returns JSON with all sensor data.
 * Dashboard polls this endpoint every ~3 seconds.
 *
 * Response format:
 * {
 *   "dist":    42.5,     // cm from ultrasonic sensor
 *   "gas":     128,      // raw ADC (0–4095 on ESP32)
 *   "voltage": 0.62,     // computed gas voltage (V)
 *   "status":  "OK",     // "OK" | "GAS_ALERT" | "OUT_OF_RANGE"
 *   "uptime":  12345,    // ms since boot
 *   "scans":   7,        // total scan cycles completed
 *   "ip":      "192.168.4.1"
 * }
 */
void handleTelemetry() {
  addCORSHeaders();

  // Fresh readings
  float rawDist = measureDistance();
  int rawGas = measureGas();

  // Update smooth buffers
  distBuffer[smoothIdx] = rawDist;
  gasBuffer[smoothIdx] = rawGas;
  smoothIdx = (smoothIdx + 1) % SMOOTH_SAMPLES;

  lastDist = getSmoothedDistance();
  lastGas = getSmoothedGas();
  lastVolt = lastGas * (3.3 / 4095.0);
  scanCount++;
  lastScanTime = millis();

  // Determine status string
  String status = "OK";
  if (lastGas > 1000)
    status = "GAS_ALERT";
  else if (lastDist >= 380)
    status = "OUT_OF_RANGE";

  // Build JSON response
  StaticJsonDocument<256> doc;
  doc["dist"] = round(lastDist * 10) / 10.0; // 1 decimal
  doc["gas"] = lastGas;
  doc["voltage"] = round(lastVolt * 100) / 100.0;
  doc["status"] = status;
  doc["uptime"] = millis();
  doc["scans"] = scanCount;
  doc["ip"] = WiFi.localIP().toString();

  String output;
  serializeJson(doc, output);

  Serial.println("[TELEMETRY] → " + output);
  server.send(200, "application/json", output);
}

/*
 * GET /ping
 * Simple liveness check — returns {"alive": true}
 */
void handlePing() {
  addCORSHeaders();
  server.send(200, "application/json",
              "{\"alive\":true,\"device\":\"ARISE-Robot\"}");
}

/*
 * GET /status
 * Returns detailed system status for the dashboard connection panel.
 */
void handleStatus() {
  addCORSHeaders();
  StaticJsonDocument<256> doc;
  doc["alive"] = true;
  doc["device"] = "ARISE-ESP32-Robot";
  doc["firmware"] = "v1.2.0";
  doc["mode"] = NETWORK_MODE;
  doc["ip"] = WiFi.localIP().toString();
  doc["rssi"] = (String(NETWORK_MODE) == "STA") ? WiFi.RSSI() : 0;
  doc["uptime"] = millis();
  doc["freeHeap"] = ESP.getFreeHeap();
  doc["lastDist"] = lastDist;
  doc["lastGas"] = lastGas;
  doc["scanCount"] = scanCount;

  String out;
  serializeJson(doc, out);
  server.send(200, "application/json", out);
}

// 404 fallback
void handleNotFound() {
  addCORSHeaders();
  server.send(404, "application/json", "{\"error\":\"Not Found\"}");
}

// ─── SETUP ───────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n============================");
  Serial.println("  A.R.I.S.E Robot Firmware");
  Serial.println("============================\n");

  // Pin modes
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(GAS_PIN, INPUT);

  // Set ADC resolution to 12-bit (max for ESP32)
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db); // Full range 0–3.3V

  // ─── Network setup ───────────────────────────────────────
  if (String(NETWORK_MODE) == "AP") {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    IPAddress ip = WiFi.softAPIP();
    Serial.println("[WIFI] Mode: Access Point");
    Serial.println("[WIFI] SSID: " + String(AP_SSID));
    Serial.println("[WIFI] Password: " + String(AP_PASS));
    Serial.print("[WIFI] IP Address: ");
    Serial.println(ip);
    Serial.println("\n→ Connect your PC to \"ARISE-Robot\" WiFi");
    Serial.println("→ Then enter http://" + ip.toString() +
                   " in the dashboard\n");
  } else {
    WiFi.mode(WIFI_STA);
    WiFi.begin(STA_SSID, STA_PASS);
    Serial.print("[WIFI] Connecting to ");
    Serial.print(STA_SSID);
    int tries = 0;
    while (WiFi.status() != WL_CONNECTED && tries < 30) {
      delay(500);
      Serial.print(".");
      tries++;
    }
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n[WIFI] Connected!");
      Serial.print("[WIFI] IP Address: ");
      Serial.println(WiFi.localIP());
      Serial.println("→ Enter this IP in the ARISE Dashboard\n");
    } else {
      Serial.println("\n[WIFI] Connection FAILED. Restarting...");
      delay(2000);
      ESP.restart();
    }
  }

  // ─── Register HTTP routes ─────────────────────────────────
  server.on("/telemetry", HTTP_GET, handleTelemetry);
  server.on("/telemetry", HTTP_OPTIONS, handleOptions);
  server.on("/ping", HTTP_GET, handlePing);
  server.on("/ping", HTTP_OPTIONS, handleOptions);
  server.on("/status", HTTP_GET, handleStatus);
  server.onNotFound(handleNotFound);
  server.begin();

  Serial.println("[HTTP] Server started on port 80");
  Serial.println("[HTTP] Endpoints:");
  Serial.println(
      "  GET /telemetry  — Sensor data (dist, gas, voltage, status)");
  Serial.println("  GET /ping       — Liveness check");
  Serial.println("  GET /status     — Full system status");
  Serial.println("\n[SYS] Ready. Waiting for dashboard...\n");
}

// ─── MAIN LOOP ───────────────────────────────────────────────
void loop() {
  server.handleClient();

  // Print live readings to Serial every 2 seconds (for debugging)
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 2000) {
    float d = measureDistance();
    int g = measureGas();
    float v = g * (3.3 / 4095.0);
    Serial.printf("[LIVE] Dist: %.1f cm | Gas: %d (%.2fV) | Heap: %d\n", d, g,
                  v, ESP.getFreeHeap());
    lastPrint = millis();
  }

  delay(10);
}
