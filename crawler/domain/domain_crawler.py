import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import aiohttp
import re
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class DomainCrawler(ABC):
    """Base class for domain-specific crawlers."""

    def __init__(self, base_url: str, user_agent: str = "RAGCrawler"):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.user_agent = user_agent
        self.headers = {
            "User-Agent": f"{user_agent}/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

    @abstractmethod
    async def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract domain-specific content from HTML."""
        pass

    @abstractmethod
    async def discover_urls(self, html: str, url: str) -> List[str]:
        """Discover domain-specific URLs from HTML."""
        pass

    async def fetch_url(self, url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Fetch the content of a URL."""
        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None


class BlogCrawler(DomainCrawler):
    """Crawler optimized for blog websites."""

    async def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract blog-specific content from HTML."""
        if not html:
            return {"url": url, "error": "No HTML content"}

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()

            # Try to find blog post content using common patterns
            content_selectors = [
                'article',
                '.post-content',
                '.entry-content',
                '.blog-post',
                '.article-content',
                '#content',
                '.content',
                'main'
            ]

            content_element = None
            for selector in content_selectors:
                # Try CSS selector
                element = soup.select_one(selector)
                if element:
                    content_element = element
                    break

                # Try HTML tag
                if selector.startswith('.') or selector.startswith('#'):
                    continue
                element = soup.find(selector)
                if element:
                    content_element = element
                    break

            # Extract text from content element or fallback to body
            if content_element:
                paragraphs = content_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'li'])
            else:
                paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

            # Extract text content
            content_parts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 10:  # Skip very short paragraphs
                    content_parts.append(text)

            content = "\n\n".join(content_parts)

            # Extract metadata
            metadata = {}

            # Published date
            date_selectors = [
                'time',
                '.post-date',
                '.entry-date',
                '.published',
                'meta[property="article:published_time"]',
                'meta[property="og:published_time"]'
            ]

            for selector in date_selectors:
                if selector.startswith('meta'):
                    element = soup.select_one(selector)
                    if element and element.get('content'):
                        metadata['published_date'] = element['content']
                        break
                else:
                    element = soup.select_one(selector)
                    if element:
                        if element.get('datetime'):
                            metadata['published_date'] = element['datetime']
                            break
                        elif element.text.strip():
                            metadata['published_date'] = element.text.strip()
                            break

            # Author
            author_selectors = [
                '.author',
                '.byline',
                'meta[name="author"]',
                'meta[property="article:author"]',
                'a[rel="author"]'
            ]

            for selector in author_selectors:
                if selector.startswith('meta'):
                    element = soup.select_one(selector)
                    if element and element.get('content'):
                        metadata['author'] = element['content']
                        break
                else:
                    element = soup.select_one(selector)
                    if element:
                        metadata['author'] = element.text.strip()
                        break

            # Categories/Tags
            tags = []
            tag_selectors = [
                '.tags a',
                '.categories a',
                '.post-tags a',
                'meta[property="article:tag"]'
            ]

            for selector in tag_selectors:
                if selector.startswith('meta'):
                    elements = soup.select(selector)
                    for element in elements:
                        if element.get('content'):
                            tags.append(element['content'])
                else:
                    elements = soup.select(selector)
                    for element in elements:
                        tag_text = element.text.strip()
                        if tag_text:
                            tags.append(tag_text)

            if tags:
                metadata['tags'] = list(set(tags))  # Remove duplicates

            return {
                "url": url,
                "title": title,
                "content": content,
                "metadata": metadata,
                "content_type": "blog"
            }

        except Exception as e:
            logger.error(f"Error extracting blog content from {url}: {str(e)}")
            return {"url": url, "error": f"Error extracting content: {str(e)}"}

    async def discover_urls(self, html: str, url: str) -> List[str]:
        """Discover blog-specific URLs from HTML."""
        if not html:
            return []

        discovered_urls = set()

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Find all links
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href'].strip()

                # Skip empty links, anchors, javascript, mailto etc.
                if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue

                # Convert relative URLs to absolute
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)

                # Only include URLs from the same domain
                parsed_href = urlparse(href)
                if parsed_href.netloc == self.domain:
                    # Look for blog-specific patterns
                    blog_patterns = [
                        r'/blog/',
                        r'/post/',
                        r'/article/',
                        r'/\d{4}/\d{2}/',  # Date-based archives
                        r'/category/',
                        r'/tag/'
                    ]

                    for pattern in blog_patterns:
                        if re.search(pattern, href):
                            discovered_urls.add(href)
                            break

                    # Also check for links in blog index pages
                    if link.parent and (
                            'post' in link.parent.get('class', []) or
                            'blog' in link.parent.get('class', []) or
                            'article' in link.parent.get('class', [])
                    ):
                        discovered_urls.add(href)

            return list(discovered_urls)

        except Exception as e:
            logger.error(f"Error discovering blog URLs from {url}: {str(e)}")
            return []


class DocumentationCrawler(DomainCrawler):
    """Crawler optimized for documentation websites."""

    async def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract documentation-specific content from HTML."""
        if not html:
            return {"url": url, "error": "No HTML content"}

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()

            # Try to find documentation content using common patterns
            content_selectors = [
                '.documentation',
                '.docs',
                '.doc-content',
                '.markdown-body',
                '.content',
                'article',
                'main'
            ]

            content_element = None
            for selector in content_selectors:
                # Try CSS selector
                element = soup.select_one(selector)
                if element:
                    content_element = element
                    break

                # Try HTML tag
                if selector.startswith('.') or selector.startswith('#'):
                    continue
                element = soup.find(selector)
                if element:
                    content_element = element
                    break

            # Extract structured content
            structured_content = {}

            # Extract headings
            headings = []
            if content_element:
                for level in range(1, 7):
                    for heading in content_element.find_all(f'h{level}'):
                        headings.append({
                            "level": level,
                            "text": heading.get_text().strip(),
                            "id": heading.get('id', '')
                        })
            else:
                for level in range(1, 7):
                    for heading in soup.find_all(f'h{level}'):
                        headings.append({
                            "level": level,
                            "text": heading.get_text().strip(),
                            "id": heading.get('id', '')
                        })

            structured_content['headings'] = headings

            # Extract paragraphs and code blocks
            paragraphs = []
            code_blocks = []

            if content_element:
                # Extract paragraphs
                for p in content_element.find_all('p'):
                    text = p.get_text().strip()
                    if text:
                        paragraphs.append(text)

                # Extract code blocks
                for code in content_element.find_all(['pre', 'code']):
                    # Skip if it's a 'code' inside a 'pre' to avoid duplication
                    if code.name == 'code' and code.parent.name == 'pre':
                        continue

                    code_text = code.get_text().strip()
                    if code_text:
                        language = ''
                        if code.get('class'):
                            for cls in code.get('class'):
                                if cls.startswith('language-') or cls.startswith('lang-'):
                                    language = cls.split('-')[1]
                                    break

                        code_blocks.append({
                            "code": code_text,
                            "language": language
                        })
            else:
                # Extract paragraphs
                for p in soup.find_all('p'):
                    text = p.get_text().strip()
                    if text:
                        paragraphs.append(text)

                # Extract code blocks
                for code in soup.find_all(['pre', 'code']):
                    # Skip if it's a 'code' inside a 'pre' to avoid duplication
                    if code.name == 'code' and code.parent.name == 'pre':
                        continue

                    code_text = code.get_text().strip()
                    if code_text:
                        language = ''
                        if code.get('class'):
                            for cls in code.get('class'):
                                if cls.startswith('language-') or cls.startswith('lang-'):
                                    language = cls.split('-')[1]
                                    break

                        code_blocks.append({
                            "code": code_text,
                            "language": language
                        })

            structured_content['paragraphs'] = paragraphs
            structured_content['code_blocks'] = code_blocks

            # Combine content into a single text
            text_parts = []

            # Add headings
            for heading in headings:
                text_parts.append(f"{'#' * heading['level']} {heading['text']}")

            # Add paragraphs
            for paragraph in paragraphs:
                text_parts.append(paragraph)

            # Add code blocks
            for code_block in code_blocks:
                language = code_block['language']
                language_str = f"```{language}\n" if language else "```\n"
                text_parts.append(f"{language_str}{code_block['code']}\n```")

            combined_text = "\n\n".join(text_parts)

            # Extract metadata
            metadata = {}

            # Try to find documentation version
            version_selectors = [
                '.version',
                '.doc-version',
                'meta[name="version"]'
            ]

            for selector in version_selectors:
                if selector.startswith('meta'):
                    element = soup.select_one(selector)
                    if element and element.get('content'):
                        metadata['version'] = element['content']
                        break
                else:
                    element = soup.select_one(selector)
                    if element:
                        metadata['version'] = element.text.strip()
                        break

            return {
                "url": url,
                "title": title,
                "content": combined_text,
                "structured_content": structured_content,
                "metadata": metadata,
                "content_type": "documentation"
            }

        except Exception as e:
            logger.error(f"Error extracting documentation content from {url}: {str(e)}")
            return {"url": url, "error": f"Error extracting content: {str(e)}"}

    async def discover_urls(self, html: str, url: str) -> List[str]:
        """Discover documentation-specific URLs from HTML."""
        if not html:
            return []

        discovered_urls = set()

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Find all links
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href'].strip()

                # Skip empty links, anchors, javascript, mailto etc.
                if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue

                # Convert relative URLs to absolute
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)

                # Only include URLs from the same domain
                parsed_href = urlparse(href)
                if parsed_href.netloc == self.domain:
                    # Look for documentation-specific patterns
                    doc_patterns = [
                        r'/docs/',
                        r'/documentation/',
                        r'/guide/',
                        r'/tutorial/',
                        r'/manual/',
                        r'/reference/',
                        r'/api/'
                    ]

                    for pattern in doc_patterns:
                        if re.search(pattern, href):
                            discovered_urls.add(href)
                            break

                    # Also check for links in navigation elements
                    if link.parent and any(
                            cls in link.parent.get('class', []) for cls in ['nav', 'sidebar', 'toc', 'menu']):
                        discovered_urls.add(href)

            return list(discovered_urls)

        except Exception as e:
            logger.error(f"Error discovering documentation URLs from {url}: {str(e)}")
            return []


