def packet_to_str(packet, fn=int):
    return [fn(c) for c in packet]
