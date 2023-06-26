# Future Funfair - CPS Code
### File Structure

This folder contains all the python code for either running or attacking the CPS itself. 

### attack_client.py

This code is loaded onto the student laptop and is used to run attacks against the target Pi server. 

This is a simple CLI prompt script with various options that provide simple and guided use. 

When first running the script it will ask you to select either Kit A or Kit B. Once a selection has been made all attacks and further commands will target that kit (and associated ports).

The main screen itself will look like this:

```
Please select an attack:
1==DoS
2==Injection
3==MitM
4==Stop Rides
5==Flush
```

1 - 3 are attacks. 4 will send a stop signal to clear any instructions sent to the target motor or the LED matrix. 5 will flush the iptables rules on the Pi server, allowing attacks to be re-run. 

#### DoS

This attack will impact the motors of the target ride and stop it spinning. It will flood the target system with junk packets from a spoofed IP address. To resolve this, the students will need to find the attacker IP and then “Enable the Wireless shield” which will block the attacker (via the UI).

#### Code Injection

This attack will impact the motors of the target ride to make it go faster. During the attack packets will be sent telling the ride to run at ‘fastest’  from a spoofed IP address (this is our code injection). To resolve this, the students will need to find the attacker IP and then “Enable the Firewall” which will block the attacker (via the UI).

#### MitM

MitM attack will target the LED matrix and change the colours, it will also cause the target ride to start spinning faster. During the attack traffic is no longer going to the Pi server, but it being “intercepted” instead someone is sending the command ‘red’. Our attacker is a spoofed IP address and the actual attack itself is all handled within the code. To resolve this, the students will need to find the attacker IP and then “Enable the bump-in-the-wire device” which will block the attacker and enable encryption (via the UI). 

### multiport_server.py

This code is designed to be loaded on the Raspberry Pi which has the Build HAT and is controlling the various LEGO rides. 

The code itself should be loaded as a systemd service (and is by default on the provided .img file).

This will run a server that listens on the following ports:

* 4444 - Kit A (DoS server)
* 5555 - Kit A (Code Injection server)
* 6666 - Kit A (MitM server)

* 7777 - Kit B (DoS server)
* 8888 - Kit B (Code Injection server)
* 9999 - Kit B (MitM server)

* 4242 - C2 server

Ports 4444 - 9999 are all `udp` and port 4242 is `tcp`

Each server is designed to run 2x motors (A or B) and 1x LED matrix. As such functionality is split between 2 "kits". With attacks targeting either Kit A or Kit B. This allows 1x Pi server to facilitate 2x groups. 

The LED matrix is only part of 1 attack (MitM) and so order of attacks and demonstration of the MitM attack needs to be carefully co-ordinated between those running the attacks to avoid collision. 

## tcp_client.py

A simple tcp server that is run in a thread - This is only ever run on port `4242` and is used to handle C2 commands outside of attacks - For example blocking attacker IPs.

## udp_client.py

A simple udp server that is run in a thread - This is run on all listed ports except `4242` and is used to handle the different attack scenarios as covered above. 
