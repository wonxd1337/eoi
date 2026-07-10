import requests
import time
import re

API = "https://discord.com/api/v10"

def get_key(bot_token, channel_id, shortlink, timeout=60):
    """
    Mendapatkan key dari Discord menggunakan BOT TOKEN (resmi).
    """
    url = f"{API}/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json"
    }

    # Kirim command ke channel
    payload = {"content": f"/bypass url: {shortlink}"}
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            print(f"[KeyFetcher] Gagal kirim: {r.status_code}")
            return None
        print("[KeyFetcher] Pesan terkirim, menunggu balasan...")
    except Exception as e:
        print(f"[KeyFetcher] Error: {e}")
        return None

    # Polling balasan
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(f"{url}?limit=10", headers=headers)
            if resp.status_code != 200:
                time.sleep(2)
                continue
            for msg in resp.json():
                content = msg.get('content', '')
                match = re.search(r'(FREE_[a-fA-F0-9]{32,})', content)
                if match:
                    print("[KeyFetcher] Key ditemukan!")
                    return match.group(1)
                if "error" in content.lower() or "failed" in content.lower():
                    print(f"[KeyFetcher] Bot error: {content[:100]}")
                    return None
        except Exception as e:
            print(f"[KeyFetcher] Polling error: {e}")
        time.sleep(2)

    print("[KeyFetcher] Timeout menunggu balasan.")
    return None