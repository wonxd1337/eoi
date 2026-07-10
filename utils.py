import json
import os
import sys
import time

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    WHITE = '\033[97m'
    MAGENTA = '\033[95m'

def bold(text):
    return f"{Colors.BOLD}{text}{Colors.END}"

def green(text):
    return f"{Colors.GREEN}{text}{Colors.END}"

def red(text):
    return f"{Colors.RED}{text}{Colors.END}"

def yellow(text):
    return f"{Colors.YELLOW}{text}{Colors.END}"

def blue(text):
    return f"{Colors.BLUE}{text}{Colors.END}"

def cyan(text):
    return f"{Colors.CYAN}{text}{Colors.END}"

def magenta(text):
    return f"{Colors.MAGENTA}{text}{Colors.END}"

def get_status_color(status):
    if status == "Online":
        return green(status)
    elif status == "Offline":
        return red(status)
    else:
        return status

def get_ascii_art():
    return f"""
{Colors.CYAN}{Colors.BOLD}
   ██╗    ██╗ ██████╗ ███╗   ██╗██╗  ██╗██████╗ 
   ██║    ██║██╔═══██╗████╗  ██║╚██╗██╔╝██╔══██╗
   ██║ █╗ ██║██║   ██║██╔██╗ ██║ ╚███╔╝ ██║  ██║
   ██║███╗██║██║   ██║██║╚██╗██║ ██╔██╗ ██║  ██║
   ╚███╔███╔╝╚██████╔╝██║ ╚████║██╔╝ ██╗██████╔╝
    ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝ 
{Colors.END}                                                 
"""

CONFIG_FILE = "config.json"

def load_config():
    default = {
        "private_code": "",
        "place_id": "",
        "packages": [],
        "bot_token": "",
        "channel_id": "" # Diperbaiki
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            for key in default:
                if key not in data:
                    data[key] = default[key]
            return data
        except:
            return default
    else:
        save_config(default)
        return default

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def clear_screen(delay=0):
    if delay > 0:
        time.sleep(delay)
    os.system('clear' if os.name == 'posix' else 'cls')

def show_loading(message, duration=1.5):
    chars = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f'\r{Colors.CYAN}{chars[i % len(chars)]}{Colors.END} {message}')
        sys.stdout.flush()
        i += 1
        time.sleep(0.1) # Diperbaiki dari 2.0 agar animasi berjalan
    sys.stdout.write('\r' + ' ' * 60 + '\r')
    sys.stdout.flush()

def print_header():
    clear_screen()
    print(get_ascii_art())

def print_menu():
    print("\n[1] Start Rejoin Tools")
    print("[2] Input Private Server Link")
    print("[3] Input Place ID")
    print("[4] Input Packages")
    print("[5] Input Bot Token (optional)")
    print("[6] Exit")
    print("")

def print_info(msg):
    print(f"{Colors.CYAN}[*]{Colors.END} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}[+]{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[-]{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[!]{Colors.END} {msg}")
