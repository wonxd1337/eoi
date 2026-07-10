import time
import sys
import os
import contextlib
import curses
from adb_utils import is_running, get_username, is_foreground
from delta_control import full_process, get_status
from utils import (
    bold, green, red, yellow, blue, cyan, get_status_color,
    clear_screen, print_header, print_info, print_error, print_success, print_warning,
    load_config, Colors
)

last_status = {}
last_username = {}
table_dirty = True

def monitor_curses(stdscr, packages, place_id, bot_token, channel_id, private_code,
                   initial_status, initial_username, start_time, interval=2):
    """Fungsi utama untuk tampilan curses (dioptimalkan untuk Termux)."""
    # Sembunyikan kursor dan nonaktifkan echo
    curses.curs_set(0)
    stdscr.nodelay(1)  # agar getch tidak blocking
    stdscr.clear()
    
    # Cek dukungan warna
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Online
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Offline
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Unknown

    # Salin status dan username
    status = initial_status.copy()
    username_map = initial_username.copy()
    
    # Timer untuk update otomatis
    last_update = time.time()

    # Loop utama
    while True:
        # Baca input keyboard (non-blocking)
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q') or key == 27:  # 27 = ESC
            break

        # Update setiap interval detik
        current_time = time.time()
        if current_time - last_update >= interval:
            last_update = current_time
            
            # Perbarui status dan username untuk setiap package
            changed = False
            for pkg in packages:
                new_status = get_status(pkg)
                if new_status != status.get(pkg):
                    status[pkg] = new_status
                    changed = True
                    if new_status == "Offline":
                        # Restart package dengan menonaktifkan output cetakan
                        with open(os.devnull, 'w') as devnull:
                            with contextlib.redirect_stdout(devnull):
                                uname = full_process(pkg, place_id, bot_token, channel_id, private_code)
                        if uname and uname != "Unknown":
                            username_map[pkg] = uname
                        status[pkg] = get_status(pkg)
                        changed = True

                new_uname = get_username(pkg)
                if new_uname and new_uname != username_map.get(pkg):
                    username_map[pkg] = new_uname
                    changed = True

        # Gambar ulang layar (setiap loop, bukan hanya saat berubah)
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # Header
        header = f"{'#':<3} {'Username':<20} {'Time':<12} {'Status':<10}"
        try:
            stdscr.addstr(0, 0, header[:w-1], curses.A_BOLD)
            stdscr.addstr(1, 0, "=" * min(55, w-1))
        except:
            pass

        # Waktu elapsed
        elapsed = int(time.time() - start_time)
        hh = elapsed // 3600
        mm = (elapsed % 3600) // 60
        ss = elapsed % 60
        time_str = f"{hh}h{mm:02d}m{ss:02d}s"

        # Isi tabel (dengan batasan baris)
        max_rows = min(len(packages), h - 5)
        for i in range(max_rows):
            pkg = packages[i]
            username = username_map.get(pkg, f"Account {i+1}")
            stat = status.get(pkg, "Unknown")
            
            # Warna status
            if stat == "Online":
                color = curses.color_pair(1) if curses.has_colors() else 0
            elif stat == "Offline":
                color = curses.color_pair(2) if curses.has_colors() else 0
            else:
                color = curses.color_pair(3) if curses.has_colors() else 0

            display_username = username[:20] if len(username) > 20 else username
            line = f"{i+1:<3} {display_username:<20} {time_str:<12}"
            try:
                stdscr.addstr(i+2, 0, line[:w-1])
                # Tampilkan status dengan warna
                status_pos = len(line)
                status_text = f" {stat}"
                stdscr.addstr(i+2, status_pos, status_text[:w-status_pos-1], color)
            except:
                pass

        # Footer
        try:
            footer_y = min(len(packages) + 3, h - 2)
            stdscr.addstr(footer_y, 0, "=" * min(55, w-1))
            stdscr.addstr(footer_y + 1, 0, "Tekan 'q' atau ESC untuk kembali")
        except:
            pass

        stdscr.refresh()
        time.sleep(0.1)  # sedikit jeda agar CPU tidak overload

def monitor(packages, place_id, bot_token, channel_id, private_code=None, interval=2):
    """Fungsi utama yang dipanggil dari main.py (dioptimalkan untuk Termux)."""
    start_time = time.time()
    status = {}
    username_map = {}

    print_info("Initializing monitoring...")
    
    # Inisialisasi status awal
    for i, pkg in enumerate(packages):
        status[pkg] = "Unknown"
        uname = get_username(pkg)
        if uname:
            username_map[pkg] = uname
        else:
            username_map[pkg] = f"Account {i+1}"

    # ---- PROSES AWAL SEQUENTIAL ----
    print_info("Starting all packages sequentially...")
    for i, pkg in enumerate(packages):
        print(f"  {cyan('[*]')} Starting {pkg}..")
        uname = full_process(pkg, place_id, bot_token, channel_id, private_code)
        if uname and uname != "Unknown":
            username_map[pkg] = uname
        status[pkg] = get_status(pkg)
        time.sleep(1)

    # Tampilkan tabel awal (print biasa) sebelum masuk curses
    print_info("Monitoring dimulai. Tekan 'q' atau ESC untuk berhenti.")
    print_info(f"Interval update: {interval} detik")
    time.sleep(1)

    # Jalankan mode monitoring dengan curses
    try:
        curses.wrapper(monitor_curses, packages, place_id, bot_token, channel_id,
                       private_code, status, username_map, start_time, interval)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print_error(f"Error di curses: {e}")
    finally:
        # Kembali ke tampilan normal
        clear_screen()
        print_info("Monitoring dihentikan.")