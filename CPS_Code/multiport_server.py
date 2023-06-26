#!/usr/bin/env python
import os
import re
import time
import socket
import threading

from buildhat import Motor
from buildhat import Matrix
from cryptography.fernet import Fernet

# define buildhats
motorA = Motor('A')
motorB = Motor('B')
matrixC = Matrix('C')

# define motors speeds
def MotorA():
    motorA.set_default_speed(30)
    motorA.start()

def MotorB():
    motorB.set_default_speed(30)
    motorB.start()

def MotorA_Fast():
    motorA.set_default_speed(60)
    motorA.start()

def MotorB_Fast():
    motorB.set_default_speed(60)
    motorB.start()

# Define port numbers
# Kit side 1 (Motor A)
DOS_PORT_A = 4444
MITM_PORT_A = 5555
INJECTION_PORT_A = 6666

# Kit side 2 (Motor B)
DOS_PORT_B = 7777
MITM_PORT_B = 8888
INJECTION_PORT_B = 9999

C2_PORT = 4242

# Define the ports to listen on.
udp_ports = [DOS_PORT_A, MITM_PORT_A, INJECTION_PORT_A, DOS_PORT_B, MITM_PORT_B, INJECTION_PORT_B]

kit_a_junk_flag = False
kit_b_junk_flag = False

# TCP Client used by the C2 server.
def handle_tcp_client(client_socket, port):
    while True:
        request = client_socket.recv(1024)
        if not request:
            break
        decoded_request = request.decode()
        print(f"Traffic received on port {port}: {decoded_request}")

        if port == 4242:
            motor_thread = threading.Thread(target=c2_server, args=(decoded_request,))
            motor_thread.start()
            client_socket.send(b"ACK!\n")
    client_socket.close()


# Define a function to setup the TCP server.
# Used by the C2 server.
def setup_tcp_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)  # Maximum backlog of connections.
    print(f"Listening on port {port}")
    while True:
        client, addr = server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")
        # Create a new thread to handle this specific connection.
        client_handler = threading.Thread(target=handle_tcp_client, args=(client, port))
        client_handler.start()


# Define the main C2 functionality.
# This will listen on port 4242 for commands from the C2 server.
# If the IP address is in the list of attacker IPs, drop the connection.
def c2_server(decoded_request):
    ip_addr = re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", decoded_request[-20:]).group(0)
    attacker_ips = ["27.19.88.195", "192.168.99.201", "136.163.89.10", 
                    "27.19.88.196", "192.168.99.202", "136.163.89.11"]
    print(ip_addr)
    if ip_addr in attacker_ips:
        os.system(f"iptables -A INPUT -s {ip_addr} -j DROP")

# Define the main generic UDP server. This will spawn a handler for
# the specific service this port is handling. EG DOS, MITM, Injection.
def setup_udp_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("0.0.0.0", port))
    print(f"Listening on port {port}")
    while True:
        message, address = server_socket.recvfrom(1024)
        if len(message) == 100:
            keys=[
                 b'cBTZG69d2hbquUFVu0SbXma6arGsqQIvWImXVsypc8M=',
                 b'__0mtubykUb4p31WybrbFx2K4QhKMT7qum4epHLtifc=',
                 b'IwVyF68VXj8QxTwg2zgz5vlIqmnxDQqt-fJp83RyCWY=',
                 b'E7IdK3dkPurzdF1DmZdf2U6xbTE_l732MEpkJtgxWCE=',
                 b'MDbRjMQtOreyqiG30APOdr6sFDvvsrBvReON4jRzZvM=',
                 b'YSJxrzadcaO3piVLULdbeV8lCD-u7FgeGjGiDrmdYlk='
            ]

            for key in keys:
                try:
                    fernet = Fernet(key)
                    decMessage = fernet.decrypt(message).decode()
                    injection_server(decMessage, port)
                except Exception:
                    continue
        else:
                print(message.decode())

                if port == DOS_PORT_A or port == DOS_PORT_B:
                    dos_server(message.decode(), port)
                else:
		            # Injection or MITM both run the same code.
                    injection_server(message.decode(), port)


