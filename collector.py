import os
import re
import requests
import trafilatura

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from feedgen.feed import FeedGenerator


sources = [
    {
        "name": "PRC Ministry of Foreign Affairs - English",
        "url": "https://www.mfa.gov.cn/eng/xw/fyrbt/",
        "path_match": "/eng/xw/fyrbt/",
        "article_folder": "articles/mfa",
        "feed_file": "feeds/mfa-en.xml",
        "language": "en",
    },
    {
        "name": "PRC Ministry of Foreign Affairs - Chinese",
        "url": "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/",
        "path_match": "/web/wjdt_674879/fyrbt_674889/",
        "article_folder": "articles/mfa-cn",
        "feed_file": "feeds/mfa-cn.xml",
        "language": "zh",
    },
]


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/131 Safari/537.36"
    )
}


ARTICLE_LIMIT = 10


def clean_filename(title):
    title = re.sub(r'[\\/:*?"<>|]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def collect_source(source):

    print("=" * 80)
    print(f"Collecting: {source['name']}")
    print("=" * 80)

    response = requests.get(
        source["url"],
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.content,
        "html.parser"
    )

    articles = []

    # Find recent article links
    for link in soup.find_all("a", href=True):

        title = link.get_text(
            " ",
            strip=True
        )

        full_url = urljoin(
            source["url"],
            link["href"]
        )

        if (
            source["path_match"] in full_url
            and full_url.endswith((".html", ".shtml"))
            and title
        ):

            # Avoid duplicate URLs
            if not any(
                article["url"] == full_url
                for article in articles
            ):

                articles.append({
                    "title": title,
                    "url": full_url
                })

        if len(articles) >= ARTICLE_LIMIT:
            break


    print(
        f"Found {len(articles)} recent articles."
    )


    # Create folders
    os.makedirs(
        source["article_folder"],
        exist_ok=True
    )

    os.makedirs(
        "feeds",
        exist_ok=True
    )


    rss_items = []


    # Download each article
    for article in articles:

        try:

            print(
                f"Downloading: {article['title']}"
            )

            article_response = requests.get(
                article["url"],
                headers=HEADERS,
                timeout=30
            )

            article_response.raise_for_status()


            article_text = trafilatura.extract(
                article_response.content,
                url=article["url"],
                include_comments=False,
                include_links=False
            )

            article_text = article_text or ""


            # Create filename from article title
            filename = (
                clean_filename(
                    article["title"]
                )
                + ".txt"
            )


            filepath = os.path.join(
                source["article_folder"],
                filename
            )


            # Save individual article file
            with open(
                filepath,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    f"TITLE:\n"
                    f"{article['title']}\n\n"
                )

                file.write(
                    f"SOURCE:\n"
                    f"{source['name']}\n\n"
                )

                file.write(
                    f"URL:\n"
                    f"{article['url']}\n\n"
                )

                file.write(
                    "ARTICLE TEXT:\n"
                )

                file.write(
                    article_text
                )


            rss_items.append({
                "title": article["title"],
                "url": article["url"],
                "text": article_text
            })


            print(
                f"Saved: {filepath}"
            )


        except Exception as error:

            print(
                f"Error collecting "
                f"{article['url']}: "
                f"{error}"
            )


    # Create RSS feed
    feed = FeedGenerator()

    feed.id(
        source["url"]
    )

    feed.title(
        source["name"]
    )

    feed.description(
        f"Recent articles from "
        f"{source['name']}."
    )

    feed.link(
        href=source["url"],
        rel="alternate"
    )

    feed.language(
        source["language"]
    )


    for article in rss_items:

        entry = feed.add_entry()

        entry.id(
            article["url"]
        )

        entry.title(
            article["title"]
        )

        entry.link(
            href=article["url"]
        )

        entry.description(
            article["text"]
        )


    feed.rss_file(
        source["feed_file"],
        pretty=True
    )


    print(
        f"Created RSS feed: "
        f"{source['feed_file']}"
    )

    print()


# Run all configured sources
for source in sources:

    collect_source(source)
