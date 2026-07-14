import os
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

RSS_URL = "https://gamezgemezofficial.blogspot.com/feeds/posts/default?alt=rss"

LATEST_FILE = Path("data/latest_post.txt")

feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("Tidak ada artikel.")
    exit()

latest = feed.entries[0]
latest_link = latest.link

# -------------------------
# Cek artikel terakhir
# -------------------------

if LATEST_FILE.exists():
    last_sent = LATEST_FILE.read_text(encoding="utf-8").strip()
else:
    last_sent = ""

if latest_link == last_sent:
    print("Artikel sudah pernah dikirim.")
    exit()

# -------------------------
# Bersihkan HTML
# -------------------------

summary_html = latest.get("summary", "")

soup = BeautifulSoup(summary_html, "html.parser")

description = soup.get_text("\n", strip=True)

if len(description) > 350:
    description = description[:350] + "..."

# -------------------------
# Cari gambar pertama
# -------------------------

thumbnail = None

img = soup.find("img")

if img and img.get("src"):
    thumbnail = img["src"]

# -------------------------
# Discord Embed
# -------------------------

embed = {
    "title": latest.title,
    "url": latest.link,
    "description": description,
    "color": 0x2ECC71,
    "footer": {
        "text": "Gamez Gemez Official"
    }
}

if thumbnail:
    embed["thumbnail"] = {
        "url": thumbnail
    }

payload = {
    "username": "Gamez Gemez",
    "embeds": [embed]
}

webhook = os.environ["DISCORD_WEBHOOK"]

response = requests.post(webhook, json=payload)

print("Discord Status:", response.status_code)

if response.status_code == 204:
    print("Berhasil mengirim ke Discord.")
    LATEST_FILE.write_text(latest_link, encoding="utf-8")
else:
    print(response.text)
