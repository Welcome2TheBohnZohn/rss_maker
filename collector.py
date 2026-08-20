import os
import re
import json
import time
import requests
import trafilatura

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from feedgen.feed import FeedGenerator
from datetime import datetime, timedelta, timezone


# ============================================================
# SOURCE LIST
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
# SOURCE-SPECIFIC FILTERS
# ============================================================

SOURCE_FILTERS = {

    "mfa-cn": {
        "allow_url_regex": (
            r"^https?://www\.mfa\.gov\.cn/"
            r"web/wjdt_674879/fyrbt_674889/"
            r"\d{6}/t\d+_\d+\.shtml$"
        )
    },

    "cctv7": {
        "allow_url_regex": (
            r"^https?://tv\.cctv\.com/"
            r"20\d{2}/\d{2}/\d{2}/"
            r"VIDE[^/]+\.shtml$"
        )
    },

    "people-en": {
        "allow_url_regex": (
            r"^https?://en\.people\.cn/"
            r"n3/20\d{2}/\d{4}/"
            r"c\d+-\d+\.html$"
        )
    },

    "people-cn": {
        "allow_url_regex": (
            r"^https?://(?:[a-zA-Z0-9-]+\.)*"
            r"people\.com\.cn/"
            r"n1/20\d{2}/\d{4}/"
            r"c\d+-\d+\.html$"
        )
    },

    "qiushi-en": {
        "allow_url_regex": (
            r"^https?://en\.qstheory\.cn/"
            r"20\d{2}-\d{2}/\d{2}/"
            r"c_\d+\.htm$"
        )
    },

    "xinhua-en": {
        "allow_url_regex": (
            r"^https?://english\.news\.cn/"
            r"20\d{6}/"
            r"[0-9a-fA-F]+/"
            r"c\.html$"
        )
    },

    "xinhua-cn": {
        "allow_url_regex": (
            r"^https?://www\.news\.cn/"
            r"(?:[^/]+/)?"
            r"20\d{6}/"
            r"[0-9a-fA-F]+/"
            r"c\.html$"
        )
    },

    "chinadaily-en": {
        "allow_url_regex": (
            r"^https?://www\.chinadaily\.com\.cn/"
            r"a/20\d{4}/\d{2}/"
            r"WS[^/]+\.html$"
        )
    },

    "cctv-en": {
        "allow_url_regex": (
            r"^https?://english\.cctv\.com/"
            r"20\d{2}/\d{2}/\d{2}/"
            r"(?:ARTI|VIDE)[^/]+\.shtml$"
        )
    },

    "cctv-cn": {
        "allow_url_regex": (
            r"^https?://(?:news|tv)\.cctv\.com/"
            r"20\d{2}/\d{2}/\d{2}/"
            r"(?:ARTI|VIDE)[^/]+\.shtml$"
        )
    },
}


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
# HTTP REQUESTS
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
# FILENAME
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


# ============================================================
# CCTV ENGLISH TITLE CLEANUP
# ============================================================

def looks_like_duration(title):

    if not title:
        return False

    title = title.strip()

    return bool(
        re.fullmatch(
            r"\d{1,2}:\d{2}(?::\d{2})?",
            title
        )
    )


def clean_cctv_page_title(title):

    if not title:
        return ""

    title = re.sub(
        r'\s+',
        ' ',
        title
    ).strip()

    # Remove common CCTV suffixes from HTML <title>.
    title = re.sub(
        r'\s*[-_|]\s*CCTV(?:\.com)?(?:\s+English)?\s*$',
        '',
        title,
        flags=re.I
    ).strip()

    title = re.sub(
        r'\s*[-_|]\s*央视网\s*$',
        '',
        title
    ).strip()

    return title


def extract_best_title(
    source,
    original_title,
    response
):

    # Only alter CCTV English items whose original
    # homepage title is clearly just a video duration.
    if source["slug"] != "cctv-en":
        return original_title

    if not looks_like_duration(
        original_title
    ):
        return original_title

    soup = BeautifulSoup(
        response.content,
        "html.parser"
    )

    title_candidates = []

    # --------------------------------------------------------
    # OpenGraph title
    # --------------------------------------------------------

    og_title = soup.find(
        "meta",
        property="og:title"
    )

    if (
        og_title
        and og_title.get("content")
    ):

        title_candidates.append(
            og_title.get("content")
        )

    # --------------------------------------------------------
    # Twitter title
    # --------------------------------------------------------

    twitter_title = soup.find(
        "meta",
        attrs={
            "name": "twitter:title"
        }
    )

    if (
        twitter_title
        and twitter_title.get("content")
    ):

        title_candidates.append(
            twitter_title.get("content")
        )

    # --------------------------------------------------------
    # Main H1
    # --------------------------------------------------------

    h1 = soup.find("h1")

    if h1:

        title_candidates.append(
            h1.get_text(
                " ",
                strip=True
            )
        )

    # --------------------------------------------------------
    # Standard HTML title
    # --------------------------------------------------------

    if soup.title:

        title_candidates.append(
            soup.title.get_text(
                " ",
                strip=True
            )
        )

    # --------------------------------------------------------
    # Choose first useful title
    # --------------------------------------------------------

    for candidate in title_candidates:

        candidate = clean_cctv_page_title(
            candidate
        )

        if not candidate:
            continue

        if looks_like_duration(
            candidate
        ):
            continue

        if len(candidate) < 6:
            continue

        return candidate

    # If nothing better was found, preserve original title.
    return original_title


