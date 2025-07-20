#!/usr/bin/env python3
"""
Ms Rachel Tonie Stock Watcher
─────────────────────────────
• Polls the Tonies product JSON every 5 minutes
• Sends an immediate SMS alert (AWS SNS) when the variant flips to *IN STOCK*
• Sends a daily 7 p.m. Eastern summary SMS
• ALL messages include the product URL

Extra flag
----------
Run with `--test` (or `-t`) to send ONE simulated in‑stock alert immediately,
print the full SNS response(s) to the console for troubleshooting, and exit.

Requirements
------------
requests, boto3, python-dotenv
(backports.zoneinfo if you’re on Python 3.8)
"""

import os
import sys
import time
import argparse
import requests
from datetime import datetime, date, time as dtime, timedelta

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:                # Python 3.8
    from backports.zoneinfo import ZoneInfo  # type: ignore

from dotenv import load_dotenv
import logging

# ─────────────── CLI flag ──────────────────────────────────────────────────
ap = argparse.ArgumentParser(description="Watch Ms Rachel Tonie stock")
ap.add_argument(
    "-t", "--test",
    action="store_true",
    help="single‑shot test: assume in‑stock, print SNS responses, exit"
)
ap.add_argument(
    "-s", "--stock-test",
    action="store_true",
    help="test stock status check without delay or SMS"
)
args = ap.parse_args()

# ─────────────── Env / IFTTT setup ─────────────────────────────────────────
load_dotenv()

IFTTT_KEY = os.getenv("IFTTT_WEBHOOK_KEY")
IFTTT_EVENT = os.getenv("IFTTT_EVENT_NAME", "tonie_alert")

if not IFTTT_KEY:
    sys.exit("❌  IFTTT_WEBHOOK_KEY missing in .env")

# ─────────────── Product constants ─────────────────────────────────────────
VARIANT_ID = 45452782502039 #Ms Rachel Tonie
URL        = "https://us.tonies.com/products/ms-rachel-tonie" #Ms Rachel Tonie

#VARIANT_ID = 45447236059287 #Test Monkey Thing
#URL = "https://us.tonies.com/products/mindfulness-movement-with-marty-the-monkey-tonie" #Test Monkey Thing

URL_JS     = f"{URL}.js"
CHECK_EVERY = 300  # seconds (5 min) — ignored in test mode
TZ         = ZoneInfo("America/New_York")

# ─────────────── Logging setup ─────────────────────────────────────────────
logging.basicConfig(
    filename='tonie_watch.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ─────────────── Helper: send notification via IFTTT ──────────────────────
def send_notification(message: str) -> None:
    """Send notification via IFTTT webhook."""
    url = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT}/with/key/{IFTTT_KEY}"
    
    try:
        resp = requests.post(url, data={'value1': message}, timeout=10)
        resp.raise_for_status()
        print(f"✅ IFTTT notification sent: {resp.status_code}")
        logging.info(f"NOTIFICATION SENT: {message}")
    except Exception as e:
        print(f"⚠️  IFTTT notification error: {e}")
        logging.error(f"NOTIFICATION FAILED: {e}")

# ─────────────── Stock check helper ────────────────────────────────────────
def is_in_stock() -> bool:
    if args.test:
        return True
    r = requests.get(URL_JS, timeout=10)
    r.raise_for_status()
    variant = next(v for v in r.json()["variants"] if v["id"] == VARIANT_ID)
    return variant.get("available", False)

# ─────────────── Daily summary helper ──────────────────────────────────────
def daily_summary(total, hits, last_seen, in_stock_flag):
    status = "IN STOCK" if in_stock_flag else "OUT OF STOCK"
    send_notification(
        f"Ms Rachel Tonie summary {date.today()}:\n"
        f"• checks run: {total}\n"
        f"• times in stock: {hits}\n"
        f"• last check: {status} @ {last_seen.strftime('%I:%M %p')}\n"
        f"{URL}"
    )

# ─────────────── Test‑mode shortcut ────────────────────────────────────────
if args.test:
    print("🧪 TEST MODE — sending simulated in‑stock alert …")
    send_notification(f"🚨 TEST: Ms Rachel Tonie is IN STOCK!\n{URL}")
    print("Test alert sent; exiting.")
    sys.exit(0)

if args.stock_test:
    print("📊 STOCK TEST MODE — checking actual stock status …")
    try:
        print(f"Fetching from: {URL_JS}")
        print(f"Looking for variant ID: {VARIANT_ID}")
        
        r = requests.get(URL_JS, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        print(f"Found {len(data['variants'])} variants:")
        for v in data['variants']:
            print(f"  ID: {v['id']}, Available: {v.get('available', False)}, Title: {v.get('title', 'N/A')}")
        
        stock_status = is_in_stock()
        print(f"Stock status: {'IN STOCK' if stock_status else 'OUT OF STOCK'}")
    except Exception as e:
        print(f"❌ Error checking stock: {e}")
        import traceback
        traceback.print_exc()
    sys.exit(0)

# ─────────────── Normal loop ───────────────────────────────────────────────
print("🔍  Watching Ms Rachel Tonie every 5 minutes …")

total_checks = hits = 0
last_state   = None
now          = datetime.now(TZ)
next_7pm     = datetime.combine(now.date(), dtime(19, 0, tzinfo=TZ), tzinfo=TZ)
if now >= next_7pm:
    next_7pm += timedelta(days=1)

while True:
    try:
        now = datetime.now(TZ)

        # Daily 7 p.m. summary
        if now >= next_7pm:
            daily_summary(total_checks, hits, now, last_state)
            total_checks = hits = 0
            next_7pm += timedelta(days=1)

        # Stock check
        in_stock = is_in_stock()
        status = "IN STOCK" if in_stock else "OUT OF STOCK"
        logging.info(f"CHECK: {status}")
        total_checks += 1
        if in_stock:
            hits += 1
            if last_state in (None, False):
                send_notification(f"🚨 Ms Rachel Tonie is IN STOCK!\n{URL}")
        last_state = in_stock

    except Exception as e:
        print(f"⚠️  {e}")

    time.sleep(CHECK_EVERY)
