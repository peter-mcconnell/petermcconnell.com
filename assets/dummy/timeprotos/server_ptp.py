#!/usr/bin/env python3
import socket
import struct
import time


class Ptp:
    def __init__(self, port=123):
        self.port = port

    def time(self):
        t = time.time()
        binary_str = struct.pack("!d", t)
        return binary_str

    def serve(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as err:
            print("Failed to create socket")
            raise err
        s.bind(("", self.port))
        print("listening ...")
        while True:
            data, addr = s.recvfrom(1024)
            if data:
                print(f"Got data from {addr[0]}:{addr[1]}")
                s.sendto(self.time(), addr)


if __name__ == "__main__":
    ntp = Ptp(9123)
    ntp.serve()
