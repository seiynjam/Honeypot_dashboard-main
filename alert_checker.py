import os
import re
import time
import json
import requests
from datetime import datetime, timedelta
import pandas as pd

# ====== CONFIG ======
LOG_FILE = "log_denfender\logs\honeypot_log.txt"
STATE_FILE = "last_alerted_requests.json"
TELEGRAM_TOKEN = "8707762224:AAFKWln2niuJI9lb-NMYje0_r8o4rB9DqlI"
CHAT_ID = "6305922625"
ALERT_THRESHOLD = 500       # แจ้งเตือนเมื่อ request ≥ 500
TIME_WINDOW = 5             # นาที
STATE_EXPIRE_HOURS = 24     # ลบ state ของ IP ที่เก่าเกินนี้
RESET_STATE = False          # True = รีเซ็ต state ทุกครั้ง, False = ใช้ค่าเดิม
# =====================

def send_alert(ip, count, start_time, end_time):
    msg = (
        f"⚠️ ตรวจพบ `{ip}` ยิงเข้าระบบเยอะมาก ({count} ครั้ง)\n"
        f"ช่วงเวลา {start_time.strftime('%H:%M:%S')} - {end_time.strftime('%H:%M:%S')}"
    )
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
        if r.status_code == 200:
            print(f"✅ ส่งแจ้งเตือน Telegram แล้ว")
        else:
            print(f"❌ Telegram error code: {r.status_code}")
    except Exception as e:
        print(f"❌ ส่งแจ้งเตือน Telegram ไม่สำเร็จ: {e}")

def parse_honeypot_log():
    pattern = r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:\.\d+)?\] \[INFO\] ([\d\.]+) - GET"
    results = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                match = re.search(pattern, line)
                if match:
                    timestamp = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
                    ip = match.group(2)
                    results.append({"ip": ip, "timestamp": timestamp})
    except Exception as e:
        print(f"❌ อ่าน log ไม่สำเร็จ: {e}")
    df = pd.DataFrame(results)
    if not df.empty:
        print(f"📄 โหลด log ได้ {len(df)} records ล่าสุด = {df['timestamp'].max()}")
    else:
        print("⚠️ ยังไม่มีข้อมูล match กับ regex")
    return df

def run_checker():
    if RESET_STATE and os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print("♻️ รีเซ็ตสถานะล่าสุดเรียบร้อย")

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_state = json.load(f)
    else:
        last_state = {}

    fixed_state = {}
    for ip, val in last_state.items():
        if isinstance(val, int):
            fixed_state[ip] = {"count": val, "last_seen": None}
        elif isinstance(val, dict):
            fixed_state[ip] = {
                "count": val.get("count", 0),
                "last_seen": val.get("last_seen")
            }
        else:
            fixed_state[ip] = {"count": 0, "last_seen": None}
    last_state = fixed_state

    df = parse_honeypot_log()
    if df.empty:
        return

    now = datetime.now()
    window_start = now - timedelta(minutes=TIME_WINDOW)
    df_recent = df[df["timestamp"] >= window_start]
    ip_counts = df_recent.groupby("ip").size()

    # ====== แสดงหัวข้อรอบตรวจ ======
    print("\n" + "="*50)
    print(f"🕒 รอบตรวจล่าสุด: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)

    for ip, count in ip_counts.items():
        ip_state = last_state.get(ip, {"count": 0, "last_seen": None})
        last_count = ip_state["count"]

        alert_sent = False
        if count >= ALERT_THRESHOLD:
            send_alert(ip, count, window_start, now)
            alert_sent = True

        last_state[ip] = {"count": count, "last_seen": now.strftime("%Y-%m-%d %H:%M:%S")}

        # ====== แสดงผลสวยขึ้น ======
        print(f"IP: {ip:<15} | count: {count:<4} | last_alert: {last_count:<4} | "
              f"{'✅ Alert sent' if alert_sent else '—'}")

    cutoff = now - timedelta(hours=STATE_EXPIRE_HOURS)
    cleaned_state = {}
    for ip, data in last_state.items():
        try:
            if data.get("last_seen") and datetime.strptime(data["last_seen"], "%Y-%m-%d %H:%M:%S") >= cutoff:
                cleaned_state[ip] = data
        except Exception:
            pass
    last_state = cleaned_state

    with open(STATE_FILE, "w") as f:
        json.dump(last_state, f, indent=2)

    print(f"📝 บันทึกสถานะล่าสุด\n")


# ====== MAIN LOOP ======
print("🚀 เริ่มตรวจจับ log จาก Honeypot... (Ctrl+C เพื่อหยุด)")
while True:
    run_checker()
    time.sleep(10)
