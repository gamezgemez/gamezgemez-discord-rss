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

categories = []


if hasattr(latest, "tags"):

    for tag in latest.tags:

        categories.append(
            tag.term.lower()
        )



if categories:

    category_text = ", ".join(
        categories
    )

else:

    category_text = "Gaming"



# =========================
# TENTUKAN TIPE KONTEN
# =========================

category_check = " ".join(
    categories
)



# Default Gamez Gemez Gaming

content_type = {

    "name": "🎮 Gamez Gemez Gaming",

    "color": 0x5865F2

}



# Kiddo

kiddo_keywords = [

    "roblox",
    "kiddo",
    "kids",
    "family",
    "anak"

]


for word in kiddo_keywords:

    if word in category_check:

        content_type = {

            "name": "🧸 Gamez Gemez Kiddo",

            "color": 0x2ECC71

        }

        break



# News

news_keywords = [

    "news",
    "update",
    "trailer",
    "berita"

]


for word in news_keywords:

    if word in category_check:

        content_type = {

            "name": "📰 Gamez Gemez News",

            "color": 0x9B59B6

        }

        break



# =========================
# AUTHOR
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

        f"{content_type['name']}\n"
        f"{latest.title}"

    ),


    "url": latest.link,


    "description": (

        f"{description}\n\n"

        "━━━━━━━━━━━━━━\n\n"

        f"🏷️ **Kategori**\n"
        f"{category_text}\n\n"

        f"✍️ **Author**\n"
        f"{author}\n\n"

        "🔗 Klik judul untuk membaca "
        "artikel lengkap."

    ),


    "color": content_type["color"],


    "footer": {

        "text": (

            f"{content_type['name']} "
            "• Gamez Gemez"

        )

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


    "username": (

        content_type["name"]

    ),


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