class EcommerceCrawler(DomainCrawler):
    """Crawler optimized for e-commerce websites."""

    async def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract e-commerce-specific content from HTML."""
        if not html:
            return {"url": url, "error": "No HTML content"}

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()

            # Check if this is a product page
            is_product_page = False
            product_indicators = [
                'meta[property="og:type"][content="product"]',
                '.product',
                '#product',
                'form[action*="cart"]',
                'button[name*="add"]',
                'input[name*="add_to_cart"]'
            ]

            for indicator in product_indicators:
                if soup.select_one(indicator):
                    is_product_page = True
                    break

            if is_product_page:
                # Extract product information
                product_info = {}

                # Product name
                product_name_selectors = [
                    'h1.product-title',
                    '.product-name',
                    '.product-title',
                    'h1',
                ]

                for selector in product_name_selectors:
                    element = soup.select_one(selector)
                    if element:
                        product_info['name'] = element.text.strip()
                        break

                # Product price
                price_selectors = [
                    '.price',
                    '.product-price',
                    'span[itemprop="price"]',
                    'meta[property="product:price:amount"]'
                ]

                for selector in price_selectors:
                    if selector.startswith('meta'):
                        element = soup.select_one(selector)
                        if element and element.get('content'):
                            product_info['price'] = element['content']
                            break
                    else:
                        element = soup.select_one(selector)
                        if element:
                            product_info['price'] = element.text.strip()
                            break

                # Product description
                description_selectors = [
                    '.product-description',
                    '.description',
                    '[itemprop="description"]',
                    'meta[property="og:description"]'
                ]

                for selector in description_selectors:
                    if selector.startswith('meta'):
                        element = soup.select_one(selector)
                        if element and element.get('content'):
                            product_info['description'] = element['content']
                            break
                    else:
                        element = soup.select_one(selector)
                        if element:
                            product_info['description'] = element.text.strip()
                            break

                # Product images
                image_selectors = [
                    'meta[property="og:image"]',
                    '[itemprop="image"]',
                    '.product-image img',
                    '.product img'
                ]

                product_images = []
                for selector in image_selectors:
                    if selector.startswith('meta'):
                        element = soup.select_one(selector)
                        if element and element.get('content'):
                            product_images.append(element['content'])
                    else:
                        elements = soup.select(selector)
                        for img in elements:
                            if img.get('src'):
                                product_images.append(img['src'])

                if product_images:
                    product_info['images'] = product_images

                # Product SKU/ID
                sku_selectors = [
                    '[itemprop="sku"]',
                    '.sku',
                    '[data-product-id]'
                ]

                for selector in sku_selectors:
                    element = soup.select_one(selector)
                    if element:
                        if selector == '[data-product-id]':
                            product_info['sku'] = element.get('data-product-id')
                        else:
                            product_info['sku'] = element.text.strip()
                        break

                return {
                    "url": url,
                    "title": title,
                    "content_type": "product",
                    "product": product_info
                }

            else:
                # This appears to be a category or other e-commerce page
                # Extract general content
                content_selectors = [
                    '.page-content',
                    '.content',
                    'main',
                    '#content'
                ]

                content_element = None
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        content_element = element
                        break

                # Extract text from content element or fallback to body
                paragraphs = []
                if content_element:
                    for p in content_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                        text = p.get_text().strip()
                        if text:
                            paragraphs.append(text)
                else:
                    for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                        text = p.get_text().strip()
                        if text:
                            paragraphs.append(text)

                content = "\n\n".join(paragraphs)

                # Check if this is a category page
                is_category_page = False
                category_indicators = [
                    '.products',
                    '.product-list',
                    '.category',
                    '.collection'
                ]

                for indicator in category_indicators:
                    if soup.select_one(indicator):
                        is_category_page = True
                        break

                # Extract products on category page
                products = []
                if is_category_page:
                    product_selectors = [
                        '.product',
                        '.product-item',
                        '.product-card',
                        '.collection-item'
                    ]

                    for selector in product_selectors:
                        product_elements = soup.select(selector)
                        for product_element in product_elements:
                            product_data = {}

                            # Extract product name
                            name_element = product_element.select_one('h3') or product_element.select_one(
                                'h2') or product_element.select_one('.name')
                            if name_element:
                                product_data['name'] = name_element.text.strip()

                            # Extract product URL
                            link_element = product_element.select_one('a')
                            if link_element and link_element.get('href'):
                                href = link_element['href']
                                if not href.startswith(('http://', 'https://')):
                                    href = urljoin(url, href)
                                product_data['url'] = href

                            # Extract product price
                            price_element = product_element.select_one('.price')
                            if price_element:
                                product_data['price'] = price_element.text.strip()

                            if product_data:
                                products.append(product_data)

                return {
                    "url": url,
                    "title": title,
                    "content": content,
                    "content_type": "category" if is_category_page else "ecommerce_page",
                    "products": products if products else None
                }

        except Exception as e:
            logger.error(f"Error extracting e-commerce content from {url}: {str(e)}")
            return {"url": url, "error": f"Error extracting content: {str(e)}"}

    async def discover_urls(self, html: str, url: str) -> List[str]:
        """Discover e-commerce-specific URLs from HTML."""
        if not html:
            return []

        discovered_urls = set()

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Find all links
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href'].strip()

                # Skip empty links, anchors, javascript, mailto etc.
                if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue

                # Convert relative URLs to absolute
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)

                # Only include URLs from the same domain
                parsed_href = urlparse(href)
                if parsed_href.netloc == self.domain:
                    # Look for e-commerce-specific patterns
                    ecommerce_patterns = [
                        r'/product/',
                        r'/products/',
                        r'/category/',
                        r'/categories/',
                        r'/catalog/',
                        r'/shop/',
                        r'/item/',
                        r'/collection/'
                    ]

                    for pattern in ecommerce_patterns:
                        if re.search(pattern, href):
                            discovered_urls.add(href)
                            break

                    # Also check for links in product elements
                    if link.parent and any(
                            cls in link.parent.get('class', []) for cls in ['product', 'item', 'product-card']):
                        discovered_urls.add(href)

            return list(discovered_urls)

        except Exception as e:
            logger.error(f"Error discovering e-commerce URLs from {url}: {str(e)}")
            return []


import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import aiohttp
import re
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class DomainCrawler(ABC):
    """Base class for domain-specific crawlers."""

    def __init__(self, base_url: str, user_agent: str = "RAGCrawler"):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.user_agent = user_agent
        self.headers = {
            "User-Agent": f"{user_agent}/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

    @abstractmethod
    async def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract domain-specific content from HTML."""
        pass

    @abstractmethod
    async def discover_urls(self, html: str, url: str) -> List[str]:
        """Discover domain-specific URLs from HTML."""
        pass

    async def fetch_url(self, url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Fetch the content of a URL."""
        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None


class BlogCrawler(DomainCrawler):
    """Crawler optimized for blog websites."""

    async def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract blog-specific content from HTML."""
        if not html:
            return {"url": url, "error": "No HTML content"}

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()

            # Try to find blog post content using common patterns
            content_selectors = [
                'article',
                '.post-content',
                '.entry-content',
                '.blog-post',
                '.article-content',
                '#content',
                '.content',
                'main'
            ]

            content_element = None
            for selector in content_selectors:
                # Try CSS selector
                element = soup.select_one(selector)
                if element:
                    content_element = element
                    break

                # Try HTML tag
                if selector.startswith('.') or selector.startswith('#'):
                    continue
                element = soup.find(selector)
                if element:
                    content_element = element
                    break

            # Extract text from content element or fallback to body
            if content_element:
                paragraphs = content_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'li'])
            else:
                paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

            # Extract text content
            content_parts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 10:  # Skip very short paragraphs
                    content_parts.append(text)

            content = "\n\n".join(content_parts)

            # Extract metadata
            metadata = {}

            # Published date
            date_selectors = [
                'time',
                '.post-date',
                '.entry-date',
                '.published',
                'meta[property="article:published_time"]',
                'meta[property="og:published_time"]'
            ]

            for selector in date_selectors:
                if selector.startswith('meta'):
                    element = soup.select_one(selector)
                    if element and element.get('content'):
                        metadata['published_date'] = element['content']
                        break
                else:
                    element = soup.select_one(selector)
                    if element:
                        if element.get('datetime'):
                            metadata['published_date'] = element['datetime']
                            break
                        elif element.text.strip():
                            metadata['published_date'] = element.text.strip()
                            break

            # Author
            author_selectors = [
                '.author',
                '.byline',
                'meta[name="author"]',
                'meta[property="article:author"]',
                'a[rel="author"]'
            ]

            for selector in author_selectors:
                if selector.startswith('meta'):
                    element = soup.select_one(selector)
                    if element and element.get('content'):
                        metadata['author'] = element['content']
                        break
                else:
                    element = soup.select_one(selector)
                    if element:
                        metadata['author'] = element.text.strip()
                        break

            # Categories/Tags
            tags = []
            tag_selectors = [
                '.tags a',
                '.categories a',
                '.post-tags a',
                'meta[property="article:tag"]'
            ]

            for selector in tag_selectors:
                if selector.startswith('meta'):
                    elements = soup.select(selector)
                    for element in elements:
                        if element.get('content'):
                            tags.append(element['content'])
                else:
                    elements = soup.select(selector)
                    for element in elements:
                        tag_text = element.text.strip()
                        if tag_text:
                            tags.append(tag_text)

            if tags:
                metadata['tags'] = list(set(tags))  # Remove duplicates

            return {
                "url": url,
                "title": title,
                "content": content,
                "metadata": metadata,
                "content_type": "blog"
            }

        except Exception as e:
            logger.error(f"Error extracting blog content from {url}: {str(e)}")
            return {"url": url, "error": f"Error extracting content: {str(e)}"}

    async def discover_urls(self, html: str, url: str) -> List[str]:
        """Discover blog-specific URLs from HTML."""
        if not html:
            return []

        discovered_urls = set()

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Find all links
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href'].strip()

                # Skip empty links, anchors, javascript, mailto etc.
                if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue

                # Convert relative URLs to absolute
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)

                # Only include URLs from the same domain
                parsed_href = urlparse(href)
                if parsed_href.netloc == self.domain:
                    # Look for blog-specific patterns
                    blog_patterns = [
                        r'/blog/',
                        r'/post/',
                        r'/article/',
                        r'/\d{4}/\d{2}/',  # Date-based archives
                        r'/category/',
                        r'/tag/'
                    ]

                    for pattern in blog_patterns:
                        if re.search(pattern, href):
                            discovered_urls.add(href)
                            break

                    # Also check for links in blog index pages
                    if link.parent and (
                            'post' in link.parent.get('class', []) or
                            'blog' in link.parent.get('class', []) or
                            'article' in link.parent.get('class', [])
                    ):
                        discovered_urls.add(href)

            return list(discovered_urls)

        except Exception as e:
            logger.error(f"Error discovering blog URLs from {url}: {str(e)}")
            return []


