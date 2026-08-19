import os
import re
import requests
import trafilatura

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from feedgen.feed import FeedGenerator


# ============================================================
# ORIGINAL SOURCE LIST
# ============================================================

sources = [

    # Diplomacy / Foreign Relations
    {
        "name": "MFA English",
        "slug": "mfa-en",
        "category": "Diplomacy",
        "url": "https://www.mfa.gov.cn/eng/xw/fyrbt/",
        "domain": "mfa.gov.cn",
        "language": "en",
    },
    {
        "name": "MFA Chinese",
        "slug": "mfa-cn",
        "category": "Diplomacy",
        "url": "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/",
        "domain": "mfa.gov.cn",
        "language": "zh",
    },

    # Military
    {
        "name": "China Military English",
        "slug": "chinamil-en",
        "category": "Military",
        "url": "http://eng.chinamil.com.cn/index.html",
        "domain": "chinamil.com.cn",
        "language": "en",
    },
    {
        "name": "81 CN",
        "slug": "81-cn",
        "category": "Military",
        "url": "http://www.81.cn/?big=jian",
        "domain": "81.cn",
        "language": "zh",
    },
    {
        "name": "CCTV 7",
        "slug": "cctv7",
        "category": "Military",
        "url": "https://tv.cctv.com/cctv7/",
        "domain": "cctv.com",
        "language": "zh",
    },
    {
        "name": "Global Times Military",
        "slug": "globaltimes-military",
        "category": "Military",
        "url": "https://www.globaltimes.cn/china/military/index.html",
        "domain": "globaltimes.cn",
        "language": "en",
    },

    # Economic
    {
        "name": "MOFCOM English",
        "slug": "mofcom-en",
        "category": "Economic",
        "url": "https://english.mofcom.gov.cn/",
        "domain": "mofcom.gov.cn",
        "language": "en",
    },
    {
        "name": "MOFCOM Chinese",
        "slug": "mofcom-cn",
        "category": "Economic",
        "url": "https://www.mofcom.gov.cn/",
        "domain": "mofcom.gov.cn",
        "language": "zh",
    },
    {
        "name": "National Bureau Statistics English",
        "slug": "stats-en",
        "category": "Economic",
        "url": "https://www.stats.gov.cn/english/",
        "domain": "stats.gov.cn",
        "language": "en",
    },
    {
        "name": "National Bureau Statistics Chinese",
        "slug": "stats-cn",
        "category": "Economic",
        "url": "https://www.stats.gov.cn/",
        "domain": "stats.gov.cn",
        "language": "zh",
    },

    # Taiwan
    {
        "name": "Taiwan Affairs Office",
        "slug": "gwyta-cn",
        "category": "Taiwan",
        "url": "https://www.gwytb.gov.cn/",
        "domain": "gwytb.gov.cn",
        "language": "zh",
    },
    {
        "name": "Taiwan CN English",
        "slug": "taiwan-en",
        "category": "Taiwan",
        "url": "https://eng.taiwan.cn/",
        "domain": "taiwan.cn",
        "language": "en",
    },
    {
        "name": "Taiwan CN Chinese",
        "slug": "taiwan-cn",
        "category": "Taiwan",
        "url": "https://www.taiwan.cn/",
        "domain": "taiwan.cn",
        "language": "zh",
    },

    # PRC Non-Authoritative Media
    {
        "name": "Global Times",
        "slug": "globaltimes",
        "category": "PRC Non-Authoritative Media",
        "url": "https://www.globaltimes.cn/",
        "domain": "globaltimes.cn",
        "language": "en",
    },

    # Authoritative PRC Media
    {
        "name": "People Daily English",
        "slug": "people-en",
        "category": "Authoritative PRC Media",
        "url": "https://en.people.cn/",
        "domain": "en.people.cn",
        "language": "en",
    },
    {
        "name": "People Daily Chinese",
        "slug": "people-cn",
        "category": "Authoritative PRC Media",
        "url": "https://www.people.com.cn/",
        "domain": "people.com.cn",
        "language": "zh",
    },
    {
        "name": "People Military",
        "slug": "people-military",
        "category": "Authoritative PRC Media",
        "url": "http://military.people.com.cn/",
        "domain": "people.com.cn",
        "language": "zh",
    },
    {
        "name": "Qiushi English",
        "slug": "qiushi-en",
        "category": "Authoritative PRC Media",
        "url": "https://en.qstheory.cn/",
        "domain": "qstheory.cn",
        "language": "en",
    },
    {
        "name": "Qiushi Chinese",
        "slug": "qiushi-cn",
        "category": "Authoritative PRC Media",
        "url": "https://www.qstheory.cn/",
        "domain": "qstheory.cn",
        "language": "zh",
    },
    {
        "name": "Xinhua English",
        "slug": "xinhua-en",
        "category": "Authoritative PRC Media",
        "url": "https://english.news.cn/",
        "domain": "news.cn",
        "language": "en",
    },
    {
        "name": "Xinhua Chinese",
        "slug": "xinhua-cn",
        "category": "Authoritative PRC Media",
        "url": "https://www.news.cn/",
        "domain": "news.cn",
        "language": "zh",
    },
    {
        "name": "China Daily English",
        "slug": "chinadaily-en",
        "category": "Authoritative PRC Media",
        "url": "https://www.chinadaily.com.cn/",
        "domain": "chinadaily.com.cn",
        "language": "en",
    },
    {
        "name": "China Daily Chinese",
        "slug": "chinadaily-cn",
        "category": "Authoritative PRC Media",
        "url": "https://cn.chinadaily.com.cn/",
        "domain": "chinadaily.com.cn",
        "language": "zh",
    },
    {
        "name": "CCTV English",
        "slug": "cctv-en",
        "category": "Authoritative PRC Media",
        "url": "https://english.cctv.com/",
        "domain": "cctv.com",
        "language": "en",
    },
    {
        "name": "CCTV Chinese",
        "slug": "cctv-cn",
        "category": "Authoritative PRC Media",
        "url": "https://www.cctv.com/",
        "domain": "cctv.com",
        "language": "zh",
    },
    {
        "name": "PRC Government English",
        "slug": "gov-en",
        "category": "Authoritative PRC Media",
        "url": "https://english.www.gov.cn/",
        "domain": "english.www.gov.cn",
        "language": "en",
    },
    {
        "name": "PRC Government Chinese",
        "slug": "gov-cn",
        "category": "Authoritative PRC Media",
        "url": "https://www.gov.cn/",
        "domain": "www.gov.cn",
        "language": "zh",
    },
]


