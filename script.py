import bluetooth
import struct

STARTBYTEID = 90

MUTE_HARDWARE_BUTTON = 8

def swap_endian(number):
    return struct.unpack("<h",struct.pack(">h", number))[0]

def handle_acknowledge(packet):
    print("Packet ACK:", packet)

def read_response(sock):
    packet = sock.recv(100) # Arbitrary size for now
    if packet[0] != STARTBYTEID:
        print("Invalid start byte:", packet[0])
    packet_id = packet[1]
    packet = packet[2:]
    if packet_id == 2:
        return handle_acknowledge(packet)
    print(packet[1])


def send_command(sock, command_id, payload):
    payload_length = len(payload)
    b = [0] * (payload_length + 4)
    b[0] = STARTBYTEID
    b[1] = command_id
    b[2] = payload_length
    b[3:] = payload
    print(bytes(b).hex())
    sock.send(bytes(b))

    # Temporary, should not be here
    read_response(sock)

def set_mute(sock, mute):
    send_command(sock, 38, [0, MUTE_HARDWARE_BUTTON, mute])

# Min -52
# Max 0
def set_volume(sock, index, level):
    binary = struct.pack("<h", level * 256)
    send_command(sock, 35, [0, index] + [c for c in binary])

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect(('00:02:3c:55:5F:37', 1))

packet1 = bytes.fromhex('5a29050000000080') # Speaker (Unknown MULTI config)
packet2 = bytes.fromhex('5a29050001000000') # Headset
packet3 = bytes.fromhex('5a23040000ffff') # Volume

#send_command(sock, 36, [0, 1])
#send_command(sock, 38, [0,8,0])
#set_mute(sock, 1)
import time
import math

def mapping(i):
    # Random values, algorithm is more complex and depends on values returned by
    # the DAC
    mini = -52
    maxi = 0
    f = 0.5
    step = 1
    if i == 0:
        return mini
    if i == 100:
        return maxi
    return math.floor((((i * f) + mini) + maxi) / step) * step

mapping = [mapping(i) for i in range(101)]
print(mapping)

set_volume(sock,0,mapping[50])

#for i in range(50, 101, 2):
#    print(i)
#    set_volume(sock,0,mapping[i])
#    time.sleep(1)
#sock.send(packet2)
#read_response(sock)
#sock.send(packet2)
#print(sock.recv(100))

sock.close()
print("Closed")