# ============================================================
# SOURCE FILTER
# ============================================================

def passes_source_filter(
    source,
    title,
    full_url
):

    rules = SOURCE_FILTERS.get(
        source["slug"]
    )

    if not rules:
        return True

    allow_regex = rules.get(
        "allow_url_regex"
    )

    if allow_regex:

        if not re.search(
            allow_regex,
            full_url,
            re.I
        ):
            return False

    return True


# ============================================================
# GENERIC ARTICLE LINK CHECK
# ============================================================

def valid_article_link(
    source,
    title,
    full_url
):

    if not title:
        return False

    title = title.strip()

    if len(title) < 6:
        return False

    parsed = urlparse(
        full_url
    )

    if parsed.scheme not in (
        "http",
        "https"
    ):
        return False

    hostname = (
        parsed.hostname or ""
    )

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

    if lower_url.endswith(
        bad_extensions
    ):
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
        "search",
        "site search",
        "video & live",
        "special reports",
        "global view",
        "we are china",
        "exclusive",
        "xi's moments",
        "xi’s moments",
        "xi's works",
        "xi’s works",
        "deutsch",
        "русский язык",
        "español",
        "français",
        "português",
        "日本語",
        "한국어",
    }

    if title.lower() in bad_titles:
        return False

    if not passes_source_filter(
        source,
        title,
        full_url
    ):
        return False

    if source["slug"] in SOURCE_FILTERS:
        return True

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
# FIND LINKS ON A PAGE
# ============================================================

def find_candidate_links(
    source,
    page_url,
    response,
    existing_urls=None
):

    if existing_urls is None:
        existing_urls = set()

    soup = BeautifulSoup(
        response.content,
        "html.parser"
    )

    candidates = []

    for link in soup.find_all(
        "a",
        href=True
    ):

        title = link.get_text(
            " ",
            strip=True
        )

        full_url = urljoin(
            page_url,
            link["href"]
        )

        full_url = (
            full_url.split("#")[0]
        )

        if full_url in existing_urls:
            continue

        if valid_article_link(
            source,
            title,
            full_url
        ):

            existing_urls.add(
                full_url
            )

            candidates.append({
                "title": title,
                "url": full_url
            })

        if (
            len(candidates)
            >= CANDIDATE_LIMIT
        ):
            break

    return candidates


# ============================================================
# CCTV-7 SPECIAL DISCOVERY
# ============================================================

def discover_cctv7_candidates(
    source,
    homepage_response
):

    soup = BeautifulSoup(
        homepage_response.content,
        "html.parser"
    )

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

        full_url = (
            full_url.split("#")[0]
        )

        # Only real dated CCTV video pages.
        if not re.search(
            r"^https?://tv\.cctv\.com/"
            r"20\d{2}/\d{2}/\d{2}/"
            r"VIDE[^/]+\.shtml$",
            full_url,
            re.I
        ):
            continue

        if full_url in seen_urls:
            continue

        if not title:
            continue

        seen_urls.add(
            full_url
        )

        candidates.append({
            "title": title,
            "url": full_url
        })

    # Sort by the date contained in the URL.
    def video_date(item):

        match = re.search(
            r"/(20\d{2})/(\d{2})/(\d{2})/",
            item["url"]
        )

        if match:

            return (
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3))
            )

        return (
            0,
            0,
            0
        )

    candidates.sort(
        key=video_date,
        reverse=True
    )

    return candidates[
        :CANDIDATE_LIMIT
    ]


# ============================================================
# DATE / TIME PARSING
# ============================================================

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,

    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def timezone_from_string(value):

    if not value:
        return None

    value = (
        value.strip().upper()
    )

    if value == "Z":
        return timezone.utc

    match = re.fullmatch(
        r'([+-])(\d{2}):?(\d{2})',
        value
    )

    if not match:
        return None

    sign = (
        1
        if match.group(1) == "+"
        else -1
    )

    offset = timedelta(
        hours=int(
            match.group(2)
        ),
        minutes=int(
            match.group(3)
        )
    )

    return timezone(
        offset * sign
    )


