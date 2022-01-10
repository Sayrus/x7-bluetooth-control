import bluetooth
import threading
from enum import IntEnum
from utils import packet_to_str


class X7Commands(IntEnum):
    ACK = 2
    HARDWARE_BUTTON_STATE = 38
    SPEAKER_CONFIGURATION = 41


# Speaker Configuration
class X7SpeakerConfiguration(IntEnum):
    # This is actually Interger.MIN_VALUE in Java. This allows changing output
    # to speakers without actually knowing the current SpeakerConfiguration
    TOGGLE_TO_SPEAKER = -(2 ** 31)
    HEADPHONES = 1
    STEREO_2_0 = 2
    MULTI_CHANNEL_5_1 = 3


# Properties for SpeakerConfiguration
# class X7SpeakerAdvancedConfiguration(IntEnum):
#     STEREO_2_0 = 1.0
#     MULTI_CHANNEL_2_1 = 2.0
#     MULTI_CHANNEL_3_0 = 3.0
#     MULTI_CHANNEL_3_1 = 4.0
#     MULTI_CHANNEL_4_0 = 5.0
#     MULTI_CHANNEL_4_1 = 6.0
#     MULTI_CHANNEL_5_0 = 7.0
#     MULTI_CHANNEL_5_1 = 8.0

# FIXME: We should ask for hardware capabilities first
class X7HardwareButtons(IntEnum):
    SBX = 1
    MUTE = 8
    CRYSTAL_VOICE = 17

    # Not available on X7
    VOICE = 4
    MICROPHONE = 5
    PHONE = 7
    NOISE_REDUCTION = 9

    # Back Buttons (BP = Bluetooth Player?), Not Available on X7
    BP_PLAY = 10
    BP_PREV_TRACK = 11
    BP_NEXT_TRACK = 12
    BP_PREV_FOLDER = 13
    BP_NEXT_FOLDER = 14
    BP_PLAY_RECORDING = 15
    BP_RECORD_RECORDING = 16

    # magic methods for argparse compatibility
    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    @staticmethod
    def argparse(s):
        try:
            return X7HardwareButtons[s.upper()]
        except KeyError:
            return s


class X7BluetoothController:
    STARTBYTEID = 90
    COMM_CHANNEL_ID = 1

    def __init__(self, mac, nonblocking):
        self.mac = mac
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.connect((self.mac, X7BluetoothController.COMM_CHANNEL_ID))
        if nonblocking:
            self.socket.settimeout(0.2)
        t = threading.Thread(target=self.read_response)
        t.start()

    def _read_packet(self):
        packet = self.socket.recv(1)
        if packet[0] != X7BluetoothController.STARTBYTEID:
            print("Invalid start byte:", packet[0])
            return
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
                print("BUTTON_STATES MASK", bin(button_states))
                for button in X7HardwareButtons:
                    print(button.name, bool(button_states >> (button.value - 1) & 1))

    def read_response(self):
        try:
            while True:
                self._read_packet()
        except bluetooth.btcommon.BluetoothError:
            # Used to exit CLI mode
            pass

    def send_command(self, command_id, payload):
        payload_length = len(payload)
        b = [0] * (payload_length + 4)
        b[0] = X7BluetoothController.STARTBYTEID
        b[1] = command_id
        b[2] = payload_length
        b[3:] = payload
        print("Sending: %s", packet_to_str(b))
        self.socket.send(bytes(b))


class X7:
    def __init__(self, mac, cli_mode=False):
        self.bluetooth = X7BluetoothController(mac, cli_mode)

    def _set_hardware_button(self, button, status):
        self.bluetooth.send_command(
            X7Commands.HARDWARE_BUTTON_STATE, [0, button, status]
        )

    def mute(self, enabled):
        self._set_hardware_button(X7HardwareButtons.MUTE, enabled)

    def sbx(self, enabled):
        self._set_hardware_button(X7HardwareButtons.SBX, enabled)

    def set_audio_output(self, output):
        if output == "headphones":
            config = X7SpeakerConfiguration.HEADPHONES
        else:
            config = X7SpeakerConfiguration.TOGGLE_TO_SPEAKER
        payload = config.to_bytes(4, byteorder="little", signed=True)
        self.bluetooth.send_command(
            X7Commands.SPEAKER_CONFIGURATION, [0] + list(payload)
        )
