#!/usr/bin/env python3
import socket
import struct
import time


class Ntp:
    def __init__(self, port=123):
        self.port = port
        self.unix_to_ntp_jump = 2208988800  # fast forward to the 90s

    def time(self):
        t = int(time.time())
        t += self.unix_to_ntp_jump
        binary_str = struct.pack("!I", t)
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
    ntp = Ntp(9123)
    ntp.serve()
