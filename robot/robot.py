from machine import Pin, PWM
import socket
import network
import select
import time
import math
import wifi_codes

# Motors pins
pin_5 = Pin(5, Pin.OUT, value=1)
pin_22 = Pin(22, Pin.OUT, value=1)
# Led pin
led = Pin(25, Pin.OUT, value=0)

# Motors PWM
left_forward = PWM(Pin(15), freq = 500, duty = 0)
left_backward = PWM(Pin(2), freq = 500, duty = 0)
right_forward = PWM(Pin(0), freq = 500, duty = 0)
right_backward = PWM(Pin(4), freq = 500, duty = 0)

# Wifi connection
nic = network.WLAN(network.STA_IF)
nic.active(True)

nic.connect(wifi_codes.SSID, wifi_codes.PASS)

# While the wifi isn't ready, wait
while nic.isconnected() == False:
    pass

print("Status: ", nic.status(), nic.ifconfig())

# Start a TCP server on port 4835
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 4835))
s.listen()

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

def read_line(sock):
    buffer = ""
    while True:
        data = sock.recv(1024)
        if data:
            buffer += data.decode("utf-8")
            if "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                yield line
        else:
            break

# Forever
while True:
    print("Waiting for client")
    conn, address = s.accept()
    print("client connected")
    
    while True:
        try:
            ready_to_read, ready_to_write, in_error = select.select([conn,], [conn,], [], 5)
        except select.error:
            conn.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
            conn.close()
            # connection error event here, maybe reconnect
            print('connection error')
            break

        data = ""
        line = ""
        while True:
            buf = conn.recv(256)
            if buf:
                data += buf.decode("utf-8")
                if "\n" in data:
                    line, data = data.split("\n", 1)
                    break
            else:
                time.sleep_ms(1)
                line = ""

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
    
    conn.close()

