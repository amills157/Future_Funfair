#!/usr/bin/env python

import time
import socket
import logging

from scapy.all import *
from scapy.layers.inet import *

from cryptography.fernet import Fernet

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

def spoof_udp_packet(src_ip, dst_ip,payload,dport):
	ip = IP(dst=dst_ip, src=src_ip)
	udp = UDP(sport=RandShort(),dport=dport)
	packet = ip/udp/payload
	send(packet, verbose=0)


def send_udp_packet(dst_ip,dport,message):

	keys=[
		b'cBTZG69d2hbquUFVu0SbXma6arGsqQIvWImXVsypc8M=',b'__0mtubykUb4p31WybrbFx2K4QhKMT7qum4epHLtifc=',
		b'IwVyF68VXj8QxTwg2zgz5vlIqmnxDQqt-fJp83RyCWY=',
		b'E7IdK3dkPurzdF1DmZdf2U6xbTE_l732MEpkJtgxWCE=',
		b'MDbRjMQtOreyqiG30APOdr6sFDvvsrBvReON4jRzZvM=',
		b'YSJxrzadcaO3piVLULdbeV8lCD-u7FgeGjGiDrmdYlk='
		]

	server_address = (dst_ip, dport)
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	if message == "encrypted":
		plaintext = "green"
		rand_key = random.randint(0,5)
		fernet = Fernet(keys[rand_key])
		message = fernet.encrypt(plaintext.encode())
		client_socket.sendto(message, server_address)
	else:
		client_socket.sendto(message.encode(), server_address)


def send_udp_packets(dst_ip,dport,message):
    while send_udp_packet.running:
        send_udp_packet(dst_ip,dport,message)
        time.sleep(5)
