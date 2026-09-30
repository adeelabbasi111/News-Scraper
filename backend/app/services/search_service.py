import requests
import urllib.parse
from typing import List, Dict
from ..core.config import get_content_config

HEADERS = {
    "User-Agent": "NewsResearchBot/1.0 (educational-project)"
}


class SearchService:
    @staticmethod
    def search_news(topic: str, content_type: str, time_range: str = "24h") -> List[Dict]:
        config = get_content_config(content_type)
        max_results = config["max_sources"]

        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": topic,
            "utf8": "1",
            "format": "json",
            "srlimit": max_results,
        }

        results = []
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            search_hits = data.get("query", {}).get("search", [])
            for hit in search_hits:
                title = hit.get("title", "")
                page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}"
                snippet = (
                    hit.get("snippet", "")
                    .replace('<span class="searchmatch">', "")
                    .replace("</span>", "")
                )
                results.append({
                    "title": title,
                    "link": page_url,
                    "snippet": snippet,
                })

        except Exception as e:
            print(f"Wikipedia Search API Error: {e}")

        return results
