# RDBye
Proof-of-concept tool which enables shutting down servers exposing RDP to the internet which allow remote shutdown

Please use this tool within an exclusive VM to not interfer with the automatic mouse movements and/or getting your private data screenshotted.

# Installation
```
git clone https://github.com/NexusFuzzy/RDBye
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt
sudo apt install wmctrl scrot python3-tk python3-dev rdesktop python3-pil gnome-screenshot
```

# Usage
```
+-+-+-+-+-+
|R|D|B|y|e|
+-+-+-+-+-+

usage: RDBye [-h] [-s SHODAN] [-i IP_ADDRESS] [-r]

Script to exploit RDP to shut down remote hosts

options:
  -h, --help            show this help message and exit
  -s SHODAN, --shodan SHODAN
                        JSON file exported from shodan.io
  -i IP_ADDRESS, --ip_address IP_ADDRESS
                        Single IP address as target
  -r, --redline         Downloaddd Redline Command & Control servers from Tria.ge (API key required)
```
# Remarks
rdbye relies on a screen resolution of 1690x920 to find the correct buttons. Please ensure that you are using this screen resolution within your virtual machine

# Known issues
If you get the error 
`Xlib.error.DisplayConnectionError: Can't connect to display ":0": b'Authorization required, but no authorization protocol specified\n'`

please run the following command:

`xhost +SI:localuser:$(whoami)`

# Get results from Shodan
![image](https://github.com/user-attachments/assets/1c6d78a0-46bb-4658-9f8b-35b837b9b285)

