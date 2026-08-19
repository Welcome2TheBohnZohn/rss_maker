import requests
from bs4 import BeautifulSoup

url = "https://www.mfa.gov.cn/eng/xw/fyrbt/"

response = requests.get(url, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

print("Successfully connected to the MFA website")
print("Page title:", soup.title.string if soup.title else "No title found")
