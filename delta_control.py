import time
from adb_utils import (
    start_app, tap, input_text, press_keycode, get_clipboard, set_clipboard,
    run, run_root, wait_app, is_running, is_foreground, get_foreground_app,
    dump_ui, get_username
)
from ui_automator import find, find_edit, find_btn, get_username_from_ui, is_in_game, is_in_lobby, is_delta_visible, is_key_requested
from key_fetcher import get_key
from utils import bold, green, red, yellow, cyan

def wait_delta(pkg, timeout=30):
    for _ in range(timeout // 2):
        if is_delta_visible():
            return True
        time.sleep(2)
    return False

def get_shortlink(pkg):
    btn = find("Receive Key") or find("Get Key")
    if not btn:
        print(f"  {yellow('[*]')} Tombol 'Receive/Get Key' tidak ditemukan.")
        return None
    print(f"  {cyan('[*]')} Tombol key ditemukan, mengetuk...")
    tap(btn[0], btn[1])
    time.sleep(2)
    s = get_clipboard()
    if s and s.startswith("http"):
        print(f"  {green('[+]')} Shortlink berhasil diambil: {s}")
        return s
    else:
        print(f"  {red('[-]')} Clipboard tidak berisi shortlink valid (isi: {s})")
        return None

def input_key(pkg, key):
    e = find_edit()
    if not e:
        print(f"  {red('[-]')} EditText tidak ditemukan untuk memasukkan key.")
        return False
    tap(e[0], e[1])
    time.sleep(1.5)
    input_text(key)
    time.sleep(1.5)
    c = find_btn("Continue")
    if c:
        tap(c[0], c[1])
        print(f"  {green('[+]')} Key berhasil dimasukkan dan tombol Continue ditekan.")
        return True
    else:
        print(f"  {red('[-]')} Tombol Continue tidak ditemukan setelah input key.")
        return False

def get_status(pkg):
    if not is_running(pkg):
        return "Offline"
    return "Online"

# get_username sekarang diambil dari adb_utils.get_username

def full_process(pkg, place_id, bot_token, channel_id, private_code=None):
    print(f"\n{bold('[*]')} Processing {bold(pkg)}...")
    print(f"  {cyan('[*]')} Openning...")
    start_app(pkg)
    time.sleep(3)
    wait_app(pkg, 10)
    username = get_username(pkg)
    if username:
        print(f"  {green('[+]')} Username: {bold(username)}")
    else:
        username = "Unknown"
        print(f"  {yellow('[*]')} Username not detected 'Unknown'.")

    # Bangun URI
    if private_code:
        uri = f"https://www.roblox.com/share?code={private_code}&type=Server"
        print(f"  {cyan('[*]')} Mode Private Server (code: {private_code})")
    else:
        uri = f"roblox://placeId={place_id}"
        print(f"  {cyan('[*]')} Mode Public Game (Place ID: {place_id})")

    run(f"am start -a android.intent.action.VIEW -d '{uri}' {pkg}")
    time.sleep(5)

    # Hanya lakukan deteksi Delta jika AUTO KEY aktif
    if bot_token and channel_id:
        if not wait_delta(pkg, 30):
            print(f"  {red('[-]')} Delta tidak muncul untuk {pkg}")
            return username

        if not is_key_requested():
            print(f"  {green('[+]')} Delta tidak meminta key (sudah aktif atau di game).")
            return username

        print(f"  {yellow('[*]')} Delta meminta key, mencoba mengambil shortlink...")
        short = get_shortlink(pkg)
        if not short:
            print(f"  {red('[-]')} Gagal mendapatkan shortlink, proses key dilewati.")
            return username

        print(f"  {cyan('[*]')} Mengambil key dari Discord...")
        key = get_key(bot_token, channel_id, short)
        if not key:
            print(f"  {red('[-]')} Gagal mengambil key dari Discord.")
            return username
        print(f"  {cyan('[*]')} Key berhasil diambil: {key[:10]}...")
        if not input_key(pkg, key):
            print(f"  {red('[-]')} Gagal memasukkan key.")
        else:
            print(f"  {green('[+]')} Proses key selesai.")
    else:
        print(f"  {yellow('[*]')} AUTO KEY Off, Skipping Delta")

    time.sleep(2)
    return username