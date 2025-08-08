import os
from io import BytesIO

from ludika_backend.utils.config import get_config_value
from ludika_backend.utils.uri_safety import is_private_ip
import requests
from ludika_backend.utils.logs import get_logger

GOOGLE_CUSTOM_SEARCH_API_KEY = os.getenv(
    "GOOGLE_CUSTOM_SEARCH_API_KEY"
) or get_config_value("GenerativeAI", "google_custom_search_api_key")
CSE_ID = "c367fb16a0eb44cea"


def get_image_links(search_query: str) -> list[str]:
    """Grab a list of image links from a search query using Google Custom Search API."""
    image_links = []
    query = {
        "key": GOOGLE_CUSTOM_SEARCH_API_KEY,
        "cx": CSE_ID,
        "q": search_query,
    }
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=query)
    if response.status_code != 200:
        get_logger().error(
            f"Failed to get image links: {response.status_code} {response.text}"
        )
        return image_links

    for item in response.json()["items"]:
        if item["kind"] == "customsearch#result":
            if "pagemap" in item:
                pagemap = item["pagemap"]
                if "cse_image" in pagemap:
                    if len(pagemap["cse_image"]) > 0:
                        if "src" in pagemap["cse_image"][0]:
                            image_links.append(pagemap["cse_image"][0]["src"])
                    continue
                elif "metatags" in pagemap:
                    metatags = pagemap["metatags"]
                    if len(metatags) > 0:
                        if "og:image" in metatags[0]:
                            image_links.append(metatags[0]["og:image"])
                        continue
    return image_links


def _get_image_from_url(url: str) -> BytesIO | None:
    """Download an image from a URL and return it as a BytesIO object."""

    if is_private_ip(url):
        get_logger().warning(f"Attempting to access a private IP address: {url}")
        return None
    response = requests.get(url)
    if response.status_code != 200:
        get_logger().error(
            f"Failed to get image from URL: {response.status_code} {response.text}"
        )
        return None
    return BytesIO(response.content)


def get_first_image_from_query(search_query: str) -> BytesIO | None:
    """Get the first image from a search query."""
    image_links = get_image_links(search_query)
    if len(image_links) == 0:
        get_logger().warning(f"No image links found for search query: {search_query}")
        return None
    while len(image_links) > 0:
        image_url = image_links.pop(0)
        try:
            image = _get_image_from_url(image_url)
            if image:
                return image
        except Exception as e:
            get_logger().warning(f"Failed to get image from URL: {image_url}: {str(e)}")
            continue
    return None
