import requests
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://www.mfa.gov.cn/eng/xw/fyrbt/"

response = requests.get(url, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

articles = []

# Find the 10 most recent article links
for link in soup.find_all("a", href=True):
    title = link.get_text(" ", strip=True)
    full_url = urljoin(url, link["href"])

    if "/eng/xw/fyrbt/" in full_url and full_url.endswith(".html") and title:

        # Avoid duplicate URLs
        if not any(article["url"] == full_url for article in articles):
            articles.append({
                "title": title,
                "url": full_url
            })

    if len(articles) >= 10:
        break


print(f"Found {len(articles)} articles.\n")


# Extract text from each article
for number, article in enumerate(articles, start=1):

    print("=" * 80)
    print(f"ARTICLE {number}")
    print("=" * 80)

    print("\nTITLE:")
    print(article["title"])

    print("\nURL:")
    print(article["url"])

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

        print("\nARTICLE TEXT:")
        print(article_text)

    except Exception as error:
        print("\nERROR:")
        print(error)

    print("\n")
