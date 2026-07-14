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
# TENTUKAN IDENTITAS KONTEN
# =========================

category_check = " ".join(
    categories
).lower()



# Default Gamez Gemez Gaming

brand = {

    "name": "🎮 GAMEZ GEMEZ",

    "color": 0x5865F2

}



# Label Kiddo

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

            "color": 0x2ECC71

        }

        break



# =========================
# AUTHOR
# =========================

author = "Gamez Gemez"



# =========================
# DESKRIPSI ARTIKEL
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
# TANGGAL
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

        f"✍️ **Author**\n"
        f"{author}\n\n"

        "🔗 Klik judul untuk membaca "
        "artikel lengkap."

    ),


    "color": brand["color"],


    "footer": {

        "text": (

            f"{brand['name']} "
            "• Blog Update"

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
# KIRIM KE DISCORD
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
