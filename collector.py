import os
import re
import json
import time
import requests
import trafilatura

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from feedgen.feed import FeedGenerator
from datetime import date, datetime, time as dt_time, timezone


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

ARTICLE_TARGET = 10
CANDIDATE_LIMIT = 30

MAX_RETRIES = 4
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8",
    "Connection": "close",
}


# ============================================================
# HTTP REQUEST WITH RETRIES
# ============================================================

def get_with_retry(url):

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            print(
                f"Request attempt {attempt}/{MAX_RETRIES}: {url}"
            )

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()

            return response

        except requests.RequestException as error:

            last_error = error

            print(f"Request failed: {error}")

            if attempt < MAX_RETRIES:

                wait_seconds = attempt * 5

                print(
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

    raise last_error


# ============================================================
# HELPERS
# ============================================================

def clean_filename(title):

    title = re.sub(
        r'[\\/:*?"<>|]',
        '',
        title
    )

    title = re.sub(
        r'\s+',
        ' ',
        title
    ).strip()

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

    if (
        full_url.rstrip("/")
        == source["url"].rstrip("/")
    ):
        return False

    lower_url = full_url.lower()

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

    if any(
        pattern in lower_url
        for pattern in article_patterns
    ):
        return True

    path_parts = [
        part
        for part in parsed.path.split("/")
        if part
    ]

    if (
        len(path_parts) >= 2
        and len(title) >= 12
    ):
        return True

    return False


# ============================================================
# PUBLICATION DATE HELPERS
# ============================================================

def parse_date_string(value):

    if not value:
        return None

    value = str(value).strip()

    patterns = [

        # 2026-08-19
        r'(?<!\d)(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})(?!\d)',

        # 2026年8月19日
        r'(?<!\d)(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日',

        # 20260819
        r'(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)',
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            value
        )

        if match:

            try:

                parsed_date = date(
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3))
                )

                return parsed_date.isoformat()

            except ValueError:
                pass

    return None


def find_date_in_json(data):

    if isinstance(data, dict):

        for key, value in data.items():

            if key.lower() in (
                "datepublished",
                "datecreated",
                "uploaddate",
                "pubdate",
                "publishdate",
            ):

                parsed = parse_date_string(value)

                if parsed:
                    return parsed

        for value in data.values():

            result = find_date_in_json(value)

            if result:
                return result

    elif isinstance(data, list):

        for item in data:

            result = find_date_in_json(item)

            if result:
                return result

    return None


def extract_publication_date(response, article_url):

    soup = BeautifulSoup(
        response.content,
        "html.parser"
    )


    # --------------------------------------------------------
    # 1. META TAGS
    # --------------------------------------------------------

    meta_keys = (
        "article:published_time",
        "og:published_time",
        "datepublished",
        "date",
        "pubdate",
        "publishdate",
        "publication_date",
        "publish_date",
        "dc.date",
        "dcterms.date",
    )

    for meta in soup.find_all("meta"):

        key = (
            meta.get("property")
            or meta.get("name")
            or meta.get("itemprop")
            or ""
        ).lower()

        if key in meta_keys:

            parsed = parse_date_string(
                meta.get("content")
            )

            if parsed:
                return parsed


    # --------------------------------------------------------
    # 2. JSON-LD
    # --------------------------------------------------------

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:

            data = json.loads(
                script.string or script.get_text()
            )

            parsed = find_date_in_json(data)

            if parsed:
                return parsed

        except Exception:
            pass


    # --------------------------------------------------------
    # 3. HTML <time> TAGS
    # --------------------------------------------------------

    for time_tag in soup.find_all("time"):

        parsed = parse_date_string(
            time_tag.get("datetime")
            or time_tag.get_text(
                " ",
                strip=True
            )
        )

        if parsed:
            return parsed


    # --------------------------------------------------------
    # 4. COMMON DATE/TIME ELEMENTS
    # --------------------------------------------------------

    date_elements = soup.find_all(
        attrs={
            "class": re.compile(
                r"(date|time|publish|pubtime)",
                re.I
            )
        }
    )

    for element in date_elements[:20]:

        parsed = parse_date_string(
            element.get_text(
                " ",
                strip=True
            )
        )

        if parsed:
            return parsed


    # --------------------------------------------------------
    # 5. ARTICLE URL FALLBACK
    # --------------------------------------------------------

    parsed = parse_date_string(
        article_url
    )

    if parsed:
        return parsed


    # No reliable date found
    return None


# ============================================================
# ARTICLE EXTRACTION
# ============================================================

def extract_article(article_url):

    response = get_with_retry(
        article_url
    )

    article_text = trafilatura.extract(
        response.content,
        url=article_url,
        include_comments=False,
        include_links=False
    )


    # Fallback paragraph extraction
    if (
        not article_text
        or len(article_text.strip()) < 100
    ):

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        paragraphs = []

        for paragraph in soup.find_all("p"):

            paragraph_text = paragraph.get_text(
                " ",
                strip=True
            )

            if len(paragraph_text) > 30:

                paragraphs.append(
                    paragraph_text
                )

        article_text = "\n\n".join(
            paragraphs
        )


    published_date = extract_publication_date(
        response,
        article_url
    )


    return (
        article_text or "",
        published_date
    )


