import logging
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from crawler.crawler.sitemap_crawler import EnhancedSitemapCrawler
from crawler.domain.domain_crawler import get_domain_crawler, DomainCrawler
from crawler.robots.robots_parser import RobotsParser

logger = logging.getLogger(__name__)


class CrawlerFactory:
    """Factory class to create appropriate crawlers for websites."""

    @staticmethod
    async def detect_website_type(url: str, user_agent: str = "RAGCrawler") -> str:
        """Detect the type of website to determine the best crawler to use."""
        try:
            # Parse URL
            parsed_url = urlparse(url)
            path = parsed_url.path.lower()

            # First, check URL patterns
            if any(pattern in path for pattern in ['/blog', '/post', '/article', '/news']):
                return "blog"
            elif any(pattern in path for pattern in
                     ['/docs', '/documentation', '/guide', '/tutorial', '/reference', '/api']):
                return "documentation"
            elif any(pattern in path for pattern in ['/product', '/products', '/shop', '/store', '/category']):
                return "ecommerce"

            # If URL doesn't give clear indication, fetch and analyze the main page
            headers = {
                "User-Agent": f"{user_agent}/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'lxml')

                        # Check for e-commerce indicators
                        ecommerce_indicators = [
                            '.products', '.product-list', '.cart', '.shop',
                            'form[action*="cart"]', 'button[name*="add"]',
                            'input[name*="add_to_cart"]'
                        ]
                        for indicator in ecommerce_indicators:
                            if soup.select(indicator):
                                return "ecommerce"

                        # Check for documentation indicators
                        doc_indicators = [
                            '.documentation', '.docs', '.markdown-body', '.doc-content',
                            'nav.toc', '.sidebar'
                        ]
                        for indicator in doc_indicators:
                            if soup.select(indicator):
                                return "documentation"

                        # Check for blog indicators
                        blog_indicators = [
                            '.blog', '.post', '.article', '.entry',
                            'article', '.post-content', '.blog-post'
                        ]
                        for indicator in blog_indicators:
                            if soup.select(indicator):
                                return "blog"

                        # Check meta tags
                        meta_tags = soup.find_all('meta')
                        for meta in meta_tags:
                            if meta.get('property') == 'og:type':
                                og_type = meta.get('content', '').lower()
                                if og_type in ['product', 'product.item']:
                                    return "ecommerce"
                                elif og_type in ['article', 'blog']:
                                    return "blog"

            # Default to a generic website if we can't determine the type
            return "generic"

        except Exception as e:
            logger.error(f"Error detecting website type for {url}: {str(e)}")
            return "generic"

    @staticmethod
    async def create_crawler(url: str, sitemap_url: Optional[str] = None,
                             user_agent: str = "RAGCrawler") -> EnhancedSitemapCrawler:
        """Create the appropriate crawler for a website."""
        # For now, we always use the EnhancedSitemapCrawler for URL discovery
        # but we might enhance this in the future to use specialized crawlers
        return EnhancedSitemapCrawler(url, user_agent)

    @staticmethod
    async def create_domain_crawler(url: str, website_type: Optional[str] = None,
                                    user_agent: str = "RAGCrawler") -> DomainCrawler:
        """Create a domain-specific crawler for content extraction."""
        if website_type is None:
            website_type = await CrawlerFactory.detect_website_type(url, user_agent)

        return get_domain_crawler(url, user_agent)

    @staticmethod
    def create_robots_parser(user_agent: str = "RAGCrawler") -> RobotsParser:
        """Create a robots.txt parser."""
        return RobotsParser(user_agent)


# Example usage
async def main():
    url = "https://example.com"
    website_type = await CrawlerFactory.detect_website_type(url)
    print(f"Detected website type: {website_type}")

    crawler = await CrawlerFactory.create_crawler(url)
    domain_crawler = await CrawlerFactory.create_domain_crawler(url, website_type)

    print(f"Created crawler: {type(crawler).__name__}")
    print(f"Created domain crawler: {type(domain_crawler).__name__}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())