#include <WiFi.h>
#include <esp_wifi.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"
#define WLAN_SSID "Dressing-de-Laurianne"
#define WLAN_PASS "285047013c72"
#define AIO_SERVER "10.42.0.1"
#define AIO_SERVERPORT 1883  // use 8883 for SSL
#define AIO_USERNAME ""
#define AIO_KEY ""


char mac[25];
char topic[40];
WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, AIO_SERVER, AIO_SERVERPORT, AIO_USERNAME, AIO_KEY);
Adafruit_MQTT_Publish* leds_pub;
Adafruit_MQTT_Subscribe* leds_sub;
void MQTT_connect();

void readMacAddress(char *mac) {
  uint8_t baseMac[6];
  esp_err_t ret = esp_wifi_get_mac(WIFI_IF_STA, baseMac);
  if (ret == ESP_OK) {
    sprintf(mac, "%02x%02x%02x%02x%02x%02x",
            baseMac[0], baseMac[1], baseMac[2],
            baseMac[3], baseMac[4], baseMac[5]);
  } else {
    strcpy(mac, "unknown");
  }
}

void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println(F("MQTT Dressing de Laurianne"));
  // Connect to WiFi access point.
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WLAN_SSID);
  WiFi.begin(WLAN_SSID, WLAN_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // Lire l'adresse MAC et créer le topic unique
  readMacAddress(mac);
  sprintf(topic, "hanger_%s/leds", mac);
  Serial.print(F("\nCreate topic "));
  Serial.print(topic);
  Serial.print("...");

  // Créer les objets MQTT dynamiquement avec le topic unique
  leds_pub = new Adafruit_MQTT_Publish(&mqtt, topic);
  leds_sub = new Adafruit_MQTT_Subscribe(&mqtt, topic);
  mqtt.subscribe(leds_sub);

  MQTT_connect();
  if (!leds_pub->publish("Create")) {
    Serial.println(F("Failed"));
  } else {
    Serial.println(F("OK!"));
  }
}

uint32_t x = 0;
void loop() {
  MQTT_connect();
  Adafruit_MQTT_Subscribe *subscription;
  while ((subscription = mqtt.readSubscription(5000))) {
    if (subscription == leds_sub) {
    Serial.print(F("Got: "));
    Serial.println((char *)leds_sub->lastread);

    // Parse the received string into an array of colors
    const char* payload = (char*)leds_sub->lastread;
    const int maxColors = 10; // adjust as needed
    int colors[maxColors][3];
    int colorCount = 0;

    const char* ptr = payload;
    while (*ptr && colorCount < maxColors) {
      int r, g, b;
      if (sscanf(ptr, " (%d,%d,%d)", &r, &g, &b) == 3 ||
        sscanf(ptr, "(%d,%d,%d)", &r, &g, &b) == 3) {
        colors[colorCount][0] = r;
        colors[colorCount][1] = g;
        colors[colorCount][2] = b;
        colorCount++;
      }
      // Move ptr to next '(' or end
      ptr = strchr(ptr, ')');
      if (ptr) ptr++;
      while (*ptr && *ptr != '(') ptr++;
    }

    // Debug: print parsed colors
    for (int i = 0; i < colorCount; ++i) {
      Serial.print("Color ");
      Serial.print(i);
      Serial.print(": (");
      Serial.print(colors[i][0]);
      Serial.print(",");
      Serial.print(colors[i][1]);
      Serial.print(",");
      Serial.print(colors[i][2]);
      Serial.println(")");
    }
    }
  }
}
// Function to connect and reconnect as necessary to the MQTT server.
// Should be called in the loop function and it will take care if connecting.
void MQTT_connect() {
  int8_t ret;
  // Stop if already connected.
  if (mqtt.connected()) {
    return;
  }
  Serial.print("Connecting to MQTT... ");
  uint8_t retries = 3;
  while ((ret = mqtt.connect()) != 0) {  // connect will return 0 for connected
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println("Retrying MQTT connection in 5 seconds...");
    mqtt.disconnect();
    delay(5000);  // wait 5 seconds
    retries--;
    if (retries == 0) {
      // basically die and wait for WDT to reset me
      while (1)
        ;
    }
  }
  Serial.println("MQTT Connected!");
}   