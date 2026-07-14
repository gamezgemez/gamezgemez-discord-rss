import os
import feedparser
import requests

RSS_URL = "https://gamezgemezofficial.blogspot.com/feeds/posts/default?alt=rss"

feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("Tidak ada artikel.")
    exit()

latest = feed.entries[0]

webhook = os.environ["DISCORD_WEBHOOK"]

# Ringkasan artikel
description = ""

if "summary" in latest:
    description = latest.summary

description = description.replace("<br />", "\n")
description = description.replace("<br/>", "\n")

# Potong supaya tidak terlalu panjang
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
    "embeds": [
        embed
    ]
}

response = requests.post(webhook, json=payload)

print("Discord Status:", response.status_code)

if response.status_code == 204:
    print("Berhasil!")
else:
    print(response.text)
