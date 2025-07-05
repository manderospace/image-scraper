from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

def scrape_reddit_images(query, subreddit="xypics", sort="top", limit=10):
    print(f"🔍 Scraping subreddit: {subreddit}, query: {query}")
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": query,
        "sort": sort,
        "limit": limit,
        "type": "link",
        "restrict_sr": "1",
        "raw_json": 1
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Reddit Image Scraper)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        posts = data.get("data", {}).get("children", [])
        image_urls = extract_image_urls(posts)
        return image_urls
    except Exception as e:
        print("Error fetching Reddit posts:", e)
        return []

def fix_imgur_url(url):
    if "imgur.com" in url and not url.startswith("https://i.imgur.com"):
        parts = url.rstrip("/").split("/")
        image_id = parts[-1].split(".")[0]
        return f"https://i.imgur.com/{image_id}.jpg"
    return url

def extract_image_urls(posts):
    urls = []
    for post in posts:
        url = post["data"].get("url", "")
        if url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            urls.append(fix_imgur_url(url))
        elif "reddit.com/gallery/" in url and "media_metadata" in post["data"]:
            media = post["data"]["media_metadata"]
            if media:
                first_image = next(iter(media.values()))
                img_url = first_image["s"]["u"].replace("&amp;", "&")
                urls.append(img_url)
    return urls

@app.route("/search")
def search():
    print("🔥 /search route was hit!")
    query = request.args.get("query", "")
    subreddit = request.args.get("subreddit", "xypics")
    print(f"Searching '{query}' in subreddit '{subreddit}'")
    images = scrape_reddit_images(query, subreddit)
    print(f"Found {len(images)} images")
    return jsonify(images)

if __name__ == "__main__":
    print("🚀 Flask server starting up!")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
