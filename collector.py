import os
import re
import requests
import trafilatura

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from feedgen.feed import FeedGenerator


url = "https://www.mfa.gov.cn/eng/xw/fyrbt/"

response = requests.get(url, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.content, "html.parser")

articles = []


# Find the 10 most recent article links
for link in soup.find_all("a", href=True):

    title = link.get_text(" ", strip=True)
    full_url = urljoin(url, link["href"])

    if (
        "/eng/xw/fyrbt/" in full_url
        and full_url.endswith(".html")
        and title
    ):

        if not any(article["url"] == full_url for article in articles):

            articles.append({
                "title": title,
                "url": full_url
            })

    if len(articles) >= 10:
        break


# Create folders
os.makedirs("articles/mfa", exist_ok=True)
os.makedirs("feeds", exist_ok=True)


def clean_filename(title):

    title = re.sub(r'[\\/:*?"<>|]', '', title)

    title = re.sub(r'\s+', ' ', title).strip()

    return title


rss_items = []


# Download and save each article
for article in articles:

    try:

        article_response = requests.get(
            article["url"],
            timeout=30
        )

        article_response.raise_for_status()

        article_text = trafilatura.extract(
            article_response.text,
            url=article["url"],
            include_comments=False,
            include_links=False
        )

        article_text = article_text or ""

        filename = clean_filename(article["title"]) + ".txt"

        filepath = os.path.join(
            "articles",
            "mfa",
            filename
        )

        with open(filepath, "w", encoding="utf-8") as file:

            file.write(f"TITLE:\n{article['title']}\n\n")

            file.write(
                "SOURCE:\n"
                "PRC Ministry of Foreign Affairs\n\n"
            )

            file.write(f"URL:\n{article['url']}\n\n")

            file.write("ARTICLE TEXT:\n")

            file.write(article_text)


        rss_items.append({
            "title": article["title"],
            "url": article["url"],
            "text": article_text
        })

        print(f"Saved: {filepath}")


    except Exception as error:

        print(
            f"Error collecting "
            f"{article['url']}: {error}"
        )


# Build RSS feed
feed = FeedGenerator()

feed.id(url)

feed.title(
    "PRC Ministry of Foreign Affairs - English"
)

feed.description(
    "Recent articles from the PRC Ministry "
    "of Foreign Affairs English website."
)

feed.link(
    href=url,
    rel="alternate"
)

feed.language("en")


for article in rss_items:

    entry = feed.add_entry()

    entry.id(article["url"])

    entry.title(article["title"])

    entry.link(
        href=article["url"]
    )

    entry.description(
        article["text"]
    )


feed.rss_file(
    "feeds/mfa-en.xml",
    pretty=True
)

print("Created RSS feed: feeds/mfa-en.xml")