def format_timezone(dt):

    if dt.tzinfo is None:
        return ""

    raw = dt.strftime(
        "%z"
    )

    if not raw:
        return ""

    return (
        raw[:3]
        + ":"
        + raw[3:]
    )


def timestamp_result(
    dt,
    has_time
):

    if has_time:

        display = dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    else:

        display = dt.strftime(
            "%Y-%m-%d"
        )

    if dt.tzinfo is not None:

        offset = format_timezone(
            dt
        )

        if offset:
            display += (
                " " + offset
            )

    return {
        "display": display,
        "datetime": dt,
        "has_time": has_time,
        "has_timezone": (
            dt.tzinfo is not None
        ),
    }


def timestamps_same_date(first, second):

    if not first or not second:
        return False

    first_dt = first.get("datetime")
    second_dt = second.get("datetime")

    if first_dt is None or second_dt is None:
        return False

    return (
        first_dt.year,
        first_dt.month,
        first_dt.day
    ) == (
        second_dt.year,
        second_dt.month,
        second_dt.day
    )


def parse_timestamp(value):

    if not value:
        return None

    value = str(
        value
    ).strip()

    value = re.sub(
        r'\s+',
        ' ',
        value
    )

    # --------------------------------------------------------
    # YYYY-MM-DD HH:MM[:SS]
    # --------------------------------------------------------

    match = re.search(
        r'(?<!\d)'
        r'(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})'
        r'[T\s]+'
        r'(\d{1,2}):(\d{2})'
        r'(?::(\d{2}))?'
        r'(?:\.\d+)?'
        r'\s*(Z|[+-]\d{2}:?\d{2})?'
        r'(?!\d)',
        value,
        re.I
    )

    if match:

        try:

            dt = datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                int(match.group(4)),
                int(match.group(5)),
                int(match.group(6) or 0),
                tzinfo=timezone_from_string(
                    match.group(7)
                )
            )

            return timestamp_result(
                dt,
                True
            )

        except ValueError:
            pass

    # --------------------------------------------------------
    # Chinese YYYY年MM月DD日 HH:MM
    # --------------------------------------------------------

    match = re.search(
        r'(?<!\d)'
        r'(20\d{2})年\s*'
        r'(\d{1,2})月\s*'
        r'(\d{1,2})日'
        r'(?:\s+'
        r'(\d{1,2}):(\d{2})'
        r'(?::(\d{2}))?'
        r')?',
        value
    )

    if match:

        try:

            has_time = bool(
                match.group(4)
            )

            dt = datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                int(match.group(4) or 0),
                int(match.group(5) or 0),
                int(match.group(6) or 0)
            )

            return timestamp_result(
                dt,
                has_time
            )

        except ValueError:
            pass

    # --------------------------------------------------------
    # HH:MM, August 20, 2026
    # --------------------------------------------------------

    month_names = (
        "January|February|March|April|May|June|July|"
        "August|September|October|November|December|"
        "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
    )

    match = re.search(
        rf'(\d{{1,2}}):(\d{{2}})'
        rf'(?:\s*(AM|PM))?'
        rf'\s*,?\s*'
        rf'({month_names})\s+'
        rf'(\d{{1,2}}),?\s+'
        rf'(20\d{{2}})',
        value,
        re.I
    )

    if match:

        try:

            hour = int(
                match.group(1)
            )

            minute = int(
                match.group(2)
            )

            am_pm = (
                match.group(3)
            )

            if am_pm:

                if (
                    am_pm.upper() == "PM"
                    and hour != 12
                ):
                    hour += 12

                elif (
                    am_pm.upper() == "AM"
                    and hour == 12
                ):
                    hour = 0

            month = MONTHS[
                match.group(4).lower()
            ]

            dt = datetime(
                int(match.group(6)),
                month,
                int(match.group(5)),
                hour,
                minute
            )

            return timestamp_result(
                dt,
                True
            )

        except (
            ValueError,
            KeyError
        ):
            pass

    # --------------------------------------------------------
    # August 20, 2026 [HH:MM]
    # --------------------------------------------------------

    match = re.search(
        rf'\b({month_names})\s+'
        r'(\d{1,2}),?\s+'
        r'(20\d{2})'
        r'(?:[,\s]+'
        r'(\d{1,2}):(\d{2})'
        r'(?::(\d{2}))?'
        r'\s*(AM|PM)?'
        r')?',
        value,
        re.I
    )

    if match:

        try:

            month = MONTHS[
                match.group(1).lower()
            ]

            hour = int(
                match.group(4) or 0
            )

            minute = int(
                match.group(5) or 0
            )

            second = int(
                match.group(6) or 0
            )

            am_pm = (
                match.group(7)
            )

            if am_pm:

                if (
                    am_pm.upper() == "PM"
                    and hour != 12
                ):
                    hour += 12

                elif (
                    am_pm.upper() == "AM"
                    and hour == 12
                ):
                    hour = 0

            dt = datetime(
                int(match.group(3)),
                month,
                int(match.group(2)),
                hour,
                minute,
                second
            )

            return timestamp_result(
                dt,
                bool(match.group(4))
            )

        except (
            ValueError,
            KeyError
        ):
            pass

    # --------------------------------------------------------
    # Numeric date only
    # --------------------------------------------------------

    match = re.search(
        r'(?<!\d)'
        r'(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})'
        r'(?!\d)',
        value
    )

    if match:

        try:

            dt = datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3))
            )

            return timestamp_result(
                dt,
                False
            )

        except ValueError:
            pass

    # --------------------------------------------------------
    # Compact YYYYMMDD
    # --------------------------------------------------------

    match = re.search(
        r'(?<!\d)'
        r'(20\d{2})(\d{2})(\d{2})'
        r'(?!\d)',
        value
    )

    if match:

        try:

            dt = datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3))
            )

            return timestamp_result(
                dt,
                False
            )

        except ValueError:
            pass

    return None


