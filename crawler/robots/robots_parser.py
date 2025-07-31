import aiohttp
import logging
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class RobotsParser:
    """Parser for robots.txt files to ensure crawler compliance."""

    def __init__(self, user_agent: str = "RAGCrawler"):
        self.user_agent = user_agent
        self.robots_cache: Dict[str, Dict[str, List[str]]] = {}

    async def fetch_robots_txt(self, base_url: str) -> Optional[str]:
        """Fetch the robots.txt file from a website."""
        try:
            parsed_url = urlparse(base_url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"Could not fetch robots.txt from {robots_url}: HTTP {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching robots.txt from {base_url}: {str(e)}")
            return None

    def parse_robots_txt(self, robots_content: str) -> Dict[str, List[str]]:
        """Parse the robots.txt content into rules."""
        if not robots_content:
            return {"*": []}

        rules: Dict[str, List[str]] = {}
        current_agent = None

        lines = robots_content.split("\n")
        for line in lines:
            # Remove comments
            if "#" in line:
                line = line[:line.index("#")]

            line = line.strip()
            if not line:
                continue

            parts = line.split(":", 1)
            if len(parts) != 2:
                continue

            directive = parts[0].strip().lower()
            value = parts[1].strip()

            if directive == "user-agent":
                current_agent = value.lower()
                if current_agent not in rules:
                    rules[current_agent] = []
            elif directive == "disallow" and current_agent:
                if value:
                    rules[current_agent].append(value)
            elif directive == "allow" and current_agent:
                # For now, we're just tracking Disallows
                # Could extend to handle Allow directives for more sophisticated crawlers
                pass
            elif directive == "crawl-delay" and current_agent:
                # Store crawl delay as a special rule
                try:
                    rules[f"{current_agent}_crawl_delay"] = float(value)
                except ValueError:
                    pass

        # If no rules were found, create an empty rule set for all agents
        if not rules:
            rules["*"] = []

        return rules

    def get_crawl_delay(self, rules: Dict[str, List[str]]) -> float:
        """Extract crawl delay from rules."""
        # Check for specific user agent crawl delay
        specific_delay_key = f"{self.user_agent.lower()}_crawl_delay"
        if specific_delay_key in rules:
            return rules[specific_delay_key]

        # Check for wildcard crawl delay
        wildcard_delay_key = "*_crawl_delay"
        if wildcard_delay_key in rules:
            return rules[wildcard_delay_key]

        # Default crawl delay
        return 1.0  # 1 second

    async def is_allowed(self, url: str) -> tuple[bool, float]:
        """
        Check if a URL is allowed to be crawled according to robots.txt rules.
        Returns a tuple of (is_allowed, crawl_delay).
        """
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        path = parsed_url.path or "/"

        # Check cache first
        if base_url not in self.robots_cache:
            robots_content = await self.fetch_robots_txt(base_url)
            rules = self.parse_robots_txt(robots_content)
            self.robots_cache[base_url] = rules
        else:
            rules = self.robots_cache[base_url]

        # Get crawl delay
        crawl_delay = self.get_crawl_delay(rules)

        # Check if URL is allowed
        user_agent_rules = []

        # Try to find rules for our specific user agent
        if self.user_agent.lower() in rules:
            user_agent_rules = rules[self.user_agent.lower()]
        # If no specific rules, use wildcard rules
        elif "*" in rules:
            user_agent_rules = rules["*"]

        # Check if the URL path matches any disallow rule
        for rule in user_agent_rules:
            if path.startswith(rule):
                return False, crawl_delay

        # If no matching disallow rule, the URL is allowed
        return True, crawl_delay

    def get_allowed_urls(self, base_url: str, urls: List[str]) -> List[str]:
        """Filter a list of URLs to only those allowed by robots.txt."""
        allowed_urls = []
        for url in urls:
            if self.is_allowed(url)[0]:
                allowed_urls.append(url)
        return allowed_urls