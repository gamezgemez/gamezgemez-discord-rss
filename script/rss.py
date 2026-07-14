import os
from pathlib import Path
import datetime

import feedparser
import requests
from bs4 import BeautifulSoup


# =========================
# KONFIGURASI
# =========================

RSS_URL = "https://gamezgemezofficial.blogspot.com/feeds/posts/default"

LATEST_FILE = Path("data/latest_post.txt")



# =========================
# AMBIL ARTIKEL TERBARU
# =========================

feed = feedparser.parse(RSS_URL)


if not feed.entries:

    print("Tidak ada artikel.")
    exit()


latest = feed.entries[0]

latest_link = latest.link



# =========================
# CEK ARTIKEL DUPLIKAT
# =========================

if LATEST_FILE.exists():

    last_sent = LATEST_FILE.read_text(
        encoding="utf-8"
    ).strip()

else:

    last_sent = ""


if latest_link == last_sent:

    print(
        "Artikel sudah pernah dikirim."
    )

    exit()



# =========================
# AMBIL LABEL BLOGGER
# =========================

categories = []


if hasattr(latest, "tags"):

    for tag in latest.tags:

        categories.append(
            tag.term
        )


if categories:

    category_text = ", ".join(categories)

else:

    category_text = "Gaming"



# =========================
# AMBIL AUTHOR
# =========================

author = latest.get(
    "author",
    "Gamez Gemez"
)



# =========================
# BERSIHKAN HTML
# =========================

summary_html = latest.get(
    "summary",
    ""
)


soup = BeautifulSoup(
    summary_html,
    "html.parser"
)


description = soup.get_text(
    " ",
    strip=True
)



if len(description) > 350:

    description = (
        description[:350]
        + "..."
    )



# =========================
# CARI THUMBNAIL
# =========================

thumbnail = None


img = soup.find("img")


if img:

    image_url = img.get("src")

    if image_url:

        thumbnail = image_url



# =========================
# FORMAT TIMESTAMP DISCORD
# =========================

timestamp = None


published = latest.get(
    "published_parsed"
)


if published:

    timestamp = datetime.datetime(
        *published[:6]
    ).isoformat() + "Z"



# =========================
# BUAT DISCORD EMBED
# =========================

embed = {

    "title": (
        f"🎮 {latest.title}"
    ),


    "url": latest.link,


    "description": (

        "🎮 **Gamez Gemez News**\n\n"

        f"{description}\n\n"

        "━━━━━━━━━━━━━━\n\n"

        f"🏷️ **Kategori**\n"
        f"{category_text}\n\n"

        f"✍️ **Author**\n"
        f"{author}\n\n"

        "🔗 Klik judul untuk membaca "
        "artikel lengkap."

    ),


    "color": 0x5865F2,


    "footer": {

        "text": (
            "Gamez Gemez Official "
            "• Gaming Update"
        )

    }

}



# Tambahkan thumbnail jika tersedia

if thumbnail:

    embed["thumbnail"] = {

        "url": thumbnail

    }



# Tambahkan tanggal

if timestamp:

    embed["timestamp"] = timestamp



# =========================
# PAYLOAD DISCORD
# =========================

payload = {

    "username": (
        "Gamez Gemez News"
    ),


    "embeds": [

        embed

    ]

}



# =========================
# KIRIM WEBHOOK
# =========================

webhook = os.environ[
    "DISCORD_WEBHOOK"
]


response = requests.post(
    webhook,
    json=payload
)



print(
    "Discord Status:",
    response.status_code
)



# =========================
# SIMPAN ARTIKEL TERAKHIR
# =========================

if response.status_code == 204:

    print(
        "Berhasil mengirim ke Discord."
    )


    LATEST_FILE.parent.mkdir(
        exist_ok=True
    )


    LATEST_FILE.write_text(
        latest_link,
        encoding="utf-8"
    )


else:

    print(
        response.text
    )
