#!/usr/bin/env python3
import socket
import struct
import time


def get_time():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(b'GIMMIETIME', ("localhost", 9123))
    data, addr = s.recvfrom(1024)
    if data:
        print(f"Got response from {addr[0]}:{addr[1]}")
        t = struct.unpack("!I", data)[0]
        print("data:", t)
        t -= 2208988800  # jump back to the 70s
        return time.ctime(t).replace("  "," ")


if __name__ == "__main__":
    print(get_time())
