import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from autogen import Agent, register_function  # Assuming 'autogen' is the library you're using.

class WebCrawlerAgent(Agent):
    def __init__(self, start_url, max_depth=3):
        super().__init__(name="WebCrawlerAgent")
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited = set()
        self.endpoints = set()

    def run(self):
        """Method that gets called to start the crawling process."""
        self._crawl_page(self.start_url, 0)
        return self.endpoints

    def _crawl_page(self, url, depth):
        """Recursively crawls the website to find endpoints."""
        # Avoid going too deep
        if depth > self.max_depth:
            return

        if url in self.visited:
            return

        self.visited.add(url)
        print(f"Crawling: {url} (Depth {depth})")

        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                print(f"Skipping {url} due to status code {response.status_code}")
                return
        except requests.exceptions.RequestException as e:
            print(f"Error crawling {url}: {e}")
            return

        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract and store endpoints
        self._extract_endpoints(url, soup)

        # Find all anchor tags with href attributes
        links = soup.find_all('a', href=True)
        for link in links:
            new_url = urljoin(url, link['href'])  # Resolves relative URLs
            if self._is_valid_url(new_url):
                self._crawl_page(new_url, depth + 1)

    def _extract_endpoints(self, base_url, soup):
        """Extract and store endpoint paths from the given page."""
        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_url, link['href'])  # Resolve relative URLs
            path = urlparse(full_url).path

            # We are only interested in valid endpoint-like paths
            if path and path != '/' and not path.endswith(('.jpg', '.png', '.gif', '.css')):
                # Match for .php, .js files and paths like /example
                if path.endswith('.php') or path.endswith('.js') or (path.startswith('/') and len(path) > 1):
                    self.endpoints.add(path)

    def _is_valid_url(self, url):
        """Ensure the URL is valid."""
        parsed_url = urlparse(url)
        return bool(parsed_url.netloc)  # Valid URL should have a netloc (e.g., www.example.com)

# Register the agent and its function
def start_crawl_task(url):
    """Function to start the crawl task from a URL."""
    crawler = WebCrawlerAgent(start_url=url)
    return crawler.run()

# Register the function so that it can be invoked by other agents or processes.
register_function(start_crawl_task)
