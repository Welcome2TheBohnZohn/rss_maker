import requests
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://www.mfa.gov.cn/eng/xw/fyrbt/"

response = requests.get(url, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Find the first recent article
article_url = None
article_title = None

for link in soup.find_all("a", href=True):
    title = link.get_text(" ", strip=True)
    full_url = urljoin(url, link["href"])

    if "/eng/xw/fyrbt/" in full_url and full_url.endswith(".html") and title:
        article_url = full_url
        article_title = title
        break

print("ARTICLE TITLE:")
print(article_title)

print("\nARTICLE URL:")
print(article_url)

# Download the article
article_response = requests.get(article_url, timeout=30)
article_response.raise_for_status()

# Extract the main article text
article_text = trafilatura.extract(
    article_response.text,
    url=article_url,
    include_comments=False,
    include_links=False
)

print("\nARTICLE TEXT:")
print(article_text)
