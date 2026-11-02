// =====================================================
// PRACTICAL NO. 03
// INTERFACING WITH PIR SENSOR
// =====================================================

const int pirPin = 2;
const int ledPin = 13;

void setup() {
  pinMode(pirPin, INPUT);
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int pirState = digitalRead(pirPin);

  if (pirState == HIGH) {
    digitalWrite(ledPin, HIGH);
    Serial.println("Motion detected!");
  } else {
    digitalWrite(ledPin, LOW);
    Serial.println("No motion");
  }

  delay(1000);
}


// =====================================================
// PRACTICAL NO. 04
// CPS MONITORING AND CONTROL
// =====================================================

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "nikhil";
const char* password = "12345678";

ESP8266WebServer server(80);

const int ledPin = D1;
float temperature = 28.5;
bool ledState = false;

void handleRoot() {
  String page = "<html><head>";
  page += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  page += "<title>CPS Monitoring</title></head>";
  page += "<body style='font-family:Arial;text-align:center;'>";
  page += "<h1>CPS Monitoring and Control</h1>";

  page += "<h2>Temperature: ";
  page += String(temperature, 1);
  page += " &deg;C</h2>";

  page += "<h2>LED Status: ";
  page += (ledState ? "ON" : "OFF");
  page += "</h2>";

  page += "<p><a href='/on'><button style='padding:15px;'>LED ON</button></a></p>";
  page += "<p><a href='/off'><button style='padding:15px;'>LED OFF</button></a></p>";
  page += "<p><a href='/update'><button style='padding:15px;'>Update Temperature</button></a></p>";

  page += "</body></html>";

  server.send(200, "text/html", page);
}

void handleOn() {
  ledState = true;
  digitalWrite(ledPin, HIGH);
  handleRoot();
}

void handleOff() {
  ledState = false;
  digitalWrite(ledPin, LOW);
  handleRoot();
}

void handleUpdate() {
  temperature = random(250, 401) / 10.0;
  handleRoot();
}

void setup() {
  Serial.begin(9600);

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected!");
  Serial.print("Open this IP address: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/on", handleOn);
  server.on("/off", handleOff);
  server.on("/update", handleUpdate);

  server.begin();
  Serial.println("Web server started");
}

void loop() {
  server.handleClient();
}


// =====================================================
// PRACTICAL NO. 05
// SENDING SENSOR DATA TO CLOUD USING FIREBASE
// =====================================================

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <DHT.h>

const char* ssid = "nikhil";
const char* password = "12345678";

const char* firebaseURL =
  "https://iiot-77fe4-default-rtdb.firebaseio.com";

#define DHT_PIN D4
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi connected");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected");
    delay(5000);
    return;
  }

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("DHT11 reading failed");
    delay(5000);
    return;
  }

  String json = "{";
  json += "\"temperature\":" + String(temperature, 1) + ",";
  json += "\"humidity\":" + String(humidity, 1) + ",";
  json += "\"uptime_ms\":" + String(millis());
  json += "}";

  WiFiClientSecure client;
  client.setInsecure();
  HTTPClient https;
  String url = String(firebaseURL) + "/sensorData/readings.json";

  if (https.begin(client, url)) {
    https.addHeader("Content-Type", "application/json");

    int code = https.POST(json);

    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" C");

    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");

    Serial.print("Firebase HTTP response: ");
    Serial.println(code);

    if (code == HTTP_CODE_OK) {
      Serial.println("Data stored successfully");
      Serial.println(https.getString());
    } else {
      Serial.println(https.getString());
    }

    https.end();
  } else {
    Serial.println("Could not connect to Firebase");
  }

  delay(20000);
}
