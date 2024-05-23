<h1 align="center"><img src="https://cdn.pixabay.com/photo/2021/03/05/22/44/dinosaur-6072475_960_720.png" width="224px"/><br/>
  Mosquitto Roboto Steamo Docko
</h1>
<p align="center">The project is a small ESP32 wheeled robot remote controlled using an app on a SteamDeck</p>

# 📃 Table of content

- [🎮 Gameplay](#-gameplay)
- [🚀 Getting started](#-getting-started)
    - [Start the MQTT broker](#start-the-mqtt-broker)
    - [Start the robot](#start-the-robot)
    - [Start the SteamDeck app](#start-the-steamdeck-app)
- [👨 Authors](#-authors)

## 🎮 Gameplau

The game is simple, you have to control the robot using the SteamDeck's joysticks. The left joystick controls the robot's speed and direction, while the right joystick controls the robot's turret.

Here is the video of the gameplay:
https://github.com/Bricklou/remote-controlled-robot/assets/62793491/5a905e7d-b1fd-4edf-bab3-463ce0a7801a

## 🚀 Getting started

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

### Start the robot

To start the robot, you need to install Thonny and the ESP32 MicroPython firmware. Then, open the `robot.py` file and run it on the ESP32.

### Start the SteamDeck app

- Switch to Desktop Mode on SteamDeck.
- Install linuxbrew.
- Install rust using linuxbrew and compile the project.
- Copy kontroller.vdf into /home/deck/.local/share/Steam/controller_config (create the folder if it doesn't exist), rename it to game_actions_480.vdf.
- Run kontroller on SteamDeck. This should open a new window, but your input can't be captured now. Close the window.
- Start steam client on the Desktop Mode. In your library, you should find a game called Spacewar. Edit its input mapping.
- Run the remote control app again, you should get the input you want.
- Run also mosquitto on another computer, and connect to the same broker as the robot.

## 👨 Authors

<p align="center"> We are a group of three creators.</p>

<table align="center">
  <tr>
    <th><img src="https://avatars.githubusercontent.com/u/15181236?v=4" width="115"><br><strong>@Bricklou</strong></th>
    <th><img  src="https://avatars.githubusercontent.com/u/62793491?v=4?size=115" width="115"><br><strong>@jvondermarck</strong></th>
    <th><img  src="https://avatars.githubusercontent.com/u/94604758?v=4" width="115"><br><strong>@Aisamet</strong></th>
  </tr>
  <tr align="center">
    <td><b>@dylan-power</b></td>
    <td><b>@jvondermarck</b> </td>
    <td><b>@NoahAldahan</b></td>
  </tr>
</table>
