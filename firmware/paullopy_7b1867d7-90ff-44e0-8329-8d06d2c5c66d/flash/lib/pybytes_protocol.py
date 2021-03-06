try:
    from pybytes_library import PybytesLibrary
except:
    from _pybytes_library import PybytesLibrary
try:
    from pybytes_constants import constants
except:
    from _pybytes_constants import constants
try:
    from terminal import Terminal
except:
    from _terminal import Terminal
try:
    from OTA import WiFiOTA
except:
    from _OTA import WiFiOTA
try:
    from flash_control_OTA import FCOTA
except:
    from _flash_control_OTA import FCOTA
try:
    from pybytes_debug import print_debug
except:
    from _pybytes_debug import print_debug

from machine import Pin
from machine import ADC
from machine import PWM
from machine import Timer
from machine import reset
from machine import WDT

import os
import sys
import _thread
import time
import socket
import struct
import machine
import binascii

class PybytesProtocol:
    def __init__(self, config, message_callback, pybytes_connection):
        self.__conf = config
        self.__thread_stack_size = 8192
        self.__device_id = config['device_id']
        self.__mqtt_download_topic = "d" + self.__device_id
        self.__mqtt_upload_topic = "u" + self.__device_id
        self.__mqtt_check_interval = 0.5
        self.__pybytes_connection = pybytes_connection
        self.__pybytes_library = PybytesLibrary(pybytes_connection=pybytes_connection, pybytes_protocol=self)
        self.__user_message_callback = message_callback
        self.__pins = {}
        self.__pin_modes = {}
        self.__custom_methods = {}
        self.__terminal_enabled = False
        self.__battery_level = -1
        self.__connectionAlarm = None
        self.__terminal = Terminal(self)
        self.__FCOTA = FCOTA()

    def start_Lora(self, pybytes_connection):
        print_debug(5, "This is PybytesProtocol.start_Lora()")
        self.__pybytes_connection = pybytes_connection
        self.__pybytes_library.set_network_type(constants.__NETWORK_TYPE_LORA)
        _thread.stack_size(self.__thread_stack_size)
        _thread.start_new_thread(self.__check_lora_messages, ())

    def start_MQTT(self, pybytes_connection, check_interval, networkType):
        print_debug(5, "This is PybytesProtocol.start_MQTT(check_interval={}, networkType={})".format(check_interval, networkType))
        self.__pybytes_connection = pybytes_connection
        self.__pybytes_library.set_network_type(networkType)
        self.__mqtt_check_interval = check_interval
        self.__start_recv_mqtt()

    def start_Sigfox(self, pybytes_connection):
        print_debug(5, "This is PybytesProtocol.start_Sigfox()")
        self.__pybytes_library.set_network_type(constants.__NETWORK_TYPE_SIGFOX)
        self.__pybytes_connection = pybytes_connection

    def __start_recv_mqtt(self):
        print_debug(5, "This is PybytesProtocol.__start_recv_mqtt()")
        self.__pybytes_connection.__connection.set_callback(self.__recv_mqtt)
        self.__pybytes_connection.__connection.subscribe(self.__mqtt_download_topic)
        print_debug(2, 'Using {} bytes as stack size'.format(self.__thread_stack_size))

        _thread.stack_size(self.__thread_stack_size)
        _thread.start_new_thread(self.__check_mqtt_message, ())
        self.__connectionAlarm = Timer.Alarm(self.__keep_connection, constants.__KEEP_ALIVE_PING_INTERVAL, periodic=True)

    def __wifi_or_lte_connection(self):
        return self.__pybytes_connection.__connection_status == constants.__CONNECTION_STATUS_CONNECTED_MQTT_WIFI or self.__pybytes_connection.__connection_status == constants.__CONNECTION_STATUS_CONNECTED_MQTT_LTE

    def __check_mqtt_message(self):
        print_debug(5, "This is PybytesProtocol.__check_mqtt_message()")
        while self.__wifi_or_lte_connection():
            try:
                self.__pybytes_connection.__connection.check_msg()
                time.sleep(self.__mqtt_check_interval)
            except Exception as ex:
                print("Error receiving MQTT. Ignore this message if you disconnected")
                print_debug(2, "Exception: {}".format(ex))
                sys.print_exception(ex)

    def __keep_connection(self, alarm):
        print_debug(5, "This is PybytesProtocol.__keep_connection(alarm={})".format(alarm))
        if self.__wifi_or_lte_connection():
            self.send_ping_message()

    def __check_lora_messages(self):
        print_debug(5, "This is PybytesProtocol.__check_lora_messages()")
        while(True):
            message = None
            with self.__pybytes_connection.lora_lock:
                try:
                    self.__pybytes_connection.__lora_socket.setblocking(False)
                    message = self.__pybytes_connection.__lora_socket.recv(256)
                except Exception as ex:
                    print_debug(5, "Exception in PybytesProtocol.__check_lora_messages: {}".format(ex))
            if (message):
                self.__process_recv_message(message)
            time.sleep(0.5)

    def __recv_mqtt(self, topic, message):
        print_debug(5, "This is PybytesProtocol.__recv_mqtt()")
        print_debug(2, 'Topic: {}\n Message: {}'.format(topic, message))
        self.__process_recv_message(message)

    def __process_recv_message(self, message):
        print_debug(5, "This is PybytesProtocol.__process_recv_message()")
        network_type, message_type, body = self.__pybytes_library.unpack_message(message)
        print_debug(2, 'Recv message of type{}'.format(message_type))
        print_debug(6, "network_type={}, message_type={}\nbody={}".format(network_type, message_type, body))

        if self.__user_message_callback is not None:
            if (message_type == constants.__TYPE_PING):
                self.send_ping_message()

            elif message_type == constants.__TYPE_PONG and self.__conf.get('connection_watchdog', True):
                print_debug(1,'message type pong received, feeding watchdog...')
                self.__pybytes_connection.__wifi_lte_watchdog.feed()

            elif (message_type == constants.__TYPE_INFO):
                self.send_info_message()

            elif (message_type == constants.__TYPE_NETWORK_INFO):
                self.send_network_info_message()

            elif (message_type == constants.__TYPE_SCAN_INFO):
                self.__send_message(self.__pybytes_library.pack_scan_info_message(self.__pybytes_connection.lora))

            elif (message_type == constants.__TYPE_BATTERY_INFO):
                self.send_battery_info()

            elif (message_type == constants.__TYPE_OTA):
                ota = WiFiOTA(self.__conf['wifi']['ssid'], self.__conf['wifi']['password'],
                              self.__conf['ota_server']['domain'], self.__conf['ota_server']['port'])

                if (self.__pybytes_connection.__connection_status == constants.__CONNECTION_STATUS_DISCONNECTED):
                    print('Connecting to WiFi')
                    ota.connect()

                print("Performing OTA")
                result = ota.update()
                self.send_ota_response(result)
                time.sleep(1.5)
                if (result == 2):
                    # Reboot the device to run the new decode
                    machine.reset()

            elif (message_type == constants.__TYPE_FCOTA):
                print_debug(2, 'receiving FCOTA request')
                if (self.__pybytes_connection.__connection_status == constants.__CONNECTION_STATUS_DISCONNECTED):
                    print('Not connected, Re-Connecting ...')
                    ota.connect()

                command = body[0]
                if (command == constants.__FCOTA_COMMAND_HIERARCHY_ACQUISITION):
                    self.send_fcota_ping('acquiring hierarchy...')
                    hierarchy = self.__FCOTA.get_flash_hierarchy()
                    self.send_fcota_hierarchy(hierarchy)

                elif (command == constants.__FCOTA_COMMAND_FILE_ACQUISITION):
                    path = body[1:len(body)].decode()
                    if (path[len(path)-2:len(path)] == '.py'):
                        self.send_fcota_ping('acquiring file...')
                    content = self.__FCOTA.get_file_content(path)
                    size = self.__FCOTA.get_file_size(path)
                    self.send_fcota_file(content, path, size)

                elif (command == constants.__FCOTA_COMMAND_FILE_UPDATE):
                    bodyString = body[1:len(body)].decode()
                    splittedBody = bodyString.split(',')
                    if (len(splittedBody) >= 2):
                        path = splittedBody[0]
                        print(path[len(path)-7:len(path)])
                        if (path[len(path)-7:len(path)] != '.pymakr'):
                            self.send_fcota_ping('updating file...')
                        newContent = bodyString[len(path)+1:len(body)]
                        if (self.__FCOTA.update_file_content(path, newContent) == True):
                            size = self.__FCOTA.get_file_size(path)
                            self.send_fcota_file(newContent, path, size)
                            if (path[len(path)-7:len(path)] != '.pymakr'):
                                time.sleep(2)
                                self.send_fcota_ping('board restarting...')
                                time.sleep(2)
                                reset()
                            else:
                                self.send_fcota_ping('pymakr archive updated!')
                        else:
                            self.send_fcota_ping('file update failed!')
                    else:
                        self.send_fcota_ping("file update failed!")

                elif (command == constants.__FCOTA_PING):
                    self.send_fcota_ping('')

                elif (command == constants.__FCOTA_COMMAND_FILE_DELETE):
                    self.send_fcota_ping('deleting file...')
                    path = body[1:len(body)].decode()
                    success = self.__FCOTA.delete_file(path)
                    if (success == True):
                        self.send_fcota_ping('file deleted!')
                        self.send_fcota_hierarchy(self.__FCOTA.get_flash_hierarchy())
                    else:
                        self.send_fcota_ping('deletion failed!')

                else:
                    print("Unknown FCOTA command received")

            elif (message_type == constants.__TYPE_PYBYTES):
                command = body[0]
                pin_number = body[1]
                value = 0

                if (len(body) > 3):
                    value = body[2] << 8 | body[3]

                if (command == constants.__COMMAND_PIN_MODE):
                    pass

                elif (command == constants.__COMMAND_DIGITAL_READ):
                    pin_mode = None
                    try:
                        pin_mode = self.__pin_modes[pin_number]
                    except Exception as ex:
                        pin_mode = Pin.PULL_UP

                    self.send_pybytes_digital_value(False, pin_number, pin_mode)

                elif (command == constants.__COMMAND_DIGITAL_WRITE):
                    if (not pin_number in self.__pins):
                        self.__configure_digital_pin(pin_number, Pin.OUT, None)
                    pin = self.__pins[pin_number]
                    pin(value)

                elif (command == constants.__COMMAND_ANALOG_READ):
                    self.send_pybytes_analog_value(False, pin_number)

                elif (command == constants.__COMMAND_ANALOG_WRITE):
                    if (not pin_number in self.__pins):
                        self.__configure_pwm_pin(pin_number)
                    pin = self.__pins[pin_number]
                    pin.duty_cycle(value * 100)

                elif (command == constants.__COMMAND_CUSTOM_METHOD):
                    if (pin_number == constants.__TERMINAL_PIN and self.__terminal_enabled):
                        self.__terminal.message_sent_from_pybytes_start()
                        terminal_command = body[2: len(body)]
                        terminal_command = terminal_command.decode("utf-8")

                        try:
                            out = eval(terminal_command)
                            if out is not None:
                                print(repr(out))
                            else:
                                print('\n')
                        except:
                            try:
                                exec(terminal_command)
                                print('\n')
                            except Exception as e:
                                print('Exception:\n  ' + repr(e))
                        self.__terminal.message_sent_from_pybytes_end()
                        return

                    if (self.__custom_methods[pin_number] is not None):
                        parameters = {}

                        for i in range(2, len(body), 3):
                            value = body[i: i + 2]
                            parameters[i / 3] = (value[0] << 8) | value[1]

                        method_return = self.__custom_methods[pin_number](parameters)

                        if (method_return is not None and len(method_return) > 0):
                            self.send_pybytes_custom_method_values(pin_number, method_return)

                    else:
                        print("WARNING: Trying to write to an unregistered Virtual Pin")

        else:
            try:
                self.__user_message_callback(message)
            except Exception as ex:
                print(ex)

    def __configure_digital_pin(self, pin_number, pin_mode, pull_mode):
        # TODO: Add a check for WiPy 1.0
        self.__pins[pin_number] = Pin("P" + str(pin_number), mode = pin_mode, pull=pull_mode)

    def __configure_analog_pin(self, pin_number):
        # TODO: Add a check for WiPy 1.0
        adc = ADC(bits=12)
        self.__pins[pin_number] = adc.channel(pin="P" + str(pin_number))

    def __configure_pwm_pin(self, pin_number):
        # TODO: Add a check for WiPy 1.0
        _PWMMap = {0: (0, 0),
                   1: (0, 1),
                   2: (0, 2),
                   3: (0, 3),
                   4: (0, 4),
                   8: (0, 5),
                   9: (0, 6),
                   10: (0, 7),
                   11: (1, 0),
                   12: (1, 1),
                   19: (1, 2),
                   20: (1, 3),
                   21: (1, 4),
                   22: (1, 5),
                   23: (1, 6)}
        pwm = PWM(_PWMMap[pin_number][0], frequency=5000)
        self.__pins[pin_number] = pwm.channel(_PWMMap[pin_number][1], pin="P" + str(pin_number),
                                              duty_cycle=0)

    def __send_message(self, message, topic=None):
        try:
            finalTopic = self.__mqtt_upload_topic if topic is None else self.__mqtt_upload_topic + "/" + topic

            print_debug(2, "Sending message:[{}] with topic:[{}] and finalTopic: [{}]".format(binascii.hexlify(message), topic, finalTopic))
            if self.__wifi_or_lte_connection():
                self.__pybytes_connection.__connection.publish(finalTopic, message)
            elif (self.__pybytes_connection.__connection_status == constants.__CONNECTION_STATUS_CONNECTED_LORA):
                with self.__pybytes_connection.lora_lock:
                    self.__pybytes_connection.__lora_socket.setblocking(True)
                    self.__pybytes_connection.__lora_socket.send(message)
                    self.__pybytes_connection.__lora_socket.setblocking(False)
            elif (self.__pybytes_connection.__connection_status == constants.__CONNECTION_STATUS_CONNECTED_SIGFOX):
                if (len(message) > 12):
                    print ("WARNING: Message not sent, Sigfox only supports 12 Bytes messages")
                    return
                self.__pybytes_connection.__sigfox_socket.send(message)

            else:
                print_debug(2, "Warning: Sending without a connection")
                pass
        except Exception as ex:
            print(ex)

    def send_user_message(self, message_type, body):
        self.__send_message(self.__pybytes_library.pack_user_message(message_type, body))

    def send_ping_message(self):
        self.__send_message(self.__pybytes_library.pack_ping_message())

    def send_info_message(self):
        self.__send_message(self.__pybytes_library.pack_info_message())

    def send_network_info_message(self):
        self.__send_message(self.__pybytes_library.pack_network_info_message())

    def send_scan_info_message(self, lora):
        print('WARNING! send_scan_info_message is deprecated and should be called only from Pybytes.')

    def send_battery_info(self):
        self.__send_message(self.__pybytes_library.pack_battery_info(self.__battery_level))

    def send_ota_response(self, result):
        print_debug(2, 'Sending OTA result back {}'.format(result))
        self.__send_message(self.__pybytes_library.pack_ota_message(result), 'ota')

    def send_fcota_hierarchy(self, hierarchy):
        print_debug(2, 'Sending FCOTA hierarchy back')
        self.__send_message(self.__pybytes_library.pack_fcota_hierarchy_message(hierarchy), 'fcota')

    def send_fcota_file(self, content, path, size):
        print_debug(2, 'Sending FCOTA file back')
        self.__send_message(self.__pybytes_library.pack_fcota_file_message(content, path, size), 'fcota')

    def send_fcota_ping(self, activity):
        print_debug(2, 'Sending FCOTA ping back: {}'.format(activity))
        self.__send_message(self.__pybytes_library.pack_fcota_ping_message(activity), 'fcota')

    def send_pybytes_digital_value(self, pin_number, pull_mode):
        if (not pin_number in self.__pins):
            self.__configure_digital_pin(pin_number, Pin.IN, pull_mode)
        pin = self.__pins[pin_number]
        self.send_pybytes_custom_method_values(pin_number, [pin()])

    def send_pybytes_analog_value(self, pin_number):
        if (not pin_number in self.__pins):
            self.__configure_analog_pin(pin_number)
        pin = self.__pins[pin_number]
        self.send_pybytes_custom_method_values(pin_number, [pin()])


    def send_pybytes_custom_method_values(self, method_id, parameters):
        print(method_id, parameters)
        if(isinstance(parameters[0], int)):
            values = bytearray(struct.pack(">i", parameters[0]))
            values.append(constants.__INTEGER)
            self.__send_pybytes_message_variable(constants.__COMMAND_CUSTOM_METHOD, method_id, values)
        elif(isinstance(parameters[0], float)):
            values = bytearray(struct.pack("<f", parameters[0]))
            values.append(constants.__FLOAT)
            self.__send_pybytes_message_variable(constants.__COMMAND_CUSTOM_METHOD, method_id, values)
        elif(isinstance(parameters[0], tuple) or isinstance(parameters[0], list)):
            stringTuple = '[' + ', '.join(map(str, parameters[0])) + ']' + str(constants.__STRING)
            values = stringTuple.encode("hex")
            self.__send_pybytes_message_variable(constants.__COMMAND_CUSTOM_METHOD, method_id, values)
        else:
            values = (parameters[0] + str(constants.__STRING)).encode("hex")
            self.__send_pybytes_message_variable(constants.__COMMAND_CUSTOM_METHOD, method_id, values)


    def add_custom_method(self, method_id, method):
        self.__custom_methods[method_id] = method

    def __send_terminal_message(self, data):
        self.__send_pybytes_message_variable(constants.__COMMAND_CUSTOM_METHOD, constants.__TERMINAL_PIN, data)

    def enable_terminal(self):
        self.__terminal_enabled = True
        os.dupterm(self.__terminal)

    def __send_pybytes_message(self, command, pin_number, value):
        self.__send_message(self.__pybytes_library.pack_pybytes_message(command, pin_number, value))

    def __send_pybytes_message_variable(self, command, pin_number, parameters):
        self.__send_message(self.__pybytes_library.pack_pybytes_message_variable(command, pin_number, parameters))

    def set_battery_level(self, battery_level):
        self.__battery_level = battery_level
