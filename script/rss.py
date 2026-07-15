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

HISTORY_FILE = Path("data/sent_posts.txt")


# Ganti dengan URL icon asli kamu

GAMEZ_ICON = "https://raw.githubusercontent.com/gamezgemez/gamezgemez-discord-rss/main/assets/Gamez%20Gemez%20Logo.png"

KIDDO_ICON = "https://raw.githubusercontent.com/gamezgemez/gamezgemez-discord-rss/main/assets/Gamez%20Gemez%20Kiddo%20Logo.png"



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
# DEBUG RSS
# =========================

print("===== DEBUG =====")
print("RSS Title :", latest.title)
print("RSS Link  :", latest.link)

if HISTORY_FILE.exists():
    print(
        "Saved Link:",
        HISTORY_FILE.read_text(
    encoding="utf-8"
).strip()
    )
else:
    print("Saved Link: (kosong)")

print("=================")



# =========================
# CEK DUPLIKAT
# =========================

if HISTORY_FILE.exists():

   last_sent = HISTORY_FILE.read_text(
    encoding="utf-8"
).strip()

else:

    last_sent = ""


if HISTORY_FILE.exists():
    sent_links = set(
        HISTORY_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
    )
else:
    sent_links = set()

if latest_link in sent_links:
    print("Artikel sudah pernah dikirim.")
    exit()



# =========================
# AMBIL LABEL BLOGGER
# =========================

labels = []


if hasattr(latest, "tags"):

    for tag in latest.tags:

        if hasattr(tag, "term"):

            labels.append(
                tag.term.strip()
            )


# fallback

if hasattr(latest, "category"):

    if latest.category:

        labels.append(
            latest.category
        )


labels = list(
    dict.fromkeys(labels)
)



label_text = " • ".join(
    label.upper()
    for label in labels
)



# =========================
# DETEKSI BRAND BERDASARKAN LABEL
# =========================

label_check = [
    x.lower()
    for x in labels
]



# Default

brand = {

    "name": "🎮 GAMEZ GEMEZ",

    "icon": GAMEZ_ICON,

    "color": 0x5865F2,

    "description": (
        "🎮 Gaming Content\n"
        "Review game, berita gaming, "
        "guide, dan informasi terbaru."
    )

}



# Jika label Gamez Gemez Kiddo ditemukan

if "gamez gemez kiddo" in label_check:

    brand = {

        "name": "🧸 GAMEZ GEMEZ KIDDO",

        "icon": KIDDO_ICON,

        "color": 0x2ECC71,

        "description": (
            "🧸 Family Friendly Content\n"
            "Konten game aman untuk anak "
            "dan keluarga."
        )

    }



# Jika label Gamez Gemez ditemukan

elif "gamez gemez" in label_check:

    brand = {

        "name": "🎮 GAMEZ GEMEZ",

        "icon": GAMEZ_ICON,

        "color": 0x5865F2,

        "description": (
            "🎮 Gaming Content\n"
            "Review game, berita gaming, "
            "guide, dan informasi terbaru."
        )

    }



# =========================
# BERSIHKAN DESKRIPSI
# =========================

import re

summary_html = latest.get("summary", "")

soup = BeautifulSoup(summary_html, "html.parser")

# Hapus script/style
for tag in soup(["script", "style"]):
    tag.decompose()

# Rapikan teks
text = " ".join(
    soup.get_text(separator=" ", strip=True).split()
)

# Pisahkan menjadi kalimat
sentences = re.split(r'(?<=[.!?])\s+', text)

description = ""
word_count = 0

for sentence in sentences:

    words = sentence.split()

    # Maksimal sekitar 75 kata
    if word_count + len(words) > 75:
        break

    description += sentence + " "
    word_count += len(words)

description = description.strip()

# Jika terlalu pendek, tambahkan kalimat berikutnya
if word_count < 50 and len(sentences) > 0:

    for sentence in sentences:

        if sentence not in description:

            description += " " + sentence

            if len(description.split()) >= 50:
                break

description = description.strip()



# =========================
# THUMBNAIL
# =========================

thumbnail = None


img = soup.find("img")


if img:

    thumbnail = img.get(
        "src"
    )



# =========================
# TIMESTAMP
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
# DISCORD EMBED
# =========================

embed = {


    "title": (

        f"{brand['name']}\n"
        f"{latest.title}"

    ),


    "url": latest.link,


    "description": (

    f"{brand['description']}\n\n"

    "━━━━━━━━━━━━━━\n\n"

    f"{description}\n\n"

    f"📖 **Baca selengkapnya di sini:**\n"
    f"{latest.link}\n\n"

    "━━━━━━━━━━━━━━\n\n"

    f"🏷️ **Label Blogger**\n"
    f"{label_text}\n\n"

    "✍️ **Author**\n"
    "Gamez Gemez"

),


    "color": brand["color"],


    "author": {

        "name": brand["name"],

        "icon_url": brand["icon"]

    },


    "footer": {

        "text": (
            "Gamez Gemez Blog Update"
        ),

        "icon_url": brand["icon"]

    }

}



if thumbnail:

    embed["thumbnail"] = {

        "url": thumbnail

    }



if timestamp:

    embed["timestamp"] = timestamp



# =========================
# KIRIM DISCORD
# =========================

payload = {

    "username": brand["name"],

    "embeds": [

        embed

    ]

}



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



if response.status_code == 204:

    print(
        "Berhasil mengirim ke Discord."
    )


    HISTORY_FILE.parent.mkdir(...)


    sent_links.add(latest_link)

HISTORY_FILE.write_text(
    "\n".join(sent_links),
    encoding="utf-8"
)


else:

    print(
        response.text
    )