# ============================================================
# JSON-LD TIMESTAMP SEARCH
# ============================================================

def find_timestamp_in_json(data):

    preferred_keys = {
        "datepublished",
        "datecreated",
        "pubdate",
        "publishdate",
        "publicationdate",
        "publish_time",
        "publishtime",
        "uploaddate",
    }

    if isinstance(
        data,
        dict
    ):

        for key, value in data.items():

            if (
                key.lower()
                in preferred_keys
            ):

                result = (
                    parse_timestamp(
                        value
                    )
                )

                if result:
                    return result

        for value in data.values():

            result = (
                find_timestamp_in_json(
                    value
                )
            )

            if result:
                return result

    elif isinstance(
        data,
        list
    ):

        for item in data:

            result = (
                find_timestamp_in_json(
                    item
                )
            )

            if result:
                return result

    return None


# ============================================================
# PUBLICATION DATE/TIME EXTRACTION
# ============================================================

def extract_publication_timestamp(
    response,
    article_url
):

    soup = BeautifulSoup(
        response.content,
        "html.parser"
    )

    # Keep the date encoded in the article URL as a trusted
    # fallback. Many of these publishers use dated article URLs.
    url_timestamp = parse_timestamp(
        article_url
    )

    # --------------------------------------------------------
    # META
    # --------------------------------------------------------

    meta_keys = {
        "article:published_time",
        "og:published_time",
        "datepublished",
        "date",
        "pubdate",
        "publishdate",
        "publication_date",
        "publish_date",
        "publish_time",
        "publishtime",
        "dc.date",
        "dcterms.date",
    }

    for meta in soup.find_all(
        "meta"
    ):

        key = (
            meta.get("property")
            or meta.get("name")
            or meta.get("itemprop")
            or ""
        ).lower()

        if key in meta_keys:

            result = parse_timestamp(
                meta.get("content")
            )

            if result:
                return result

    # --------------------------------------------------------
    # JSON-LD
    # --------------------------------------------------------

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:

            raw = (
                script.string
                or script.get_text()
            )

            data = json.loads(
                raw
            )

            result = (
                find_timestamp_in_json(
                    data
                )
            )

            if result:
                return result

        except Exception:
            pass

    # --------------------------------------------------------
    # <time>
    # --------------------------------------------------------

    for time_tag in soup.find_all(
        "time"
    ):

        result = parse_timestamp(
            time_tag.get(
                "datetime"
            )
            or time_tag.get_text(
                " ",
                strip=True
            )
        )

        if result:
            return result

    # --------------------------------------------------------
    # DATE/TIME CLASSES
    # --------------------------------------------------------

    date_pattern = re.compile(
        r"(date|time|publish|pubtime|timestamp|updated)",
        re.I
    )

    checked = 0

    for element in soup.find_all(
        True
    ):

        attributes = " ".join(
            [
                str(
                    element.get("id")
                    or ""
                ),
                " ".join(
                    element.get(
                        "class"
                    )
                    or []
                ),
            ]
        )

        if not date_pattern.search(
            attributes
        ):
            continue

        text = element.get_text(
            " ",
            strip=True
        )

        result = parse_timestamp(
            text
        )

        if result:

            # If the article URL contains a date and this page
            # element points to a different date, it is often a
            # photo caption or related-content timestamp rather
            # than the article publication date.
            if (
                url_timestamp
                and not timestamps_same_date(
                    result,
                    url_timestamp
                )
            ):
                checked += 1
                continue

            return result

        checked += 1

        if checked >= 40:
            break

    # --------------------------------------------------------
    # URL FALLBACK
    # --------------------------------------------------------
    #
    # Use the dated article URL before scanning arbitrary page
    # text. This prevents photo-caption dates from becoming the
    # article publication date.
    # --------------------------------------------------------

    if url_timestamp:
        return url_timestamp

    # --------------------------------------------------------
    # VISIBLE PAGE TEXT - LAST RESORT
    # --------------------------------------------------------
    #
    # Only use broad page text if metadata, structured data,
    # explicit time elements/classes, and the URL all failed.
    # --------------------------------------------------------

    page_text = soup.get_text(
        " ",
        strip=True
    )

    result = parse_timestamp(
        page_text[:5000]
    )

    if result:
        return result

    return None


