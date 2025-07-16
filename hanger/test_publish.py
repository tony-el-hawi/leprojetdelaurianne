import paho.mqtt.client as mqtt
import time

MQTT_BROKER = "10.42.0.1"
MQTT_TOPIC = "hanger_a085e3e834c8/leds"
FILENAME = "test_publish.txt"

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)

with open(FILENAME, "r") as f:
    for line in f:
        line = line.strip()
        if line:
            print(f"Publishing: {line}")
            client.publish(MQTT_TOPIC, line)
            time.sleep(3)  # attendre 1 seconde entre chaque envoi

client.disconnect()