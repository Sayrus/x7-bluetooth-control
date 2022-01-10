import bluetooth
import threading
from enum import IntEnum
from utils import packet_to_str

class X7Commands(IntEnum):
    ACK = 2
    HARDWARE_BUTTON_STATE = 38

class X7HardwareButtons(IntEnum):
    SBX = 1
    MUTE = 8

class X7BluetoothController():
    STARTBYTEID = 90
    COMM_CHANNEL_ID = 1

    def __init__(self, mac, nonblocking):
        self.mac = mac
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.connect((self.mac, X7BluetoothController.COMM_CHANNEL_ID))
        if nonblocking:
            self.socket.settimeout(0.1)
        t = threading.Thread(target = self.read_response)
        t.start()

    def read_response(self):
        try:
            while True:
                packet = self.socket.recv(1)
                if packet[0] != X7BluetoothController.STARTBYTEID:
                    print("Invalid start byte:", packet[0])
                    continue
                packet = self.socket.recv(2)
                packet_id = packet[0]
                packet_len = packet[1]
                data = self.socket.recv(packet_len)
                if packet_id == X7Commands.ACK:
                    print("Packet ACK:", packet_to_str(packet))

                if packet_id == X7Commands.HARDWARE_BUTTON_STATE:
                    is_get = data[0]
                    if is_get == 1 and packet_len == 5:
                        button_states = data[1] | data[2] << 8 | data[3] << 16 | data[4] << 24
                        print("STATES", bin(button_states))
                        for button in X7HardwareButtons:
                            print(button.name, not (button_states >> (button.value - 1) & 1))
        except bluetooth.btcommon.BluetoothError:
            pass


    def send_command(self, command_id, payload):
        payload_length = len(payload)
        b = [0] * (payload_length + 4)
        b[0] = X7BluetoothController.STARTBYTEID
        b[1] = command_id
        b[2] = payload_length
        b[3:] = payload
        print('Sending: %s', packet_to_str(b))
        self.socket.send(bytes(b))


class X7():
    def __init__(self, mac, cli_mode = False):
        self.bluetooth = X7BluetoothController(mac, cli_mode)

    def _set_hardware_button(self, button, status):
        self.bluetooth.send_command(X7Commands.HARDWARE_BUTTON_STATE, [0, button, status])

    def mute(self, enabled):
        self._set_hardware_button(X7HardwareButtons.MUTE, enabled)

    def sbx(self, enabled):
        self._set_hardware_button(X7HardwareButtons.SBX, enabled)
