import re
import time
from adb_utils import dump_ui, tap

def find(text):
    xml = dump_ui()
    if not xml:
        return None
    p = r'<node.*?(?:text|content-desc)="([^"]*{}[^"]*?)".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'.format(re.escape(text))
    m = re.search(p, xml, re.I | re.DOTALL)
    if m:
        x1, y1, x2, y2 = map(int, m.groups()[1:])
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    return None

def find_edit():
    xml = dump_ui()
    if not xml:
        return None
    m = re.search(r'<node.*?class="android\.widget\.EditText".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml, re.DOTALL)
    if m:
        x1, y1, x2, y2 = map(int, m.groups())
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    return None

def find_btn(text):
    return find(text)

def get_username_from_ui():
    xml = dump_ui()
    if not xml:
        return None
    pattern = r'<node.*?text="([^"]*@[^"]*?)".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
    match = re.search(pattern, xml, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def is_delta_visible():
    xml = dump_ui()
    if not xml:
        return False
    if "ZETSU DELTA" in xml or "LITE" in xml:
        return True
    if "Receive Key" in xml or "Get Key" in xml:
        return True
    if "KEY_example" in xml:
        return True
    if 'text="Continue"' in xml:
        return True
    return False

def is_in_game():
    game_elements = ["Settings", "Inventory", "FPS", "Team", "Players", "Leaderboard"]
    for elem in game_elements:
        if find(elem):
            return True
    return False

def is_in_lobby():
    lobby_elements = ["Play", "Join Game", "Teleport", "Game", "Servers"]
    for elem in lobby_elements:
        if find(elem):
            return True
    return False

def is_key_requested():
    xml = dump_ui()
    if not xml:
        return False
    if re.search(r'(?:text|content-desc)="(?:Get|Receive)\s*Key"', xml, re.I):
        return True
    has_edit = re.search(r'class="android\.widget\.EditText"', xml)
    has_continue = re.search(r'(?:text|content-desc)="Continue"', xml, re.I)
    if has_edit and has_continue:
        return True
    return False