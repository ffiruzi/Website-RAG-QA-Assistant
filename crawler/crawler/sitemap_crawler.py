import aiohttp
import asyncio
import logging
import gzip
import io
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta
import time

from crawler.robots.robots_parser import RobotsParser

logger = logging.getLogger(__name__)


class EnhancedSitemapCrawler:
    """An enhanced crawler that can handle all sitemap formats and respects robots.txt."""

    def __init__(self, base_url: str, user_agent: str = "RAGCrawler"):
        self.base_url = base_url.rstrip('/')
        self.parsed_url = urlparse(self.base_url)
        self.domain = self.parsed_url.netloc
        self.user_agent = user_agent
        self.robots_parser = RobotsParser(user_agent)
        self.crawl_delays = {}
        self.headers = {
            "User-Agent": f"{user_agent}/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",  # Don't include 'br' until we support it
            "Connection": "keep-alive"
        }
        self.discovered_urls = set()
        self.crawled_urls = set()
        self.last_request_time = {}
        self.default_crawl_delay = 1.0  # Add this line to fix the error

    async def fetch_url(self, url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Fetch the content of a URL with improved content encoding handling."""
        try:
            # Apply rate limiting
            domain = urlparse(url).netloc
            if domain in self.last_request_time:
                time_since_last_request = time.time() - self.last_request_time[domain]
                if time_since_last_request < self.default_crawl_delay:
                    await asyncio.sleep(self.default_crawl_delay - time_since_last_request)

            # Make the request
            self.last_request_time[domain] = time.time()

            # Explicitly specify accepted encodings
            headers = dict(self.headers)
            headers['Accept-Encoding'] = 'gzip, deflate'  # Temporarily remove 'br' until we add proper support

            async with session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status == 200:
                    try:
                        return await response.text()
                    except Exception as e:
                        # Fallback to raw bytes if text decoding fails
                        logger.warning(f"Text decoding failed for {url}, trying raw content: {str(e)}")
                        raw_content = await response.read()
                        # Try to decode as utf-8 with error handling
                        try:
                            return raw_content.decode('utf-8', errors='replace')
                        except:
                            logger.error(f"Failed to decode content from {url}")
                            return None
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    async def discover_sitemap_url(self, session: aiohttp.ClientSession) -> Optional[str]:
        """Discover the sitemap URL from robots.txt or try common locations."""
        sitemap_url = None

        # First, try to find sitemap in robots.txt
        robots_url = f"{self.parsed_url.scheme}://{self.domain}/robots.txt"
        robots_content = await self.fetch_url(robots_url, session)

        if robots_content:
            sitemap_matches = re.findall(r'Sitemap:\s*(.*)', robots_content, re.IGNORECASE)
            if sitemap_matches:
                sitemap_url = sitemap_matches[0].strip()
                logger.info(f"Found sitemap URL in robots.txt: {sitemap_url}")
                return sitemap_url

        # Try common sitemap locations
        common_locations = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/sitemap/sitemap.xml",
            f"{self.base_url}/sitemap/index.xml",
            f"{self.base_url}/sitemaps/sitemap.xml"
        ]

        for location in common_locations:
            logger.info(f"Checking common sitemap location: {location}")
            content = await self.fetch_url(location, session)
            if content:
                logger.info(f"Found sitemap at {location}")
                return location

        logger.warning(f"Could not find sitemap for {self.base_url}")
        return None

    async def parse_sitemap(self, sitemap_content: str, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Parse the sitemap XML and extract URLs with metadata."""
        if not sitemap_content:
            return []

        try:
            soup = BeautifulSoup(sitemap_content, 'xml')

            # Check if this is a sitemap index
            sitemaps = soup.find_all('sitemap')
            if sitemaps:
                logger.info(f"Found sitemap index with {len(sitemaps)} sitemaps")
                all_urls = []

                for sitemap in sitemaps:
                    loc_tag = sitemap.find('loc')
                    if loc_tag and loc_tag.string:
                        sitemap_url = loc_tag.string.strip()
                        logger.info(f"Processing sub-sitemap: {sitemap_url}")

                        sub_content = await self.fetch_url(sitemap_url, session)
                        if sub_content:
                            sub_urls = await self.parse_sitemap(sub_content, session)
                            all_urls.extend(sub_urls)

                return all_urls

            # Handle regular sitemap
            url_entries = []
            urls = soup.find_all('url')

            if not urls:
                # Some sitemaps directly list locs at the root level
                locs = soup.find_all('loc')
                if locs:
                    for loc in locs:
                        if loc.string:
                            url_entries.append({
                                "url": loc.string.strip(),
                                "lastmod": None,
                                "changefreq": None,
                                "priority": None
                            })
            else:
                for url in urls:
                    loc = url.find('loc')
                    if loc and loc.string:
                        url_data = {
                            "url": loc.string.strip(),
                            "lastmod": None,
                            "changefreq": None,
                            "priority": None
                        }

                        # Extract additional metadata
                        lastmod = url.find('lastmod')
                        if lastmod and lastmod.string:
                            url_data["lastmod"] = lastmod.string.strip()

                        changefreq = url.find('changefreq')
                        if changefreq and changefreq.string:
                            url_data["changefreq"] = changefreq.string.strip()

                        priority = url.find('priority')
                        if priority and priority.string:
                            try:
                                url_data["priority"] = float(priority.string.strip())
                            except ValueError:
                                pass

                        url_entries.append(url_data)

            return url_entries

        except Exception as e:
            logger.error(f"Error parsing sitemap: {str(e)}")
            return []

    async def discover_urls_from_html(self, html_content: str, base_url: str) -> Set[str]:
        """Extract URLs from HTML content for sites without sitemaps."""
        if not html_content:
            return set()

        discovered_urls = set()

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href'].strip()

                # Skip empty links, anchors, javascript, mailto etc.
                if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue

                # Convert relative URLs to absolute
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)

                # Only include URLs from the same domain
                parsed_href = urlparse(href)
                if parsed_href.netloc == self.domain:
                    discovered_urls.add(href)

        except Exception as e:
            logger.error(f"Error extracting links from HTML: {str(e)}")

        return discovered_urls

    async def crawl_without_sitemap(self, session: aiohttp.ClientSession, max_pages: int = 100) -> List[Dict[str, Any]]:
        """Crawl a website without a sitemap by following links."""
        to_crawl = {self.base_url}
        crawled = set()
        results = []

        while to_crawl and len(crawled) < max_pages:
            current_url = to_crawl.pop()

            if current_url in crawled:
                continue

            logger.info(f"Crawling {current_url}")

            # Check robots.txt
            allowed, delay = await self.robots_parser.is_allowed(current_url)
            if not allowed:
                logger.warning(f"URL {current_url} is disallowed by robots.txt")
                continue

            # Fetch page
            html_content = await self.fetch_url(current_url, session)
            if html_content:
                # Add to crawled list
                crawled.add(current_url)

                # Add to results
                results.append({
                    "url": current_url,
                    "lastmod": None,
                    "changefreq": None,
                    "priority": None
                })

                # Extract links for further crawling
                new_urls = await self.discover_urls_from_html(html_content, current_url)
                for url in new_urls:
                    if url not in crawled:
                        to_crawl.add(url)

            # Apply rate limiting
            await asyncio.sleep(delay)

        return results

    async def crawl(self, max_pages: int = 500) -> List[Dict[str, Any]]:
        """Crawl the website and return discovered URLs with metadata."""
        async with aiohttp.ClientSession() as session:
            # Try to find and use sitemap
            sitemap_url = await self.discover_sitemap_url(session)

            if sitemap_url:
                logger.info(f"Using sitemap at {sitemap_url}")
                sitemap_content = await self.fetch_url(sitemap_url, session)
                if sitemap_content:
                    return await self.parse_sitemap(sitemap_content, session)

            # If no sitemap found or sitemap processing failed, fall back to HTML crawling
            logger.info(f"No sitemap found for {self.base_url}, falling back to HTML crawling")
            return await self.crawl_without_sitemap(session, max_pages)


# Example usage
async def main():
    crawler = EnhancedSitemapCrawler("https://example.com")
    urls = await crawler.crawl()
    print(f"Discovered {len(urls)} URLs:")
    for url_data in urls[:10]:  # Print first 10 URLs
        print(f"- {url_data['url']} (lastmod: {url_data['lastmod']})")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())