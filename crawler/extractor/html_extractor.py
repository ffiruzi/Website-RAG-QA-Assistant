import aiohttp
import asyncio
from bs4 import BeautifulSoup, Comment
import logging
import re
from typing import Dict, Any, List, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin
import trafilatura
import readability
import time
import json

logger = logging.getLogger(__name__)


class EnhancedHTMLContentExtractor:
    """Enhanced extractor for HTML content with advanced cleaning and preprocessing."""

    def __init__(self, user_agent: str = "RAGCrawler"):
        self.headers = {
            "User-Agent": f"{user_agent}/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        self.last_request_time = {}

    async def fetch_url(self, url: str, session: aiohttp.ClientSession, delay: float = 1.0) -> Optional[str]:
        """Fetch the content of a URL with rate limiting."""
        try:
            # Apply rate limiting
            domain = urlparse(url).netloc
            if domain in self.last_request_time:
                time_since_last_request = time.time() - self.last_request_time[domain]
                if time_since_last_request < delay:
                    await asyncio.sleep(delay - time_since_last_request)

            # Make the request
            self.last_request_time[domain] = time.time()
            async with session.get(url, headers=self.headers, allow_redirects=True) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def remove_boilerplate(self, html: str) -> str:
        """Remove boilerplate content using trafilatura."""
        try:
            extracted = trafilatura.extract(html, include_comments=False, include_tables=True,
                                            include_links=True, include_images=False)
            if extracted:
                return extracted
        except Exception as e:
            logger.warning(f"Trafilatura extraction failed: {str(e)}")

        # Fallback to readability if trafilatura fails
        try:
            doc = readability.Document(html)
            return doc.summary()
        except Exception as e:
            logger.warning(f"Readability extraction failed: {str(e)}")

        # If both methods fail, fallback to BeautifulSoup
        return html

    def clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace and normalizing content."""
        if not text:
            return ""

        # Replace multiple newlines with a single one
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove HTML entities
        text = re.sub(r'&[a-zA-Z0-9]+;', ' ', text)

        # Normalize whitespace
        text = text.strip()

        return text

    def extract_structured_content(self, html: str) -> Dict[str, Any]:
        """Extract structured content from HTML (like headings, paragraphs, lists)."""
        if not html:
            return {"headings": [], "paragraphs": [], "lists": []}

        soup = BeautifulSoup(html, 'lxml')

        # Extract headings
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                headings.append({
                    "level": level,
                    "text": heading.get_text().strip()
                })

        # Extract paragraphs
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text and len(text) > 10:  # Ignore very short paragraphs
                paragraphs.append(text)

        # Extract lists
        lists = []
        for list_tag in soup.find_all(['ul', 'ol']):
            items = []
            for item in list_tag.find_all('li'):
                text = item.get_text().strip()
                if text:
                    items.append(text)
            if items:
                lists.append({
                    "type": list_tag.name,
                    "items": items
                })

        return {
            "headings": headings,
            "paragraphs": paragraphs,
            "lists": lists
        }

    def extract_metadata(self, html: str, url: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from HTML."""
        if not html:
            return {}

        soup = BeautifulSoup(html, 'lxml')
        metadata = {
            "url": url,
            "domain": urlparse(url).netloc
        }

        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata["title"] = title_tag.text.strip()

        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')

            if name and content:
                name = name.lower()

                # Extract common metadata
                if name in ['description', 'keywords', 'author', 'robots']:
                    metadata[name] = content
                # Extract OpenGraph metadata
                elif name.startswith('og:'):
                    og_key = name[3:]
                    if 'opengraph' not in metadata:
                        metadata['opengraph'] = {}
                    metadata['opengraph'][og_key] = content
                # Extract Twitter metadata
                elif name.startswith('twitter:'):
                    twitter_key = name[8:]
                    if 'twitter' not in metadata:
                        metadata['twitter'] = {}
                    metadata['twitter'][twitter_key] = content

        # Extract canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            metadata['canonical_url'] = canonical['href']

        # Extract language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag['lang']

        # Extract published date
        published_time = None

        # Try various meta tags for publication date
        for meta in soup.find_all('meta'):
            property_attr = meta.get('property', '').lower()
            name_attr = meta.get('name', '').lower()
            if property_attr in ['article:published_time', 'og:published_time'] or name_attr == 'publication_date':
                published_time = meta.get('content')
                break

        # Try common date markup patterns
        if not published_time:
            time_tag = soup.find('time')
            if time_tag and time_tag.get('datetime'):
                published_time = time_tag['datetime']

        if published_time:
            metadata['published_date'] = published_time

        return metadata

    def combine_content(self, structured_content: Dict[str, Any]) -> str:
        """Combine structured content into a single text."""
        text_parts = []

        # Add headings
        for heading in structured_content.get("headings", []):
            text_parts.append(f"{'#' * heading['level']} {heading['text']}")

        # Add paragraphs
        for paragraph in structured_content.get("paragraphs", []):
            text_parts.append(paragraph)

        # Add lists
        for list_data in structured_content.get("lists", []):
            for i, item in enumerate(list_data["items"]):
                prefix = "- " if list_data["type"] == "ul" else f"{i + 1}. "
                text_parts.append(f"{prefix}{item}")

        return "\n\n".join(text_parts)

    async def extract_from_url(self, url: str, delay: float = 1.0) -> Dict[str, Any]:
        """Extract content from a specific URL."""
        async with aiohttp.ClientSession() as session:
            html = await self.fetch_url(url, session, delay)
            if not html:
                return {"url": url, "error": "Failed to fetch content"}

            # Extract basic content
            cleaned_html = self.remove_boilerplate(html)
            structured_content = self.extract_structured_content(cleaned_html)
            metadata = self.extract_metadata(html, url)

            # Combine content into a single text
            text = self.combine_content(structured_content)
            clean_text = self.clean_text(text)

            return {
                "url": url,
                "title": metadata.get("title", ""),
                "metadata": metadata,
                "text": clean_text,
                "structured_content": structured_content,
                "raw_html": html if metadata.get("keep_raw_html", False) else None
            }

    async def extract_from_urls(self, urls: List[str], delay: float = 1.0) -> List[Dict[str, Any]]:
        """Extract content from multiple URLs in parallel, with rate limiting."""
        async with aiohttp.ClientSession() as session:
            tasks = []

            for url in urls:
                tasks.append(self.extract_from_url(url, delay))

            results = await asyncio.gather(*tasks)
            return results


# Example usage
async def main():
    extractor = EnhancedHTMLContentExtractor()
    content = await extractor.extract_from_url("https://example.com")
    print(f"Title: {content['title']}")
    print(f"Text length: {len(content['text'])} characters")
    print(f"Metadata: {json.dumps(content['metadata'], indent=2)}")
    print("\nContent sample:")
    print(content['text'][:500] + "..." if len(content['text']) > 500 else content['text'])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())