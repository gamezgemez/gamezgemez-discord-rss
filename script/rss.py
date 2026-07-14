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

message = {
    "content": f"📰 Artikel baru!\n\n**{latest.title}**\n{latest.link}"
}

response = requests.post(webhook, json=message)

print("Status Discord:", response.status_code)

if response.status_code == 204:
    print("✅ Berhasil mengirim ke Discord!")
else:
    print(response.text)
