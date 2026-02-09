"""
URL scraper - best-effort HTML text extraction
"""
import re
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    """Simple HTML parser to extract text content."""

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_tags = {"script", "style", "head", "meta", "link"}
        self.current_skip = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.skip_tags:
            self.current_skip += 1

    def handle_endtag(self, tag):
        if tag.lower() in self.skip_tags and self.current_skip > 0:
            self.current_skip -= 1

    def handle_data(self, data):
        if self.current_skip == 0:
            text = data.strip()
            if text:
                self.text_parts.append(text)

    def get_text(self) -> str:
        return "\n".join(self.text_parts)


def fetch_url(url: str, timeout: int = 30) -> Optional[str]:
    """
    Fetch and extract text content from a URL.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Extracted text content, or None on failure
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        request = Request(url, headers=headers)

        with urlopen(request, timeout=timeout) as response:
            # Try to detect encoding
            content_type = response.headers.get("Content-Type", "")
            encoding = "utf-8"
            if "charset=" in content_type:
                match = re.search(r"charset=([^\s;]+)", content_type)
                if match:
                    encoding = match.group(1)

            html = response.read().decode(encoding, errors="replace")

        # Extract text
        parser = TextExtractor()
        parser.feed(html)
        text = parser.get_text()

        # Clean up
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        if len(text) < 100:
            return None

        return text

    except (URLError, HTTPError, TimeoutError, UnicodeDecodeError) as e:
        print(f"URL fetch failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