# ============================================================
# CCTV TEXT CLEANUP
# ============================================================

def normalize_text_lines(text):

    if not text:
        return []

    lines = []

    for raw_line in text.replace("\r", "\n").split("\n"):

        line = re.sub(
            r'\s+',
            ' ',
            raw_line
        ).strip()

        if line:
            lines.append(line)

    return lines


def extract_cctv_news_body(soup):

    # CCTV has several news-page templates. Try a group of
    # known/likely article-body containers before falling back.
    selectors = [
        "div.content_area",
        "div.cnt_bd",
        "div#content_area",
        "div#content",
        "div.article_content",
        "div.article-body",
        "div.article_body",
        "div.text_area",
        "div.text-box",
        "div.content_detail",
        "div#text_area",
    ]

    navigation_markers = {
        "新闻",
        "新闻频道",
        "中国新闻",
        "点击收起全文",
        "返回央视网首页",
        "返回新闻频道",
        "分享",
        "扫一扫 分享到微信",
        "手机看",
        "扫一扫 手机继续看",
        "最新推荐",
        "精彩图集",
        "正在阅读：",
        "A-",
        "A+",
    }

    def clean_lines(raw_text):

        cleaned = []

        for line in normalize_text_lines(
            raw_text
        ):

            if line in navigation_markers:
                continue

            if re.match(
                r'^(来源|编辑|责任编辑|原标题|分享|返回|扫一扫|望海热线)[:：]?',
                line,
                re.I
            ):
                continue

            if re.fullmatch(
                r'[>|｜|]+',
                line
            ):
                continue

            if (
                "xinwenxiansuo@" in line.lower()
            ):
                continue

            cleaned.append(line)

        return cleaned

    # --------------------------------------------------------
    # 1. Dedicated article containers
    # --------------------------------------------------------

    for selector in selectors:

        container = soup.select_one(
            selector
        )

        if not container:
            continue

        paragraphs = []

        for paragraph in container.find_all(
            "p"
        ):

            value = paragraph.get_text(
                " ",
                strip=True
            )

            value = re.sub(
                r'\s+',
                ' ',
                value
            ).strip()

            if len(value) >= 20:
                paragraphs.append(value)

        candidate = "\n\n".join(
            clean_lines(
                "\n".join(paragraphs)
            )
        ).strip()

        if (
            len(candidate) >= 120
            and not looks_like_navigation_text(
                candidate
            )
        ):
            return candidate

        candidate = "\n\n".join(
            clean_lines(
                container.get_text(
                    "\n",
                    strip=True
                )
            )
        ).strip()

        if (
            len(candidate) >= 120
            and not looks_like_navigation_text(
                candidate
            )
        ):
            return candidate

    # --------------------------------------------------------
    # 2. JSON-LD articleBody
    # --------------------------------------------------------

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:

            data = json.loads(
                script.string
                or script.get_text()
            )

        except Exception:
            continue

        stack = [data]

        while stack:

            item = stack.pop()

            if isinstance(
                item,
                dict
            ):

                for key, value in item.items():

                    if (
                        key.lower()
                        == "articlebody"
                        and isinstance(
                            value,
                            str
                        )
                    ):

                        candidate = "\n\n".join(
                            clean_lines(value)
                        ).strip()

                        if (
                            len(candidate) >= 120
                            and not looks_like_navigation_text(
                                candidate
                            )
                        ):
                            return candidate

                    elif isinstance(
                        value,
                        (dict, list)
                    ):
                        stack.append(value)

            elif isinstance(
                item,
                list
            ):

                stack.extend(item)

    # --------------------------------------------------------
    # 3. Metadata description
    #
    # Better to publish a clean summary than navigation junk.
    # --------------------------------------------------------

    for attrs in (
        {"property": "og:description"},
        {"name": "description"},
        {"name": "Description"},
    ):

        tag = soup.find(
            "meta",
            attrs=attrs
        )

        if (
            tag
            and tag.get("content")
        ):

            candidate = re.sub(
                r'\s+',
                ' ',
                tag.get("content")
            ).strip()

            if (
                len(candidate) >= 80
                and not looks_like_navigation_text(
                    candidate
                )
            ):
                return candidate

    return ""


