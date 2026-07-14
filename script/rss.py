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


# Ganti dengan URL icon asli kamu

GAMEZ_ICON = "https://media.discordapp.net/attachments/1525719632210563082/1526602588219506748/style1_7.png?ex=6a579ef3&is=6a564d73&hm=073e936ddfc1685ae41f916532e51131b52ea2f43b9ebf70e96df22dc006d314&=&format=webp&quality=lossless&width=821&height=821"

KIDDO_ICON = "https://media.discordapp.net/attachments/1525719632210563082/1526602512516386856/pose_change_33.png?ex=6a579ee1&is=6a564d61&hm=a5c1d9226d1b5d791a67338dc0d62cf37cbfca9527a2e188a8e4d6cf6d21193f&=&format=webp&quality=lossless&width=821&height=821"



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
# CEK DUPLIKAT
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



label_text = ", ".join(labels)



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
