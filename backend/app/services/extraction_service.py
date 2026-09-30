import trafilatura
from bs4 import BeautifulSoup
import requests
import hashlib

HEADERS = {
    "User-Agent": "NewsResearchBot/1.0 (educational-project)"
}


class ExtractionService:
    @staticmethod
    def extract_article(url: str) -> dict:
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                # Fallback: try requests with User-Agent
                resp = requests.get(url, headers=HEADERS, timeout=10)
                if resp.status_code == 200:
                    downloaded = resp.text
                else:
                    return {"status": "failed", "content": None}

            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                no_fallback=False,
            )
            if not text:
                # Fallback to simple BS4 if trafilatura fails
                if not isinstance(downloaded, str):
                    resp = requests.get(url, headers=HEADERS, timeout=10)
                    downloaded = resp.text
                soup = BeautifulSoup(downloaded, "html.parser")
                text = " ".join([p.text for p in soup.find_all("p")])

            if not text or len(text) < 100:
                return {"status": "failed", "content": None}

            # Truncate very long articles to keep prompt size manageable
            if len(text) > 5000:
                text = text[:5000]

            return {"status": "success", "content": text.strip()}
        except Exception as e:
            print(f"Extraction failed for {url}: {e}")
            return {"status": "failed", "content": None}

    @staticmethod
    def deduplicate_articles(articles: list) -> list:
        seen_hashes = set()
        unique_articles = []

        for article in articles:
            content = article.get("content", "")
            if not content:
                continue

            content_hash = hashlib.md5(content[:500].encode("utf-8")).hexdigest()
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_articles.append(article)

        return unique_articles