def looks_like_navigation_text(text):

    if not text:
        return True

    navigation_terms = [
        "返回央视网首页",
        "返回新闻频道",
        "扫一扫 分享到微信",
        "手机继续看",
        "最新推荐",
        "精彩图集",
        "正在阅读",
        "A-",
        "A+",
    ]

    hits = sum(
        1
        for term in navigation_terms
        if term in text
    )

    if (
        hits >= 3
        and len(text) < 1200
    ):
        return True

    prose_markers = (
        text.count("。")
        + text.count("！")
        + text.count("？")
        + text.count(". ")
    )

    if (
        len(text) >= 120
        and prose_markers == 0
    ):
        return True

    return False


def extract_cctv_video_summary(soup):

    page_lines = normalize_text_lines(
        soup.get_text(
            "\n",
            strip=True
        )
    )

    stop_exact = {
        "编辑",
        "责任编辑",
        "全部评论",
        "查看更多评论",
        "热播榜",
        "更多>",
        "更多 >",
        "相关推荐",
        "加载更多",
        "央视网首页",
        "央视节目官网首页",
        "中央广播电视总台",
        "央视网",
        "版权所有",
        "栏目信息",
        "栏目名称：",
        "栏目名称:",
        "栏目介绍：",
        "栏目介绍:",
        "播放列表",
        "精彩看点",
        "往期节目",
    }

    def is_stop(line):

        if line in stop_exact:
            return True

        if re.match(
            r'^(编辑|责任编辑)\s*[:：]',
            line
        ):
            return True

        if re.match(
            r'^京ICP备',
            line
        ):
            return True

        return False

    # --------------------------------------------------------
    # Prefer the actual "主要内容" section.
    # --------------------------------------------------------

    if "主要内容" in page_lines:

        index = page_lines.index(
            "主要内容"
        )

        content_lines = []

        for candidate in page_lines[
            index + 1:
        ]:

            if is_stop(candidate):
                break

            if candidate in {
                "正在加载",
                "正在加载...",
            }:
                continue

            content_lines.append(
                candidate
            )

        content = "\n\n".join(
            content_lines
        ).strip()

        if len(content) >= 20:
            return content

    # --------------------------------------------------------
    # Fallback to "视频简介".
    # --------------------------------------------------------

    if "视频简介" in page_lines:

        index = page_lines.index(
            "视频简介"
        )

        summary_lines = []

        for candidate in page_lines[
            index + 1:
        ]:

            if (
                candidate == "主要内容"
                or is_stop(candidate)
            ):
                break

            if candidate in {
                "关注",
                "内容简介",
                "简介",
                "正在加载",
                "正在加载...",
            }:
                continue

            if re.match(
                r'^来源\s*[:：]',
                candidate
            ):
                continue

            summary_lines.append(
                candidate
            )

        summary = "\n\n".join(
            summary_lines
        ).strip()

        if len(summary) >= 20:
            return summary

    return ""