# Define a function to run the motor code.
# This function is called by the thread that handles the client connection.
# The port is passed in so we can determine which motor to run.
def run_motor_code(traffic, port):
    # If the port is 4444, 5555 or 6666, run the motor code for motor A.
    # else run the code for motor B.
    if port == 4444 or port == 5555 or port == 6666:
        kit = "A"
    else:
        kit = "B"

    print(f"Kit {kit} - Starting motor code for traffic: {traffic}")
    if traffic == 'slow':
        # Runs idle script
        if kit == "A":
            MotorA()
        else:
            MotorB()

        print('Idle script executed')

    elif traffic == 'fastest':
        # Runs injection script
        if kit == "A":
            MotorA_Fast()
        else:
            MotorB_Fast()

        print(f'Kit {kit} - Injection executed')

    elif traffic == 'green':
        # Mitm script - At the moment, only one matrix on port C is available 
        if kit == "A":
            MotorA()
        else:
            MotorB()
           
        matrixC.clear(("green", 10))
        print(f'Kit {kit} - MITM executed')

    elif traffic == 'red':
        # Mitm script - At the moment, only one matrix on port C is available        
        matrixC.clear(("red", 10))

        if kit == "A":
            MotorA_Fast()
        else:
            MotorB_Fast()
           
        print(f'Kit {kit} - MITM executed')

    elif traffic == 'stopping':
        # Force stop the motors
        print(f"Kit {kit} - Stopping motors")
        matrixC.clear()
        if kit == "A":
            motorA.stop()
        else:
            motorB.stop()

    elif traffic == 'flush':
        # Flush iptables for all ports - can be used between sessions to clean up
        print("Flushing iptables")
        os.system("iptables -F")


# Denial of service code. This is called by the main UDP server.
# It will spawn a thread to run the motor code which can be
# stop, slow, medium or fastest..
# 
# If we receive a DOS message that contains a junk payload, use some smoke and mirrors
# to force stop the motor code.
#
# Some janky threading code is used to force stop the motor code, so every now and then, the
# standard idle code will be partially run. This is to make the attack more realistic.
#
def dos_server(decoded_request, port):
    accepted_parameters = ["stop", "slow", "medium", "fastest"]

    if port == DOS_PORT_A:
        kit = "A"
    else:
        kit = "B"

    # Create a new thread to run the motor code with the decoded request.
    print(f"Kit {kit} - DOS code received: {decoded_request}")

    # If the decoded request is not in the accepted parameters, this is a
    # DOS (junk) packet. Create a thread to run the junk code.
    if decoded_request not in accepted_parameters:
        junk_thread = threading.Thread(target=set_junk_flag, args=(port,))
        junk_thread.start()
    else:
        # Process the regular idle traffic
        motor_thread = threading.Thread(target=run_motor_code, args=(decoded_request, port,))
        motor_thread.start()


# Some more some and mirrors code to force stop the motor code.
def set_junk_flag(port):
    global kit_a_junk_flag
    global kit_b_junk_flag

    if port == DOS_PORT_A:
        kit = "A"
    else:
        kit = "B"

    print(f"Kit {kit} - Junk code!")

    if kit == "A":
        kit_a_junk_flag = True
        motorA.stop()
    else:
        kit_b_junk_flag = True
        motorB.stop()

    time.sleep(5)
    print(f"Kit {kit} - Stopping motor code...")
    if kit == "A":
        kit_a_junk_flag = False
    else:
        kit_b_junk_flag = False


# Injection code. This is called by the main UDP server.
# Just process the payload command and run the motor code.
def injection_server(decoded_request, port):
        motor_thread = threading.Thread(target=run_motor_code, args=(decoded_request, port,))
        motor_thread.start()


# Create and start a thread for each server.
for port in udp_ports:
    udp_server_thread = threading.Thread(target=setup_udp_server, args=(port,))
    udp_server_thread.start()

tcp_server_thread = threading.Thread(target=setup_tcp_server, args=(C2_PORT,))
tcp_server_thread.start()
