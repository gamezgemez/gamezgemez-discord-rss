import os
from pathlib import Path

import feedparser
import requests

RSS_URL = "https://gamezgemezofficial.blogspot.com/feeds/posts/default?alt=rss"

LATEST_FILE = Path("data/latest_post.txt")

feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("Tidak ada artikel ditemukan.")
    exit()

latest = feed.entries[0]

latest_link = latest.link

# Membaca link terakhir
if LATEST_FILE.exists():
    last_sent = LATEST_FILE.read_text(encoding="utf-8").strip()
else:
    last_sent = ""

# Jika artikel sama, hentikan
if latest_link == last_sent:
    print("Artikel sudah pernah dikirim.")
    exit()

# Ambil webhook
webhook = os.environ["DISCORD_WEBHOOK"]

# Ringkasan artikel
description = ""

if "summary" in latest:
    description = latest.summary

description = (
    description
    .replace("<br />", "\n")
    .replace("<br/>", "\n")
)

description = description[:350]

embed = {
    "title": latest.title,
    "description": description,
    "url": latest.link,
    "color": 3066993,
    "footer": {
        "text": "Gamez Gemez Official"
    }
}

payload = {
    "username": "Gamez Gemez",
    "embeds": [embed]
}

response = requests.post(webhook, json=payload)

print("Discord Status:", response.status_code)

if response.status_code == 204:
    print("Berhasil mengirim ke Discord.")

    LATEST_FILE.write_text(latest_link, encoding="utf-8")

else:
    print(response.text)
