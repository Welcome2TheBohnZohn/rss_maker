import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://www.mfa.gov.cn/eng/xw/fyrbt/"

response = requests.get(url, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("Recent MFA articles:\n")

count = 0

for link in soup.find_all("a", href=True):
    title = link.get_text(" ", strip=True)
    article_url = urljoin(url, link["href"])

    if "/eng/xw/fyrbt/" in article_url and article_url.endswith(".html"):
        if title:
            print(title)
            print(article_url)
            print()

            count += 1

    if count >= 10:
        break