def clean_cctv_article_text(
    source,
    article_url,
    response,
    article_text
):

    if source["slug"] not in {
        "cctv7",
        "cctv-cn",
        "cctv-en",
    }:
        return article_text

    soup = BeautifulSoup(
        response.content,
        "html.parser"
    )

    hostname = (
        urlparse(article_url).hostname
        or ""
    ).lower()

    # --------------------------------------------------------
    # CCTV CHINESE NEWS ARTICLES
    # --------------------------------------------------------

    if (
        source["slug"] == "cctv-cn"
        and hostname == "news.cctv.com"
    ):

        body = extract_cctv_news_body(
            soup
        )

        if body:
            return body

        # Do not knowingly publish CCTV navigation as an article.
        # Returning an empty string causes this candidate to be
        # skipped and the collector will try the next one.
        return ""

    # --------------------------------------------------------
    # CCTV VIDEO PAGES
    # --------------------------------------------------------

    if hostname == "tv.cctv.com":

        # CCTV Chinese pages that are mostly player/navigation
        # markup are much cleaner when we use the page's own
        # video-summary field.
        if source["slug"] == "cctv-cn":

            video_summary = (
                extract_cctv_video_summary(
                    soup
                )
            )

            if video_summary:
                return video_summary

    # --------------------------------------------------------
    # SAFE LINE-BASED CLEANUP
    # --------------------------------------------------------

    lines = normalize_text_lines(
        article_text
    )

    cleaned = []

    exact_noise = {
        "节目官网",
        "收藏",
        "播放列表",
        "正在播放",
        "热播榜",
        "内容简介",
        "关注",
        "栏目信息",
        "栏目名称：",
        "栏目名称:",
        "栏目介绍：",
        "栏目介绍:",
        "正在加载",
        "正在加载...",
        "更多 >",
        "更多",
        "关闭",
        "返回顶部",
        "相关推荐",
        "加载更多",
        "Share this:",
    }

    for line in lines:

        # For CCTV-7, everything after the program-information
        # marker is boilerplate in the pages we've observed.
        if (
            source["slug"] == "cctv7"
            and line in {
                "栏目名称：",
                "栏目名称:",
                "栏目介绍：",
                "栏目介绍:",
            }
        ):
            break

        if line in exact_noise:
            continue

        if re.match(
            r'^(编辑|责任编辑)\s*[:：]',
            line
        ):
            continue

        cleaned.append(line)

    cleaned_text = "\n\n".join(
        cleaned
    ).strip()

    if cleaned_text:
        return cleaned_text

    return article_text


# ============================================================
# ARTICLE EXTRACTION
# ============================================================

def extract_article(
    source,
    article_url,
    original_title
):

    response = get_with_retry(
        article_url
    )

    # --------------------------------------------------------
    # TAIWAN.CN ENCODING FIX
    # --------------------------------------------------------
    #
    # Some Taiwan.cn Chinese article pages use legacy Chinese
    # encodings or inconsistent charset declarations. Passing
    # the raw bytes directly to Trafilatura can produce
    # mojibake in the extracted article body.
    #
    # Only taiwan-cn gets this special handling so the other
    # working feeds keep their existing behavior.
    # --------------------------------------------------------

    if source["slug"] == "taiwan-cn":

        detected_encoding = (
            response.apparent_encoding
            or response.encoding
            or "gb18030"
        )

        try:

            extraction_input = response.content.decode(
                detected_encoding,
                errors="replace"
            )

        except (
            LookupError,
            UnicodeDecodeError
        ):

            extraction_input = response.content.decode(
                "gb18030",
                errors="replace"
            )

    else:

        extraction_input = response.content


    article_text = trafilatura.extract(
        extraction_input,
        url=article_url,
        include_comments=False,
        include_links=False
    )

    if (
        not article_text
        or len(
            article_text.strip()
        ) < 100
    ):

        soup = BeautifulSoup(
            extraction_input,
            "html.parser"
        )

        paragraphs = []

        for paragraph in soup.find_all(
            "p"
        ):

            text = paragraph.get_text(
                " ",
                strip=True
            )

            if len(text) > 30:

                paragraphs.append(
                    text
                )

        article_text = "\n\n".join(
            paragraphs
        )

    article_text = clean_cctv_article_text(
        source,
        article_url,
        response,
        article_text or ""
    )

    published = (
        extract_publication_timestamp(
            response,
            article_url
        )
    )

    resolved_title = (
        extract_best_title(
            source,
            original_title,
            response
        )
    )

    return (
        article_text or "",
        published,
        resolved_title
    )


# ============================================================
# RSS SORTING
# ============================================================

