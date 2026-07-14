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


# Icon kecil dalam embed
# Tidak mengubah avatar webhook Discord

GAMEZ_ICON = "https://photos.google.com/u/1/photo/AF1QipNOV5N3g22luuBhWF3jXyIo5zUsNt-D3pkm_6Y3"

KIDDO_ICON = "https://photos.google.com/u/1/photo/AF1QipOHNECwazkHOEiWTyZ5XoD0GSzNZ7CVkobFF4CC"



# =========================
# AMBIL ARTIKEL
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

    print("Artikel sudah pernah dikirim.")
    exit()



# =========================
# AMBIL LABEL BLOGGER
# =========================

categories = []


if hasattr(latest, "tags"):

    for tag in latest.tags:

        if hasattr(tag, "term"):

            categories.append(
                tag.term
            )


if not categories and hasattr(latest, "category"):

    categories.append(
        latest.category
    )


categories = list(
    dict.fromkeys(categories)
)


if categories:

    category_text = ", ".join(categories)

else:

    category_text = "Gaming"



# =========================
# TENTUKAN BRAND
# =========================

category_check = " ".join(
    categories
).lower()



# Default Gamez Gemez

brand = {

    "name": "🎮 GAMEZ GEMEZ",

    "color": 0x5865F2,

    "icon": GAMEZ_ICON

}



# Deteksi Kiddo

kiddo_keywords = [

    "kiddo",
    "kids",
    "family",
    "anak",
    "roblox"

]


for keyword in kiddo_keywords:

    if keyword in category_check:

        brand = {

            "name": "🧸 GAMEZ GEMEZ KIDDO",

            "color": 0x2ECC71,

            "icon": KIDDO_ICON

        }

        break



# =========================
# DESKRIPSI
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

        f"{description}\n\n"

        "━━━━━━━━━━━━━━\n\n"

        f"🏷️ **Label**\n"
        f"{category_text}\n\n"

        "✍️ **Author**\n"
        "Gamez Gemez\n\n"

        "🔗 Klik judul untuk membaca "
        "artikel lengkap."

    ),


    "color": brand["color"],


    "author": {

        "name": brand["name"],

        "icon_url": brand["icon"]

    },


    "footer": {

        "text": (

            f"{brand['name']} "
            "• Blog Update"

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
