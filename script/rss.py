import os
from pathlib import Path
import datetime
import re

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

# Ambil Webhook dari Environment Variable
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
if not WEBHOOK_URL:
    print("Error: Environment variable 'DISCORD_WEBHOOK' tidak ditemukan.")
    exit()

# =========================
# AMBIL ARTIKEL TERBARU
# =========================

feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("Tidak ada artikel di RSS Feed.")
    exit()

# Ambil maksimal 10 artikel terbaru
entries = feed.entries[:10]

# Muat riwayat artikel yang sudah pernah dikirim
if HISTORY_FILE.exists():
    sent_links = set(
        HISTORY_FILE.read_text(encoding="utf-8").splitlines()
    )
else:
    sent_links = set()

print(f"Menemukan {len(entries)} artikel terbaru.")
print(f"History berisi {len(sent_links)} artikel.\n")

# Flag untuk mendeteksi apakah ada history baru yang perlu disimpan
history_updated = False

# Proses satu per satu artikel (Semua proses sekarang di dalam Loop)
for latest in entries:
    latest_link = latest.link

    print("===== MEMPROSES ARTIKEL =====")
    print("RSS Title :", latest.title)
    print("RSS Link  :", latest_link)

    # Lewati jika sudah pernah dikirim
    if latest_link in sent_links:
        print("Status    : SUDAH DIKIRIM (Skipped)\n")
        continue
    else:
        print("Status    : BELUM DIKIRIM (Processing...)")

    # =========================
    # AMBIL LABEL BLOGGER
    # =========================
    labels = []

    if hasattr(latest, "tags"):
        labels = [
            tag.term.strip()
            for tag in latest.tags
            if hasattr(tag, "term") and tag.term.strip()
        ]
    elif hasattr(latest, "category") and latest.category:
        labels = [latest.category.strip()]

    # Hapus label duplikat tetapi tetap mempertahankan urutan
    labels = list(dict.fromkeys(labels))

    # Jika artikel tidak memiliki label
    if not labels:
        labels = ["Uncategorized"]

    # Untuk ditampilkan di Discord
    label_text = " • ".join(label.upper() for label in labels)

    # =========================
    # DETEKSI BRAND BERDASARKAN LABEL
    # =========================
    label_check = {label.lower().strip() for label in labels}

    # Default: Gamez Gemez
    brand = {
        "name": "🎮 GAMEZ GEMEZ",
        "icon": GAMEZ_ICON,
        "color": 0x5865F2,
        "description": (
            "🎮 Gaming Content\n"
            "Review game, berita gaming, guide, dan informasi terbaru."
        )
    }

    # Jika artikel berlabel Gamez Gemez Kiddo
    if "gamez gemez kiddo" in label_check:
        brand = {
            "name": "🧸 GAMEZ GEMEZ KIDDO",
            "icon": KIDDO_ICON,
            "color": 0x2ECC71,
            "description": (
                "🧸 Family Friendly Content\n"
                "Konten game aman untuk anak dan keluarga."
            )
        }
    # Jika artikel berlabel Gamez Gemez
    elif "gamez gemez" in label_check:
        brand = {
            "name": "🎮 GAMEZ GEMEZ",
            "icon": GAMEZ_ICON,
            "color": 0x5865F2,
            "description": (
                "🎮 Gaming Content\n"
                "Review game, berita gaming, guide, dan informasi terbaru."
            )
        }

    # =========================
    # BERSIHKAN DESKRIPSI
    # =========================
    summary_html = latest.get("summary", "")
    soup = BeautifulSoup(summary_html, "html.parser")

    # Hapus tag yang tidak diperlukan
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Ambil seluruh teks dan rapikan spasi
    text = " ".join(soup.get_text(separator=" ", strip=True).split())

    # Pisahkan berdasarkan kalimat
    sentences = re.split(r'(?<=[.!?])\s+', text)

    summary_sentences = []
    word_count = 0

    for sentence in sentences:
        words = sentence.split()
        # Berhenti jika sudah mencapai sekitar 75 kata
        if word_count + len(words) > 75:
            break
        summary_sentences.append(sentence)
        word_count += len(words)

    # Jika ringkasan terlalu pendek (<50 kata), tambahkan kalimat berikutnya
    if word_count < 50:
        for sentence in sentences[len(summary_sentences):]:
            summary_sentences.append(sentence)
            word_count += len(sentence.split())
            if word_count >= 50:
                break

    description = " ".join(summary_sentences).strip()

    # Fallback jika RSS tidak memiliki titik sehingga hanya 1 kalimat panjang
    if len(description.split()) > 75:
        words = description.split()[:75]
        description = " ".join(words)

        # Hindari memotong di tengah kata/kalimat
        if "." in description:
            description = description.rsplit(".", 1)[0] + "."
        elif "," in description:
            description = description.rsplit(",", 1)[0] + "..."
        else:
            description += "..."

    # =========================
    # THUMBNAIL
    # =========================
    thumbnail = None
    img = soup.find("img")

    if img and img.get("src"):
        thumbnail = img["src"]
    else:
        thumbnail = brand["icon"]

    # =========================
    # TIMESTAMP
    # =========================
    timestamp = None
    published = latest.get("published_parsed")

    if published:
        timestamp = datetime.datetime(
            *published[:6],
            tzinfo=datetime.timezone.utc
        ).isoformat()

    # =========================
    # DISCORD EMBED
    # =========================
    embed = {
        "title": latest.title,
        "url": latest_link,
        "description": (
            f"{brand['description']}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{description}\n\n"
            f"📖 **Baca selengkapnya di sini:**\n"
            f"{latest_link}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🏷️ **Label**\n"
            f"{label_text}\n\n"
            "✍️ **Author**\n"
            "Gamez Gemez"
        ),
        "color": brand["color"],
        "author": {
            "name": brand["name"],
            "icon_url": brand["icon"]
        },
        "thumbnail": {
            "url": thumbnail
        },
        "footer": {
            "text": "Gamez Gemez Blog Update",
            "icon_url": brand["icon"]
        }
    }

    if timestamp:
        embed["timestamp"] = timestamp

    # =========================
    # KIRIM DISCORD
    # =========================
    payload = {
        "username": brand["name"],
        "embeds": [embed]
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    print("Discord Status:", response.status_code)

    if response.status_code == 204:
        print("Berhasil mengirim ke Discord.\n")
        # Masukkan ke memori history agar tidak dikirim ulang pada iterasi loop berikutnya
        sent_links.add(latest_link)
        history_updated = True
    else:
        print(f"Gagal mengirim. Response: {response.text}\n")

# =========================
# SIMPAN HISTORY (Di luar loop, setelah semua artikel diproses)
# =========================
if history_updated:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        "\n".join(sorted(sent_links)),
        encoding="utf-8"
    )
    print("History file berhasil diperbarui.")