# ============================================================
# SETTINGS
# ============================================================

ARTICLE_LIMIT = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/131.0 Safari/537.36"
    )
}


# ============================================================
# HELPERS
# ============================================================

def clean_filename(title):

    title = re.sub(r'[\\/:*?"<>|]', '', title)

    title = re.sub(r'\s+', ' ', title).strip()

    # Prevent extremely long filenames
    return title[:180]


def valid_article_link(source, title, full_url):

    if not title:
        return False

    if len(title.strip()) < 6:
        return False

    parsed = urlparse(full_url)

    if parsed.scheme not in ("http", "https"):
        return False

    hostname = parsed.hostname or ""

    if source["domain"] not in hostname:
        return False

    # Don't treat the source homepage itself as an article
    if full_url.rstrip("/") == source["url"].rstrip("/"):
        return False

    lower_url = full_url.lower()

    # Ignore obvious non-article files
    bad_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".pdf",
        ".zip",
        ".mp3",
        ".mp4",
        ".css",
        ".js",
    )

    if lower_url.endswith(bad_extensions):
        return False

    # Ignore obvious navigation text
    bad_titles = {
        "home",
        "english",
        "中文",
        "more",
        "more >>",
        "next",
        "previous",
        "about us",
        "contact us",
    }

    if title.lower().strip() in bad_titles:
        return False

    # Prefer links that look like articles
    article_patterns = [
        ".html",
        ".shtml",
        ".htm",
        "/2026",
        "/2025",
        "content",
        "article",
        "news",
        "t20",
    ]

    if any(pattern in lower_url for pattern in article_patterns):
        return True

    # Allow deeper URLs with meaningful titles
    path_parts = [
        part
        for part in parsed.path.split("/")
        if part
    ]

    if len(path_parts) >= 2 and len(title) >= 12:
        return True

    return False


