#!/usr/bin/env python

import os
import sys
import time
import random
import string
import socket
import threading

from scapy.all import *
from random import getrandbits
from ipaddress import IPv4Address 

"""
def spoof_tcp_packets(src_ip,dest_ip,payload,sport,dport):
	# SYN
	ip = IP(src=src_ip, dst=dest_ip)
	SYN = TCP(sport=sport, dport=dport, flags='S', seq=1000)
	SYNACK = sr1(ip/SYN)

	# SYN-ACK
	ACK = TCP(sport=sport, dport=dport, flags='A', seq=SYNACK.ack + 1, ack=SYNACK.seq + 1)
	send(ip/ACK)
	
	#spoofed_packet = IP(src=src_ip, dst=dest_ip) / TCP(sport=sport, dport=dport, seq=ACK.ack + 1, ack=ACK.seq + 1) / payload
	#send(spoofed_packet)
"""

def send_tcp_packet(message):
    server_address = ('192.168.0.36', 8888)  # Replace with your MITM's IP address

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect(server_address)

        # Send the message
        client_socket.sendall(message.encode())

        # Receive a response from the server
        response = client_socket.recv(1024)
        print('Received response:', response.decode())

    except Exception as e:
        print('Error:', e)

    finally:
        # Close the socket
        client_socket.close()
        

def send_tcp_packets(sleep_time):
    while send_tcp_packet.running:
        message = "TURN LIGHT BLUE"
        send_tcp_packet(message)
        time.sleep(sleep_time)