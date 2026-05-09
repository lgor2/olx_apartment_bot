import re
import requests
import logging
import logging_config
from multiprocessing import Pool
from urllib.parse import urlparse
from bs4 import BeautifulSoup, ResultSet, Tag
from utils import get_header


class OlxScraper:
    """Class used to scrape data from OLX Romania."""

    def __init__(self):
        self.headers = get_header()
        self.schema = "https"
        self.current_page = 1
        self.last_page = None

    def parse_content(self, target_url: str) -> BeautifulSoup:
        """
        Parse content from a given URL.

        Args:
            target_url (str): A string representing the URL to be processed.

        Returns:
            BeautifulSoup: An object representing the processed content,
            or None in case of error.
        """
        try:
            r = requests.get(target_url, headers=self.headers, timeout=60)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            logging.error(f"Connection error: {error}")
        else:
            parsed_content = BeautifulSoup(r.text, "html.parser")
            return parsed_content

    def get_ads(self, parsed_content: BeautifulSoup) -> list:
        """
        Returns all ads found on the parsed web page.

        Args:
            parsed_content (BeautifulSoup): a BeautifulSoup object created as
            a result of parsing the web page.

        Returns:
            list: A list containing all HTML tags that contain ads.
        """
        if parsed_content is None:
            return []
        ads = parsed_content.find_all("a", href=True)
        return [a for a in ads if "/obyavlenie/" in a["href"]]

    def get_last_page(self, parsed_content: BeautifulSoup) -> int:
        """
        Returns the number of the last page available for processing.

        Args:
            parsed_content (BeautifulSoup): a BeautifulSoup object created
            as a result of parsing the web page.

        Returns:
            int: The number of the last page available for parsing. If
            there is no paging or the parsed object is None, it will return None.
        """
        if parsed_content is not None:
            pagination_ul = parsed_content.find("ul", class_="pagination-list")
            if pagination_ul is not None:
                pages = pagination_ul.find_all("li", class_="pagination-item")
                if pages:
                    return int(pages[-1].text)
        return None

    def scrape_ads_urls(self, target_url: str) -> list:
        """
        Scrapes the URLs of all valid ads present on an OLX page. Search all relevant
        URLs of the ads and adds them to a set. Parses all pages, from first to last.

        Args:
            target_url (str): URL of the OLX page to start the search from.

        Returns:
            list: a list of relevant URLs of the ads found on the page.

        Raises:
            ValueError: If the URL is invalid or does not belong to the specified domain.
        """
        ads_links = set()
        self.current_page = 1
        self.netloc = urlparse(target_url).netloc
        if "olx" not in self.netloc:
            raise ValueError(
                "Bad URL! OLXRadar is configured to process OLX links only.")
        while True:
            if "?" in target_url:
                url = f"{target_url}&page={self.current_page}"
            else:
                url = f"{target_url}/?page={self.current_page}"
            parsed_content = self.parse_content(url)
            self.last_page = self.get_last_page(parsed_content)
            ads = self.get_ads(parsed_content)
            if not ads:
                break
            for link in ads:
                link_href = link["href"]
                if not self.is_internal_url(link_href, self.netloc):
                    continue
                if not self.is_relevant_url(link_href):
                    continue
                if self.is_relative_url(link_href):
                    link_href = f"{self.schema}://{self.netloc}{link_href}"
                ads_links.add(link_href)
            if self.last_page is None or self.current_page >= self.last_page:
                break
            self.current_page += 1
        return ads_links

    def is_relevant_url(self, url: str) -> bool:
        """
        Determines whether a particular URL is relevant by analyzing the query segment it contains.
        """
        # Removed query filtering as OLX adds tracking parameters to all URLs now
        return True

    def is_internal_url(self, url: str, domain: str) -> bool:
        """
        Checks if the URL has the same domain as the page it was taken from.

        Args:
            url (str): the URL to check.
            domain (str): Domain of the current page.

        Returns:
            bool: True if the URL is an internal link, False otherwise.
        """
        # URL starts with "/"
        if self.is_relative_url(url):
            return True
        parsed_url = urlparse(url)
        if parsed_url.netloc == domain:
            return True
        return False

    def is_relative_url(self, url: str) -> bool:
        """
        Check if the given url is relative or absolute.

        Args:
            url (str): url to check.

        Returns:
            True if the url is relative, otherwise False.
        """

        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            return True
        if re.search(r"^\/[\w.\-\/]+", url):
            return True
        return False

    def get_ad_data(self, ad_url: str) -> dict[str]:
        """
        Extracts data from the HTML page of the ad.

        Args:
            ad_url (str): the URL of the ad.

        Returns:
            dict or None: A dictionary containing the scraped ad data
            or None if the required information is missing.
        """
        logging.info(f"Processing {ad_url}")
        content = self.parse_content(ad_url)

        if content is None:
            return None

        title = None
        if content.title and content.title.string:
            title = content.title.string.split(" - ")[0]
            
        price = "Не вказана"
        if title and ":" in title:
            parts = title.split(":")
            price = parts[-1].strip()
            title = ":".join(parts[:-1]).strip()

        description_meta = content.find("meta", attrs={"name": "description"})
        description = description_meta.get("content") if description_meta else "Без опису"

        if title is None:
            return None
            
        ad_data = {
            "title": title,
            "price": price,
            "url": ad_url,
            "description": description
        }
        return ad_data
