# remote-controlled-robot

Small ESP32 wheeled robot remote controlled using an app on a SteamDeck

## Run for development

### Start the MQTT broker

First, install docker and run the containers with:

```sh
docker compose up
```

This will boot both MQTTX and Mosquitto.

Then, connect to MQTTX at http://127.0.0.1:9002, and create a new connection with the following information:

- Name: Mosquitto
- Host: `ws://`, `127.0.0.1`
- Port: `9001`
- Username: `mosquitto`
- Password: `mosquitto`
- SSL: no

Finally, subscribe a new topic : `robot/#`. Now the MQTT broker is ready.
