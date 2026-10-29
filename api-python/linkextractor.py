#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_links(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LinkExtractor/1.0"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        return [{"text": f"Error fetching {url}: {str(e)}", "href": url}]

    soup = BeautifulSoup(res.text, "html.parser")
    base = url
    base_tag = soup.find("base")
    if base_tag and base_tag.get("href"):
        base = base_tag.get("href")

    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            text = " ".join(link.text.split()) or "[IMG]"
            links.append({
                "text": text,
                "href": urljoin(base, href)
            })
    return links