def extract_text(article_url):

    response = requests.get(
        article_url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    text = trafilatura.extract(
        response.content,
        url=article_url,
        include_comments=False,
        include_links=False
    )

    # Fallback if Trafilatura cannot identify the article body
    if not text or len(text.strip()) < 100:

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        paragraphs = []

        for p in soup.find_all("p"):

            paragraph = p.get_text(
                " ",
                strip=True
            )

            if len(paragraph) > 30:
                paragraphs.append(paragraph)

        text = "\n\n".join(paragraphs)

    return text or ""


# ============================================================
# COLLECT SOURCE
# ============================================================

def collect_source(source):

    print()
    print("=" * 80)
    print(source["name"])
    print(source["url"])
    print("=" * 80)

    result = {
        "name": source["name"],
        "slug": source["slug"],
        "url": source["url"],
        "status": "UNKNOWN",
        "links_found": 0,
        "articles_extracted": 0,
        "error": "",
    }

    try:

        response = requests.get(
            source["url"],
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

    except Exception as error:

        result["status"] = "SOURCE FAILED"
        result["error"] = str(error)

        print(f"SOURCE FAILED: {error}")

        return result


    soup = BeautifulSoup(
        response.content,
        "html.parser"
    )


    articles = []
    seen_urls = set()


    for link in soup.find_all("a", href=True):

        title = link.get_text(
            " ",
            strip=True
        )

        full_url = urljoin(
            source["url"],
            link["href"]
        )

        # Remove fragments
        full_url = full_url.split("#")[0]

        if full_url in seen_urls:
            continue

        if valid_article_link(
            source,
            title,
            full_url
        ):

            seen_urls.add(full_url)

            articles.append({
                "title": title,
                "url": full_url
            })

        if len(articles) >= ARTICLE_LIMIT:
            break


    result["links_found"] = len(articles)

    print(
        f"Article links found: "
        f"{len(articles)}"
    )


    # --------------------------------------------------------
    # FOLDERS
    # --------------------------------------------------------

    article_folder = os.path.join(
        "articles",
        source["slug"]
    )

    os.makedirs(
        article_folder,
        exist_ok=True
    )

    os.makedirs(
        "feeds",
        exist_ok=True
    )


    rss_items = []


    # --------------------------------------------------------
    # ARTICLE EXTRACTION
    # --------------------------------------------------------

    for article in articles:

        print(
            f"Trying: {article['title']}"
        )

        try:

            article_text = extract_text(
                article["url"]
            )

            if article_text:

                result["articles_extracted"] += 1


                filename = (
                    clean_filename(
                        article["title"]
                    )
                    + ".txt"
                )


                filepath = os.path.join(
                    article_folder,
                    filename
                )


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
                        f"CATEGORY:\n"
                        f"{source['category']}\n\n"
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


        except Exception as error:

            print(
                f"ARTICLE FAILED: "
                f"{article['url']} "
                f"{error}"
            )


    # --------------------------------------------------------
    # RSS FEED
    # --------------------------------------------------------

    feed = FeedGenerator()

    feed.id(
        source["url"]
    )

    feed.title(
        source["name"]
    )

    feed.description(
        f"{source['category']} feed generated "
        f"from {source['url']}"
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
            article["text"] or ""
        )


    feed_path = os.path.join(
        "feeds",
        source["slug"] + ".xml"
    )


    feed.rss_file(
        feed_path,
        pretty=True
    )


    if result["articles_extracted"] > 0:

        result["status"] = "WORKING"

    elif result["links_found"] > 0:

        result["status"] = "LINKS FOUND - TEXT FAILED"

    else:

        result["status"] = "NO ARTICLES FOUND"


    print(
        f"STATUS: {result['status']}"
    )

    print(
        f"RSS: {feed_path}"
    )


    return result


# ============================================================
# RUN EVERYTHING
# ============================================================

results = []


for source in sources:

    try:

        result = collect_source(
            source
        )

        results.append(
            result
        )

    except Exception as error:

        results.append({
            "name": source["name"],
            "slug": source["slug"],
            "url": source["url"],
            "status": "SCRIPT ERROR",
            "links_found": 0,
            "articles_extracted": 0,
            "error": str(error),
        })


# ============================================================
# STATUS REPORT
# ============================================================

report_path = os.path.join(
    "feeds",
    "status-report.txt"
)


with open(
    report_path,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "PRC RSS COLLECTOR STATUS REPORT\n"
    )

    report.write(
        "=" * 70 + "\n\n"
    )


    for result in results:

        report.write(
            f"SOURCE: {result['name']}\n"
        )

        report.write(
            f"URL: {result['url']}\n"
        )

        report.write(
            f"STATUS: {result['status']}\n"
        )

        report.write(
            f"ARTICLE LINKS FOUND: "
            f"{result['links_found']}\n"
        )

        report.write(
            f"ARTICLES WITH TEXT: "
            f"{result['articles_extracted']}\n"
        )

        report.write(
            f"RSS FEED: "
            f"feeds/{result['slug']}.xml\n"
        )

        if result["error"]:

            report.write(
                f"ERROR: {result['error']}\n"
            )

        report.write(
            "\n" + "-" * 70 + "\n\n"
        )


# ============================================================
# SUMMARY
# ============================================================

working = sum(
    1
    for result in results
    if result["status"] == "WORKING"
)

failed = len(results) - working


print()
print("=" * 80)
print("COLLECTION COMPLETE")
print("=" * 80)

print(
    f"Working sources: "
    f"{working}/{len(results)}"
)

print(
    f"Sources needing attention: "
    f"{failed}"
)

print(
    "See feeds/status-report.txt "
    "for details."
)