# ============================================================
# COLLECT ONE SOURCE
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
        "candidates_found": 0,
        "articles_attempted": 0,
        "articles_extracted": 0,
        "articles_failed": 0,
        "dates_found": 0,
        "error": "",
    }


    # --------------------------------------------------------
    # DOWNLOAD SOURCE PAGE
    # --------------------------------------------------------

    try:

        response = get_with_retry(
            source["url"]
        )

    except Exception as error:

        result["status"] = "SOURCE FAILED"
        result["error"] = str(error)

        print(
            f"SOURCE FAILED: {error}"
        )

        return result


    soup = BeautifulSoup(
        response.content,
        "html.parser"
    )


    # --------------------------------------------------------
    # FIND CANDIDATE ARTICLE LINKS
    # --------------------------------------------------------

    candidates = []
    seen_urls = set()


    for link in soup.find_all(
        "a",
        href=True
    ):

        title = link.get_text(
            " ",
            strip=True
        )

        full_url = urljoin(
            source["url"],
            link["href"]
        )

        full_url = full_url.split("#")[0]

        if full_url in seen_urls:
            continue

        if valid_article_link(
            source,
            title,
            full_url
        ):

            seen_urls.add(
                full_url
            )

            candidates.append({
                "title": title,
                "url": full_url
            })

        if len(candidates) >= CANDIDATE_LIMIT:
            break


    result["candidates_found"] = len(
        candidates
    )

    print(
        f"Candidate article links found: "
        f"{len(candidates)}"
    )


    # --------------------------------------------------------
    # OUTPUT FOLDERS
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
    # TRY CANDIDATES UNTIL 10 GOOD ARTICLES ARE FOUND
    # --------------------------------------------------------

    for article in candidates:

        if (
            result["articles_extracted"]
            >= ARTICLE_TARGET
        ):
            break


        result["articles_attempted"] += 1


        print()
        print(
            f"Trying article: "
            f"{article['title']}"
        )


        try:

            article_text, published_date = extract_article(
                article["url"]
            )


            if (
                not article_text
                or len(article_text.strip()) < 100
            ):

                print(
                    "Skipped: not enough article text."
                )

                continue


            result["articles_extracted"] += 1


            if published_date:

                result["dates_found"] += 1

                print(
                    f"Published: {published_date}"
                )

            else:

                print(
                    "Published date not found."
                )


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


            # ------------------------------------------------
            # SAVE ARTICLE FILE
            # ------------------------------------------------

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
                    f"PUBLISHED:\n"
                    f"{published_date or 'Unknown'}\n\n"
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
                "text": article_text,
                "published_date": published_date,
            })


            print(
                f"Saved: {filepath}"
            )


        except Exception as error:

            print(
                f"ARTICLE FAILED: "
                f"{article['url']}"
            )

            print(
                f"ERROR: {error}"
            )


    result["articles_failed"] = (
        result["articles_attempted"]
        - result["articles_extracted"]
    )


    # --------------------------------------------------------
    # CREATE RSS FEED
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
            article["text"]
        )


        # ----------------------------------------------------
        # RSS PUBLICATION DATE
        # ----------------------------------------------------

        if article["published_date"]:

            published = datetime.combine(
                date.fromisoformat(
                    article["published_date"]
                ),
                dt_time.min,
                tzinfo=timezone.utc
            )

            entry.pubDate(
                published
            )


    feed_path = os.path.join(
        "feeds",
        source["slug"] + ".xml"
    )


    feed.rss_file(
        feed_path,
        pretty=True
    )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if result["candidates_found"] == 0:

        result["status"] = (
            "NO ARTICLES FOUND"
        )

    elif (
        result["articles_extracted"]
        >= ARTICLE_TARGET
    ):

        result["status"] = "WORKING"

    elif result["articles_extracted"] > 0:

        result["status"] = "PARTIAL"

    else:

        result["status"] = (
            "LINKS FOUND - TEXT FAILED"
        )


    print()
    print(
        f"STATUS: "
        f"{result['status']}"
    )

    print(
        f"Articles with publication date: "
        f"{result['dates_found']}"
    )

    print(
        f"RSS: {feed_path}"
    )


    return result


# ============================================================
# RUN ALL SOURCES
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
            "candidates_found": 0,
            "articles_attempted": 0,
            "articles_extracted": 0,
            "articles_failed": 0,
            "dates_found": 0,
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
            f"CANDIDATE LINKS FOUND: "
            f"{result['candidates_found']}\n"
        )

        report.write(
            f"ARTICLES ATTEMPTED: "
            f"{result['articles_attempted']}\n"
        )

        report.write(
            f"ARTICLES WITH TEXT: "
            f"{result['articles_extracted']}\n"
        )

        report.write(
            f"ARTICLES WITH PUB DATE: "
            f"{result['dates_found']}\n"
        )

        report.write(
            f"ARTICLES SKIPPED/FAILED: "
            f"{result['articles_failed']}\n"
        )

        report.write(
            f"RSS FEED: "
            f"feeds/{result['slug']}.xml\n"
        )

        if result["error"]:

            report.write(
                f"ERROR: "
                f"{result['error']}\n"
            )

        report.write(
            "\n"
            + "-" * 70
            + "\n\n"
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

working = sum(
    1
    for result in results
    if result["status"] == "WORKING"
)

partial = sum(
    1
    for result in results
    if result["status"] == "PARTIAL"
)

failed = (
    len(results)
    - working
    - partial
)


print()
print("=" * 80)
print("COLLECTION COMPLETE")
print("=" * 80)

print(
    f"Fully working: "
    f"{working}/{len(results)}"
)

print(
    f"Partial: "
    f"{partial}/{len(results)}"
)

print(
    f"Failed: "
    f"{failed}/{len(results)}"
)

print(
    "See feeds/status-report.txt "
    "for details."
)
