from umqttsimple import MQTTClient
import ubinascii
import machine
import gc


class Mqtt:
    """Class used for work with MQTT."""

    def __init__(self) -> None:
        """
        Constructor of the class.

        :param: None
        :return: None
        """
        self.__client_id = ubinascii.hexlify(machine.unique_id())
        self.__topic_of_received_message = "Null"
        self.__read_data = "Null"

        self.__ip_address = None
        self.__topic_sub = []
        self.__client = None

        self.__mqtt_object = None

    def __sub_cb(self, topic: bytes, msg: bytes) -> None:
        """
        Callback for receiving messages.

        :param topic: bytes
        :param msg: bytes

        Parameters:
        - first parameter is the topic on which was received message.
        - second parameter is the message that we received.
        """
        self.__read_data = str(msg, 'UTF-8').strip()
        self.__topic_of_received_message = str(topic, 'UTF-8').strip()
        del topic
        del msg
        gc.collect()

    def set_mqtt_broker_ip_address(self, ip_address: str) -> None:
        """
        This function will set the IP address of the MQTT broker

        :param ip_address: str
        :return: None

        Parameters:
        - The first parameter is the IP adress on which is running
        the MQTT broker.
        """
        self.__ip_address = str(ip_address)
        del ip_address
        gc.collect()

    def set_credentials(self, username: str, password: str) -> None:
        """
        This function will set the MQTT credentials of the MQTT broker

        :param username: str
        :param password: str
        :return: None
        """
        self.__username = username
        self.__password = password
        del username
        del password
        gc.collect()

    def add_topic_sub(self, topic: str) -> None:
        """
        This function will add topics to which we will subscribe.

        :param topic: str
        :return: None

        Parameters:
        - The parameter to this function is the name of the topic to
        which we want to subscribe.
        """
        self.__topic_sub.append(str(topic))
        del topic
        gc.collect()

    def connect_and_subscribe(self) -> int:
        """
        Function used for connecting to the mqtt broker.

        :param: None
        :return: int

        Return:
        - 0 if everything was set properly.
        - 1 if there are no topics to which we want to listen to.
        - 2 if we dont set the IP address of the MQTT broker
        - 3 if we failed to connect to the MQTT broker.
        """
        if len(self.__topic_sub) == 0:
            print("""at first you must set some topic to which we will subscribe""")
            print('Mqtt - connect_and_subscribe')
            return 1

        if self.__ip_address is None:
            print("""at first you must set the IP address of MQTT broker""")
            print('Mqtt - connect_and_subscribe')
            return 2

        try:
            self.__client = MQTTClient(
                self.__client_id, self.__ip_address, user=self.__username, password=self.__password)
            self.__client.set_callback(self.__sub_cb)
            self.__client.connect()
        except OSError:
            print("""I failed to connect to the MQTT broker""")
            print('Mqtt - connect_and_subscribe')
            self.__client = None
            return 3

        for i in range(0, len(self.__topic_sub)):
            self.__client.subscribe(self.__topic_sub[i])
        print('connected to the ' + str(self.__ip_address) + ' MQTT broker')
        print('listenning on topics: ')
        for i in range(0, len(self.__topic_sub)):
            print(str(i+1) + '. ' + str(self.__topic_sub[i]))
        print()
        del i
        gc.collect()
        return 0

    def check_incomming_messages(self) -> list:
        """
        This function check whether we have some incomming message.

        :param: None
        :return: list

        Return:
        - This function return list.
            * first element
            - If the first element of the list is 0 we have received.
            some message.
            - If it is 1 we dont receive any message.
            - If it is 2 we have not connected to the MQTT broker.

            * second element
            - if we have received some message the second parameter is set
            to the topic on which we have received the message.

            * third element
            - if we have received some message the third parameter is set
            to the massage that we have received.
        """
        if self.__client == None:
            print('At first you must connect to the MQTT broker')
            print('Mqtt - check_incomming_messages')
            return [2]
        self.__client.check_msg()
        if self.__read_data != 'Null':
            pom = [0, self.__topic_of_received_message,
                   self.__read_data]
            self.__read_data = 'Null'
            return pom
        else:
            return [1]

    def send_message(self, topic: str, message: str) -> int:
        """
        This function send message to the selected topic.

        :param topic: str
        :param message: str
        :return: int

        Parameters:
        - the first parameter is the topic to which we want to send
        the message.
        - the second parameter is the massage that we want to send.

        Return:
        - 0 if the message was succesfully send.
        - 1 if we have not connected to the MQTT broker.
        """

        if self.__client == None:
            print('At first you must connect to the MQTT broker')
            print('Mqtt - send_message')
            del topic
            del message
            gc.collect()
            return 1

        self.__client.publish(str(topic), str(message))
        del topic
        del message
        gc.collect()
        return 0

# import network
# from time import sleep
#
# # starting connecting to WiFi network
#
# ssid = '***'
# password = '***'
#
# station = network.WLAN(network.STA_IF)
#
# station.active(True)
# if station.isconnected() == False:
#     station.connect(ssid, password)
#
# while station.isconnected() == False:
#   pass
#
# print('Connection successful')
# print(station.ifconfig())
# print()
#
# # ending connecting to WiFi network
#
# # starting work with node_red
#
# MQTT_SERVER_IP_ADDRESS = '*.*.*.*'
#
# # we can create as much sub topics as we want to
# MQTT_SERVER_SUB_TOPIC_1 = '***'
# MQTT_SERVER_SUB_TOPIC_2 = '***'
#
# # we can create as much pub topics as we want to
# MQTT_SERVER_PUB_TOPIC_1 = '***'
# MQTT_SERVER_PUB_TOPIC_2 = '***'
#
# mqtt_object = Mqtt()
#
# mqtt_object.set_mqtt_broker_ip_address(MQTT_SERVER_IP_ADDRESS)
# mqtt_object.add_topic_sub(MQTT_SERVER_SUB_TOPIC_1)
# mqtt_object.add_topic_sub(MQTT_SERVER_SUB_TOPIC_2)
#
# while mqtt_object.connect_and_subscribe() != 0:
#     pass
#     sleep(1)
#
# variable1 = 1
# variable2 = 50000
#
# while True:
#     pom = mqtt_object.check_incomming_messages()
#     if pom[0] == 0:
#         print('received message topic: ' + pom[1])
#         print('received message: ' + pom[2])
#         print()
#
#     mqtt_object.send_message(MQTT_SERVER_PUB_TOPIC_1, variable1)
#     mqtt_object.send_message(MQTT_SERVER_PUB_TOPIC_2, variable2)
#
#     variable1 = variable1 + 1
#     variable2 = variable2 - 1
#
#     sleep(5)
