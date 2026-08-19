import os
import re
import requests
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://www.mfa.gov.cn/eng/xw/fyrbt/"

response = requests.get(url, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.content, "html.parser")

articles = []

# Find the 10 most recent article links
for link in soup.find_all("a", href=True):
    title = link.get_text(" ", strip=True)
    full_url = urljoin(url, link["href"])

    if "/eng/xw/fyrbt/" in full_url and full_url.endswith(".html") and title:

        if not any(article["url"] == full_url for article in articles):
            articles.append({
                "title": title,
                "url": full_url
            })

    if len(articles) >= 10:
        break


# Create folder for saved articles
os.makedirs("articles/mfa", exist_ok=True)


def clean_filename(title):
    # Remove characters that are unsafe in filenames
    title = re.sub(r'[\\/:*?"<>|]', '', title)

    # Remove extra spaces
    title = re.sub(r'\s+', ' ', title).strip()

    return title


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

        filename = clean_filename(article["title"]) + ".txt"

        filepath = os.path.join(
            "articles",
            "mfa",
            filename
        )

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"TITLE:\n{article['title']}\n\n")
            file.write(f"SOURCE:\nPRC Ministry of Foreign Affairs\n\n")
            file.write(f"URL:\n{article['url']}\n\n")
            file.write("ARTICLE TEXT:\n")
            file.write(article_text or "")

        print(f"Saved: {filepath}")

    except Exception as error:
        print(f"Error collecting {article['url']}: {error}")