class DocumentationCrawler(DomainCrawler):
    """Crawler optimized for documentation websites."""

    async def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract documentation-specific content from HTML."""
        if not html:
            return {"url": url, "error": "No HTML content"}

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()

            # Try to find documentation content using common patterns
            content_selectors = [
                '.documentation',
                '.docs',
                '.doc-content',
                '.markdown-body',
                '.content',
                'article',
                'main'
            ]

            content_element = None
            for selector in content_selectors:
                # Try CSS selector
                element = soup.select_one(selector)
                if element:
                    content_element = element
                    break

                # Try HTML tag
                if selector.startswith('.') or selector.startswith('#'):
                    continue
                element = soup.find(selector)
                if element:
                    content_element = element
                    break

            # Extract structured content
            structured_content = {}

            # Extract headings
            headings = []
            if content_element:
                for level in range(1, 7):
                    for heading in content_element.find_all(f'h{level}'):
                        headings.append({
                            "level": level,
                            "text": heading.get_text().strip(),
                            "id": heading.get('id', '')
                        })
            else:
                for level in range(1, 7):
                    for heading in soup.find_all(f'h{level}'):
                        headings.append({
                            "level": level,
                            "text": heading.get_text().strip(),
                            "id": heading.get('id', '')
                        })

            structured_content['headings'] = headings

            # Extract paragraphs and code blocks
            paragraphs = []
            code_blocks = []

            if content_element:
                # Extract paragraphs
                for p in content_element.find_all('p'):
                    text = p.get_text().strip()
                    if text:
                        paragraphs.append(text)

                # Extract code blocks
                for code in content_element.find_all(['pre', 'code']):
                    # Skip if it's a 'code' inside a 'pre' to avoid duplication
                    if code.name == 'code' and code.parent.name == 'pre':
                        continue

                    code_text = code.get_text().strip()
                    if code_text:
                        language = ''
                        if code.get('class'):
                            for cls in code.get('class'):
                                if cls.startswith('language-') or cls.startswith('lang-'):
                                    language = cls.split('-')[1]
                                    break

                        code_blocks.append({
                            "code": code_text,
                            "language": language
                        })
            else:
                # Extract paragraphs
                for p in soup.find_all('p'):
                    text = p.get_text().strip()
                    if text:
                        paragraphs.append(text)

                # Extract code blocks
                for code in soup.find_all(['pre', 'code']):
                    # Skip if it's a 'code' inside a 'pre' to avoid duplication
                    if code.name == 'code' and code.parent.name == 'pre':
                        continue

                    code_text = code.get_text().strip()
                    if code_text:
                        language = ''
                        if code.get('class'):
                            for cls in code.get('class'):
                                if cls.startswith('language-') or cls.startswith('lang-'):
                                    language = cls.split('-')[1]
                                    break

                        code_blocks.append({
                            "code": code_text,
                            "language": language
                        })

            structured_content['paragraphs'] = paragraphs
            structured_content['code_blocks'] = code_blocks

            # Combine content into a single text
            text_parts = []

            # Add headings
            for heading in headings:
                text_parts.append(f"{'#' * heading['level']} {heading['text']}")

            # Add paragraphs
            for paragraph in paragraphs:
                text_parts.append(paragraph)

            # Add code blocks
            for code_block in code_blocks:
                language = code_block['language']
                language_str = f"```{language}\n" if language else "```\n"
                text_parts.append(f"{language_str}{code_block['code']}\n```")

            combined_text = "\n\n".join(text_parts)

            # Extract metadata
            metadata = {}

            # Try to find documentation version
            version_selectors = [
                '.version',
                '.doc-version',
                'meta[name="version"]'
            ]

            for selector in version_selectors:
                if selector.startswith('meta'):
                    element = soup.select_one(selector)
                    if element and element.get('content'):
                        metadata['version'] = element['content']
                        break
                else:
                    element = soup.select_one(selector)
                    if element:
                        metadata['version'] = element.text.strip()
                        break

            return {
                "url": url,
                "title": title,
                "content": combined_text,
                "structured_content": structured_content,
                "metadata": metadata,
                "content_type": "documentation"
            }

        except Exception as e:
            logger.error(f"Error extracting documentation content from {url}: {str(e)}")
            return {"url": url, "error": f"Error extracting content: {str(e)}"}

    async def discover_urls(self, html: str, url: str) -> List[str]:
        """Discover documentation-specific URLs from HTML."""
        if not html:
            return []

        discovered_urls = set()

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Find all links
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href'].strip()

                # Skip empty links, anchors, javascript, mailto etc.
                if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue

                # Convert relative URLs to absolute
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)

                # Only include URLs from the same domain
                parsed_href = urlparse(href)
                if parsed_href.netloc == self.domain:
                    # Look for documentation-specific patterns
                    doc_patterns = [
                        r'/docs/',
                        r'/documentation/',
                        r'/guide/',
                        r'/tutorial/',
                        r'/manual/',
                        r'/reference/',
                        r'/api/'
                    ]

                    for pattern in doc_patterns:
                        if re.search(pattern, href):
                            discovered_urls.add(href)
                            break

                    # Also check for links in navigation elements
                    if link.parent and any(
                            cls in link.parent.get('class', []) for cls in ['nav', 'sidebar', 'toc', 'menu']):
                        discovered_urls.add(href)

            return list(discovered_urls)

        except Exception as e:
            logger.error(f"Error discovering documentation URLs from {url}: {str(e)}")
            return []


class EcommerceCrawler(DomainCrawler):
    """Crawler optimized for e-commerce websites."""

    async def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract e-commerce-specific content from HTML."""
        if not html:
            return {"url": url, "error": "No HTML content"}

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()

            # Check if this is a product page
            is_product_page = False
            product_indicators = [
                'meta[property="og:type"][content="product"]',
                '.product',
                '#product',
                'form[action*="cart"]',
                'button[name*="add"]',
                'input[name*="add_to_cart"]'
            ]

            for indicator in product_indicators:
                if soup.select_one(indicator):
                    is_product_page = True
                    break

            if is_product_page:
                # Extract product information
                product_info = {}

                # Product name
                product_name_selectors = [
                    'h1.product-title',
                    '.product-name',
                    '.product-title',
                    'h1',
                ]

                for selector in product_name_selectors:
                    element = soup.select_one(selector)
                    if element:
                        product_info['name'] = element.text.strip()
                        break

                # Product price
                price_selectors = [
                    '.price',
                    '.product-price',
                    'span[itemprop="price"]',
                    'meta[property="product:price:amount"]'
                ]

                for selector in price_selectors:
                    if selector.startswith('meta'):
                        element = soup.select_one(selector)
                        if element and element.get('content'):
                            product_info['price'] = element['content']
                            break
                    else:
                        element = soup.select_one(selector)
                        if element:
                            product_info['price'] = element.text.strip()
                            break

                # Product description
                description_selectors = [
                    '.product-description',
                    '.description',
                    '[itemprop="description"]',
                    'meta[property="og:description"]'
                ]

                for selector in description_selectors:
                    if selector.startswith('meta'):
                        element = soup.select_one(selector)
                        if element and element.get('content'):
                            product_info['description'] = element['content']
                            break
                    else:
                        element = soup.select_one(selector)
                        if element:
                            product_info['description'] = element.text.strip()
                            break

                # Product images
                image_selectors = [
                    'meta[property="og:image"]',
                    '[itemprop="image"]',
                    '.product-image img',
                    '.product img'
                ]

                product_images = []
                for selector in image_selectors:
                    if selector.startswith('meta'):
                        element = soup.select_one(selector)
                        if element and element.get('content'):
                            product_images.append(element['content'])
                    else:
                        elements = soup.select(selector)
                        for img in elements:
                            if img.get('src'):
                                product_images.append(img['src'])

                if product_images:
                    product_info['images'] = product_images

                # Product SKU/ID
                sku_selectors = [
                    '[itemprop="sku"]',
                    '.sku',
                    '[data-product-id]'
                ]

                for selector in sku_selectors:
                    element = soup.select_one(selector)
                    if element:
                        if selector == '[data-product-id]':
                            product_info['sku'] = element.get('data-product-id')
                        else:
                            product_info['sku'] = element.text.strip()
                        break

                return {
                    "url": url,
                    "title": title,
                    "content_type": "product",
                    "product": product_info
                }

            else:
                # This appears to be a category or other e-commerce page
                # Extract general content
                content_selectors = [
                    '.page-content',
                    '.content',
                    'main',
                    '#content'
                ]

                content_element = None
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        content_element = element
                        break

                # Extract text from content element or fallback to body
                paragraphs = []
                if content_element:
                    for p in content_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                        text = p.get_text().strip()
                        if text:
                            paragraphs.append(text)
                else:
                    for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                        text = p.get_text().strip()
                        if text:
                            paragraphs.append(text)

                content = "\n\n".join(paragraphs)

                # Check if this is a category page
                is_category_page = False
                category_indicators = [
                    '.products',
                    '.product-list',
                    '.category',
                    '.collection'
                ]

                for indicator in category_indicators:
                    if soup.select_one(indicator):
                        is_category_page = True
                        break

                # Extract products on category page
                products = []
                if is_category_page:
                    product_selectors = [
                        '.product',
                        '.product-item',
                        '.product-card',
                        '.collection-item'
                    ]

                    for selector in product_selectors:
                        product_elements = soup.select(selector)
                        for product_element in product_elements:
                            product_data = {}

                            # Extract product name
                            name_element = product_element.select_one('h3') or product_element.select_one(
                                'h2') or product_element.select_one('.name')
                            if name_element:
                                product_data['name'] = name_element.text.strip()

                            # Extract product URL
                            link_element = product_element.select_one('a')
                            if link_element and link_element.get('href'):
                                href = link_element['href']
                                if not href.startswith(('http://', 'https://')):
                                    href = urljoin(url, href)
                                product_data['url'] = href

                            # Extract product price
                            price_element = product_element.select_one('.price')
                            if price_element:
                                product_data['price'] = price_element.text.strip()

                            if product_data:
                                products.append(product_data)

                return {
                    "url": url,
                    "title": title,
                    "content": content,
                    "content_type": "category" if is_category_page else "ecommerce_page",
                    "products": products if products else None
                }

        except Exception as e:
            logger.error(f"Error extracting e-commerce content from {url}: {str(e)}")
            return {"url": url, "error": f"Error extracting content: {str(e)}"}

    async def discover_urls(self, html: str, url: str) -> List[str]:
        """Discover e-commerce-specific URLs from HTML."""
        if not html:
            return []

        discovered_urls = set()

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Find all links
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href'].strip()

                # Skip empty links, anchors, javascript, mailto etc.
                if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue

                # Convert relative URLs to absolute
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)

                # Only include URLs from the same domain
                parsed_href = urlparse(href)
                if parsed_href.netloc == self.domain:
                    # Look for e-commerce-specific patterns
                    ecommerce_patterns = [
                        r'/product/',
                        r'/products/',
                        r'/category/',
                        r'/categories/',
                        r'/catalog/',
                        r'/shop/',
                        r'/item/',
                        r'/collection/'
                    ]

                    for pattern in ecommerce_patterns:
                        if re.search(pattern, href):
                            discovered_urls.add(href)
                            break

                    # Also check for links in product elements
                    if link.parent and any(
                            cls in link.parent.get('class', []) for cls in ['product', 'item', 'product-card']):
                        discovered_urls.add(href)

            return list(discovered_urls)

        except Exception as e:
            logger.error(f"Error discovering e-commerce URLs from {url}: {str(e)}")
            return []


def get_domain_crawler(url: str, user_agent: str = "RAGCrawler") -> DomainCrawler:
    """Factory function to get the appropriate domain crawler for a URL."""
    # Parse URL to determine the appropriate crawler
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()

    # Check URL path patterns to determine website type
    if any(pattern in path for pattern in ['/blog', '/post', '/article', '/news']):
        return BlogCrawler(url, user_agent)
    elif any(pattern in path for pattern in
             ['/docs', '/documentation', '/guide', '/tutorial', '/manual', '/reference', '/api']):
        return DocumentationCrawler(url, user_agent)
    elif any(pattern in path for pattern in ['/product', '/products', '/category', '/shop', '/store', '/item']):
        return EcommerceCrawler(url, user_agent)

    # If no specific pattern matches, try to detect from the HTML content
    # This would require fetching the page and analyzing it
    # For now, default to a generic blog crawler
    return BlogCrawler(url, user_agent)