import time
import sys
import re
from utils import (
    load_config, clear_screen, save_config, print_header, print_menu,
    print_info, print_error, print_success, print_warning,
    show_loading, bold, green, red, yellow, cyan, Colors
)
from adb_utils import get_packages_by_prefix
from delta_control import full_process
from monitor import monitor

def extract_private_code(link):
    match = re.search(r'[?&]code=([^&]+)', link)
    if match:
        return match.group(1)
    return None

def input_private_server(config):
    link = input("[+] Server Link: ").strip()
    code = extract_private_code(link)
    if code:
        config["private_code"] = code
        config["place_id"] = ""  # prioritas private
        save_config(config)
        print_success(f"Private server code: {code}")
    else:
        print_error("[!] Not Valid.")
        clear_screen(delay=1)

def input_place_id(config):
    print("\n[X] Choose :")
    print("1. Fish IT")
    print("2. Grow A Garden 2")
    print("3. Grow A Garden")
    print("4. Other Games (input manual)")
    choice = input("root@wonxd1337~ : ").strip()
    place_id = ""
    if choice == "1":
        place_id = "121864768012064"
    elif choice == "2":
        place_id = "97598239454123"
    elif choice == "3":
        place_id = "126884695634066"
    elif choice == "4":
        place_id = input("[+] Enter Place ID: ").strip()
        if not place_id.isdigit():
            print_error("[!] Place ID must be number.")
            clear_screen(delay=1)
            return
    else:
        print_error("[FAIL] Not Valid.")
        clear_screen(delay=1)
        return
    config["place_id"] = place_id
    config["private_code"] = ""  
    save_config(config)
    print_success(f"[+] Place ID saved: {place_id}")
    clear_screen(delay=2)

def input_packages(config):
    print("\n[X] Choose:")
    print("1. By Name (separated with commas)")
    print("2. By Prefix")
    method = input("root@wonxd1337~ : ").strip()
    
    if method == "1":
        print("\nExample format: com.roblox.clienu, com.roblox.clientv, com.roblox.clientw")
        print("Separate multiple packages with commas")
        raw = input("Name Package : ").strip()
        if raw:
            packages = [p.strip() for p in raw.split(",") if p.strip()]
            config["packages"] = packages
            save_config(config)
            print_success(f"{len(packages)} package(s) saved.")
            clear_screen(delay=2)
        else:
            print_error("[FAIL] Enter Package First.")
            clear_screen(delay=1)
            
    elif method == "2":
        prefix = input("Prefix Package (com.roblox): ").strip()
        if not prefix:
            print_error("[!] Prefix cannot empty.")
            time.sleep(1)
            clear_screen()
            return
            
        print_info(f"Searching for packages with prefix: {prefix}...")
        found = get_packages_by_prefix(prefix)
        
        if not found:
            print_error(f"[FAIL] No packages found with prefix '{prefix}' installed.")
            time.sleep(2)
            clear_screen()
            return
            
        print_info(f"[OK] Found {len(found)} package(s):")
        for i, pkg in enumerate(found, 1):
            clean_pkg = pkg.strip()
            print(f"  {i}. {clean_pkg}")
        
        print("")  
        sys.stdout.flush() 
        
        confirm = input("[?] Use All Package? (y/n): ").strip().lower()
        if confirm == "y":
            config["packages"] = found
            save_config(config)
            print_success(f"{len(found)} package(s) saved.")
        else:
            print_info("[!] Canceled.")
            clear_screen(delay=1)
    else:
        print_error("[!] Not Valid.")
        time.sleep(1)
        clear_screen()

def input_bot_token(config):
    token = input("Bot Token [OPTIONAL]: ").strip()
    channel = input("Channel ID [OPTIONAL]: ").strip()
    config["bot_token"] = token
    config["channel_id"] = channel
    save_config(config)
    if token and channel:
        print_success("[OK] Bot token and Channel ID saved.")
        clear_screen(delay=1)
    else:
        print_info("Bot Token or Channel ID Empty [AUTO KEY OFF].")
        clear_screen(delay=1)

def start_tools(config):
    if not config.get("packages"):
        print_error("[!] Enter Package First.")
        clear_screen(delay=1)
        return
    if not config.get("private_code") and not config.get("place_id"):
        print_error("[!] Choose Private Server or Place ID First.")
        clear_screen(delay=1)
        return

    print_info("Starting...")
    config = load_config()
    packages = config["packages"]
    private_code = config.get("private_code", "")
    place_id = config.get("place_id", "")
    bot_token = config.get("bot_token", "")
    channel_id = config.get("channel_id", "")

    print_info(f"Package(s): {', '.join(packages)}")
    if private_code:
        print_info(f"[MODE] Private Server (code: {private_code})")
    else:
        print_info(f"[MODE] Public Game (Place ID: {place_id})")
    
    if bot_token and channel_id:
        print_info("[!] Bot Token Found. AUTO KEY ON.")
    else:
        print_info("[!] Bot Token / Channel ID Not Found. AUTO KEY OFF.")

    time.sleep(2)
    try:
        monitor(packages, place_id, bot_token, channel_id, private_code)
    except KeyboardInterrupt:
        print_warning("\n[!] STOPPED, Back To Menu.")
        return

def main():
    config = load_config()
    while True:
        print_header()
        print_menu()
        choice = input("root@wonxd1337~ : ").strip()
        if choice == "1":
            start_tools(config)
        elif choice == "2":
            input_private_server(config)
            config = load_config()
        elif choice == "3":
            input_place_id(config)
            config = load_config()
        elif choice == "4":
            input_packages(config)
            config = load_config()
        elif choice == "5":
            input_bot_token(config)
            config = load_config()
        elif choice == "6":
            print_info("Exit.")
            break
        else:
            print_error("[!] Not Valid, Press Enter To Back.")
            input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting.")
        sys.exit(0)
