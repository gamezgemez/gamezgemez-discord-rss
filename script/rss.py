# =========================
# DATA ARTIKEL
# =========================

published = latest.get(
    "published_parsed"
)


timestamp = None


if published:

    import datetime

    timestamp = datetime.datetime(
        *published[:6]
    ).isoformat() + "Z"



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



if timestamp:

    embed["timestamp"] = timestamp
