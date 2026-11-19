
import os
import requests

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from tavily import TavilyClient
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()


# Get Tavily client safely
def get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY is missing. Add it to your .env "
            "file or deployment secrets."
        )

    return TavilyClient(api_key=api_key)


# 1. Web Search Tool
@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information.
    Returns titles, URLs and relevant snippets."""

    try:
        tavily = get_tavily_client()

        results = tavily.search(
            query=query,
            max_results=5
        )

        output = []

        for result in results.get("results", []):
            output.append(
                f"Title: {result.get('title', 'No title')}\n"
                f"URL: {result.get('url', 'No URL')}\n"
                f"Snippet: {result.get('content', '')[:300]}\n"
            )

        if not output:
            return "No search results found."

        return "\n-----\n".join(output)

    except Exception as e:
        return f"Web search failed: {str(e)}"


# 2. URL Scraping Tool
@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a valid webpage URL."""

    try:
        parsed_url = urlparse(url)

        if parsed_url.scheme not in ("http", "https"):
            return "Invalid URL: Only HTTP and HTTPS URLs are supported."

        if not parsed_url.hostname:
            return "Invalid URL: Missing hostname."

        response = requests.get(
            url,
            timeout=(5, 15),
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type.lower():
            return "This URL does not contain an HTML webpage."

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unnecessary HTML elements
        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript"
        ]):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        if not text:
            return "No readable content found on this webpage."

        return text[:5000]

    except requests.exceptions.Timeout:
        return "Scraping failed: Website request timed out."

    except requests.exceptions.HTTPError as e:
        return f"Scraping failed: HTTP error: {str(e)}"

    except requests.exceptions.RequestException as e:
        return f"Scraping failed: Network error: {str(e)}"

    except Exception as e:
        return f"Scraping failed: {str(e)}"
