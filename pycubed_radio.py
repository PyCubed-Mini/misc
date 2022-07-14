"""
CircuitPython driver for PyCubed satellite board radio
PyCubed Mini mainboard-v02 for Pocketqube Mission
* Author(s): Max Holliday, Yashika Batra
"""
import pycubed
from os import stat


def create_packets(c_size, send_buffer, filename):
    """
    split a file into packets given packet size, buffer size, and the filename
    """

    # number of packets is the size of the file / packet size
    num_packets = int(stat(filename)[6] / c_size)

    # open the file
    with open(filename, "rb") as f:
        # for each packet
        for i in range(num_packets + 1):
            # move the cursor to the end of i * packet size,
            # add to buffer
            f.seek(i * c_size)
            f.readinto(send_buffer)

            # return bytes; yield keyword returns without destroying
            # states of local vars
            yield bytes([i, 0x45, num_packets])


def send_file(filename):
    """
    downlink a file packet by packet
    """
    # define some base case c_size and send_buffer
    c_size = 1
    send_buffer = bytearray()

    for packet in create_packets(c_size, send_buffer, filename):
        pycubed.send(packet)
