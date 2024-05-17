from machine import Pin, PWM
from libs.u_mqtt import Mqtt
import network
import select
import time
import math

# Motors pins
pin_5 = Pin(5, Pin.OUT, value=1)
pin_22 = Pin(22, Pin.OUT, value=1)
# Led pin
led = Pin(25, Pin.OUT, value=0)

# Motors PWM
left_forward = PWM(Pin(15), freq=500, duty=0)
left_backward = PWM(Pin(2), freq=500, duty=0)
right_forward = PWM(Pin(0), freq=500, duty=0)
right_backward = PWM(Pin(4), freq=500, duty=0)

# Wifi connection
nic = network.WLAN(network.STA_IF)
nic.active(True)

nic.connect("Xiaomi_BACD", "6pfyULAAgmpjvyoTwd")

# While the wifi isn't ready, wait
while nic.isconnected() == False:
    pass

print("Status: ", nic.status(), nic.ifconfig())

# Start MQTT server
MQTT_SERVER_IP_ADDRESS = "192.168.1.43"
MQTT_SERVER_SUB_TOPIC = "robot"
MQTT_CREDENTIALS = {"username": "mosquitto", "password": "mosquitto"}

mqtt_object = Mqtt()
mqtt_object.set_mqtt_broker_ip_address(MQTT_SERVER_IP_ADDRESS)
mqtt_object.set_credentials(
    MQTT_CREDENTIALS["username"], MQTT_CREDENTIALS["password"])
mqtt_object.add_topic_sub(MQTT_SERVER_SUB_TOPIC)


while mqtt_object.connect_and_subscribe() != 0:
    pass
    time.sleep(1)

MAX_SPEED = 400


def joy_to_diff_drive(joy_x, joy_y):
    left = joy_x * math.sqrt(2.0)/2.0 + joy_y * math.sqrt(2.0)/2.0
    right = -joy_x * math.sqrt(2.0)/2.0 + joy_y * math.sqrt(2.0)/2.0
    return [left, right]


def move(x: float, y: float):
    [left, right] = joy_to_diff_drive(x, -y)

    motor_left_power = int(round(left / 1.0 * MAX_SPEED))
    motor_right_power = int(round(right / 1.0 * MAX_SPEED))

    # Ensure the motor power does not exceed max_power
    motor_left_power = max(-MAX_SPEED, min(MAX_SPEED, motor_left_power))
    motor_right_power = max(-MAX_SPEED, min(MAX_SPEED, motor_right_power))

    power_motor(left_forward, left_backward, motor_left_power)
    power_motor(right_forward, right_backward, motor_right_power)


def power_motor(motor_forward, motor_backward, value):
    if value < 0:
        motor_forward.duty(0)
        motor_backward.duty(abs(value))
    else:
        motor_forward.duty(value)
        motor_backward.duty(0)


# Forever
while True:
    pom = mqtt_object.check_incomming_messages()

    if pom[0] != 0 or pom[1] != "robot":
        time.sleep_ms(1)
        continue

    line = pom[2]
    line = str(line).split(" ")
    if len(line) < 1:
        time.sleep_ms(1)
        continue

    action = line[0]

    if action == "move":
        if len(line) != 3:
            time.sleep_ms(1)
            continue
        vel_x = 0
        vel_y = 0

        try:
            vel_x = float(line[1])
            vel_y = float(line[2])
        except:
            pass

        move(vel_x, vel_y)
    elif action == "led":
        if led.value():
            led.off()
        else:
            led.on()
