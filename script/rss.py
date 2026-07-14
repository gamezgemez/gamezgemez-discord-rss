import os
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup


# =========================
# KONFIGURASI
# =========================

RSS_URL = "https://gamezgemezofficial.blogspot.com/feeds/posts/default"

LATEST_FILE = Path("data/latest_post.txt")


# Logo hanya untuk ikon kecil di embed
# Tidak mengubah avatar webhook Discord
LOGO_URL = "https://YOUR_LOGO_URL.png"



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
    "\n",
    strip=True
)



if len(description) > 350:

    description = (
        description[:350]
        + "..."
    )



# =========================
# CARI THUMBNAIL ARTIKEL
# =========================

thumbnail = None


img = soup.find("img")


if img and img.get("src"):

    thumbnail = img["src"]



# Jika artikel tidak punya gambar

if not thumbnail:

    thumbnail = LOGO_URL



# =========================
# DATA ARTIKEL
# =========================

published = latest.get(
    "published"
)



# =========================
# DISCORD EMBED
# =========================

embed = {

    "title": (
        f"🎮 {latest.title}"
    ),


    "url": latest.link,


    "description": (
        f"{description}\n\n"
        "🔗 **Baca artikel lengkap "
        "di Gamez Gemez Blog**"
    ),


    # Warna Discord BlurPle
    "color": 0x5865F2,


    "author": {

        "name": (
            "Gamez Gemez News"
        ),

        "icon_url": LOGO_URL

    },


    "thumbnail": {

        "url": thumbnail

    },


    "footer": {

        "text": (
            "🎮 Gamez Gemez Official "
            "• Gaming Update"
        ),

        "icon_url": LOGO_URL

    }

}



# Tambahkan tanggal artikel

if published:

    embed["timestamp"] = published



# =========================
# PAYLOAD DISCORD
# =========================

# Tidak menggunakan avatar_url
# Logo webhook tetap memakai setting Discord

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
# SIMPAN ARTIKEL TERKIRIM
# =========================

if response.status_code == 204:

    print(
        "Berhasil mengirim ke Discord."
    )


    LATEST_FILE.write_text(
        latest_link,
        encoding="utf-8"
    )


else:

    print(
        response.text
    )
