import feedparser

RSS_URL = "https://gamezgemezofficial.blogspot.com/feeds/posts/default?alt=rss"

print("=" * 60)
print("GAMEZ GEMEZ RSS TEST")
print("=" * 60)

feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("❌ RSS tidak memiliki artikel.")
    exit()

latest = feed.entries[0]

print("Judul:")
print(latest.title)

print()

print("Link:")
print(latest.link)

print()

print("Jumlah artikel:", len(feed.entries))

print("=" * 60)