def rss_sort_key(article):

    published = article.get(
        "published"
    )

    if (
        published
        and published.get("datetime")
    ):

        dt = published["datetime"]

        return (
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second
        )

    # Final defensive fallback for an article that somehow
    # reached RSS without a parsed publication timestamp.
    url_result = parse_timestamp(
        article.get("url", "")
    )

    if (
        url_result
        and url_result.get("datetime")
    ):

        dt = url_result["datetime"]

        return (
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second
        )

    return (
        0,
        0,
        0,
        0,
        0,
        0
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
        "published_found": 0,
        "times_found": 0,
        "timezone_found": 0,
        "error": "",
    }

    # --------------------------------------------------------
    # SOURCE PAGE
    # --------------------------------------------------------

    try:

        response = get_with_retry(
            source["url"]
        )

    except Exception as error:

        result["status"] = (
            "SOURCE FAILED"
        )

        result["error"] = str(
            error
        )

        return result

    # --------------------------------------------------------
    # DISCOVERY
    # --------------------------------------------------------

    if (
        source["slug"]
        == "cctv7"
    ):

        candidates = (
            discover_cctv7_candidates(
                source,
                response
            )
        )

    else:

        candidates = (
            find_candidate_links(
                source,
                source["url"],
                response
            )
        )

    result[
        "candidates_found"
    ] = len(
        candidates
    )

    print(
        f"Candidate links found: "
        f"{len(candidates)}"
    )

    # --------------------------------------------------------
    # OUTPUT FOLDERS
    # --------------------------------------------------------

    article_folder = (
        os.path.join(
            "articles",
            source["slug"]
        )
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
    # ARTICLES
    # --------------------------------------------------------

    for article in candidates:

        if (
            result[
                "articles_extracted"
            ]
            >= ARTICLE_TARGET
        ):
            break

        result[
            "articles_attempted"
        ] += 1

        print()
        print(
            f"Trying: "
            f"{article['title']}"
        )

        try:

            (
                article_text,
                published,
                resolved_title
            ) = extract_article(
                source,
                article["url"],
                article["title"]
            )

            if (
                not article_text
                or len(
                    article_text.strip()
                ) < 100
            ):

                print(
                    "Skipped: insufficient article text."
                )

                continue

            result[
                "articles_extracted"
            ] += 1

            if (
                resolved_title
                != article["title"]
            ):

                print(
                    f"Resolved title: "
                    f"{resolved_title}"
                )

            published_display = (
                "Unknown"
            )

            if published:

                published_display = (
                    published[
                        "display"
                    ]
                )

                result[
                    "published_found"
                ] += 1

                if published[
                    "has_time"
                ]:

                    result[
                        "times_found"
                    ] += 1

                if published[
                    "has_timezone"
                ]:

                    result[
                        "timezone_found"
                    ] += 1

            print(
                f"Published: "
                f"{published_display}"
            )

            # ------------------------------------------------
            # SAVE ARTICLE
            # ------------------------------------------------

            filename = (
                clean_filename(
                    resolved_title
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
                    f"{resolved_title}\n\n"
                )

                file.write(
                    f"PUBLISHED:\n"
                    f"{published_display}\n\n"
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
                "title": resolved_title,
                "url": article["url"],
                "text": article_text,
                "published": published,
            })

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
    # RSS
    # --------------------------------------------------------

    # Feedgen renders later-added entries first in the RSS XML.
    # Add the oldest item first so the final feed displays the
    # newest article at the top.
    rss_items.sort(
        key=rss_sort_key
    )

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

        if article[
            "published"
        ]:

            rss_description = (
                "Published: "
                + article[
                    "published"
                ]["display"]
                + "\n\n"
                + article["text"]
            )

        else:

            rss_description = (
                article["text"]
            )

        entry.description(
            rss_description
        )

        if (
            article["published"]
            and article[
                "published"
            ]["has_timezone"]
        ):

            entry.pubDate(
                article[
                    "published"
                ]["datetime"]
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

    if (
        result[
            "candidates_found"
        ]
        == 0
    ):

        result["status"] = (
            "NO ARTICLES FOUND"
        )

    elif (
        result[
            "articles_extracted"
        ]
        >= ARTICLE_TARGET
    ):

        result["status"] = (
            "WORKING"
        )

    elif (
        result[
            "articles_extracted"
        ]
        > 0
    ):

        result["status"] = (
            "PARTIAL"
        )

    else:

        result["status"] = (
            "LINKS FOUND - TEXT FAILED"
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
            "candidates_found": 0,
            "articles_attempted": 0,
            "articles_extracted": 0,
            "articles_failed": 0,
            "published_found": 0,
            "times_found": 0,
            "timezone_found": 0,
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
        "=" * 70
        + "\n\n"
    )

    for result in results:

        report.write(
            f"SOURCE: "
            f"{result['name']}\n"
        )

        report.write(
            f"URL: "
            f"{result['url']}\n"
        )

        report.write(
            f"STATUS: "
            f"{result['status']}\n"
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
            f"{result['published_found']}\n"
        )

        report.write(
            f"ARTICLES WITH PUB TIME: "
            f"{result['times_found']}\n"
        )

        report.write(
            f"ARTICLES WITH EXPLICIT TIMEZONE: "
            f"{result['timezone_found']}\n"
        )

        report.write(
            f"ARTICLES SKIPPED/FAILED: "
            f"{result['articles_failed']}\n"
        )

        report.write(
            f"RSS FEED: "
            f"feeds/{result['slug']}.xml\n"
        )

        if result[
            "error"
        ]:

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
# SUMMARY
# ============================================================

working = sum(
    1
    for result in results
    if result["status"]
    == "WORKING"
)

partial = sum(
    1
    for result in results
    if result["status"]
    == "PARTIAL"
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
