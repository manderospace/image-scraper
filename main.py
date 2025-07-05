from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import sys
import praw

app = Flask(__name__)
CORS(app)

reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    user_agent="ImageFetcherBot/0.1 by your_reddit_username"
)


def scrape_reddit_images(query, subreddit="kpics", limit=10):
    try:
        sub = reddit.subreddit(subreddit)
        results = sub.search(query, limit=limit)
        urls = []
        for post in results:
            url = post.url
            if url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                urls.append(url)
        return urls
    except Exception as e:
        print("OAuth Reddit error:", e, flush=True)
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
    print("🔥 /search route was hit!", flush=True)
    query = request.args.get("query", "")
    subreddit = request.args.get("subreddit", "xypics")
    print(f"Searching '{query}' in subreddit '{subreddit}'", flush=True)
    images = scrape_reddit_images(query, subreddit)
    print(f"Found {len(images)} images", flush=True)
    return jsonify(images)

if __name__ == "__main__":
    print("🚀 Flask server starting up!")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
