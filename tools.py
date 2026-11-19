
import os
import requests

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from tavily import TavilyClient
from langchain.tools import tool
from dotenv import load_dotenv


# --------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# 2. GET TAVILY API KEY
# --------------------------------------------------

def get_tavily_api_key():

    api_key = os.getenv("TAVILY_API_KEY", "").strip()

    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get(
                "TAVILY_API_KEY", ""
            ).strip()
        except Exception:
            api_key = ""

    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY is missing. "
            "Configure it in Render Environment Variables."
        )

    return api_key


# --------------------------------------------------
# 3. INITIALIZE TAVILY CLIENT
# --------------------------------------------------

def get_tavily_client():

    api_key = get_tavily_api_key()

    return TavilyClient(api_key=api_key)


# --------------------------------------------------
# 4. WEB SEARCH TOOL
# --------------------------------------------------

@tool
def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information.

    Returns:
        Titles, URLs and relevant snippets.
    """

    try:

        if not query or not query.strip():
            return "Search failed: Research query cannot be empty."

        tavily = get_tavily_client()

        results = tavily.search(
            query=query.strip(),
            max_results=5,
            search_depth="advanced"
        )

        search_results = results.get("results", [])

        if not search_results:
            return "No relevant search results found."

        output = []

        for index, result in enumerate(search_results, start=1):

            title = result.get("title", "No title")
            url = result.get("url", "No URL")
            content = result.get("content", "")

            output.append(
                f"""
SOURCE {index}

Title: {title}

URL: {url}

Snippet:
{content[:1000]}
"""
            )

        return "\n\n--------------------------\n".join(output)

    except Exception as e:

        return f"Web search failed: {str(e)}"


# --------------------------------------------------
# 5. URL VALIDATION
# --------------------------------------------------

def validate_url(url: str):

    try:

        parsed_url = urlparse(url)

        if parsed_url.scheme not in ("http", "https"):
            return False

        if not parsed_url.hostname:
            return False

        if parsed_url.username or parsed_url.password:
            return False

        return True

    except Exception:
        return False


# --------------------------------------------------
# 6. URL SCRAPING TOOL
# --------------------------------------------------

@tool
def scrape_url(url: str) -> str:
    """
    Scrape a webpage and extract clean readable text.

    Returns:
        Extracted webpage content.
    """

    try:

        if not url or not url.strip():
            return "Scraping failed: URL cannot be empty."

        url = url.strip()

        if not validate_url(url):
            return (
                "Invalid URL: Only valid HTTP and HTTPS "
                "webpage URLs are supported."
            )

        response = requests.get(
            url,
            timeout=(10, 20),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; "
                    "ResearchBot/1.0)"
                )
            },
            allow_redirects=True
        )

        response.raise_for_status()

        # Validate final redirected URL
        if not validate_url(response.url):
            return "Scraping failed: Invalid redirect URL."

        content_type = response.headers.get(
            "Content-Type", ""
        )

        if "text/html" not in content_type.lower():
            return (
                "This URL does not contain an HTML webpage."
            )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove unnecessary HTML elements
        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript",
            "iframe",
            "svg"
        ]):
            tag.decompose()

        # Extract page title
        title = (
            soup.title.get_text(strip=True)
            if soup.title else "Untitled webpage"
        )

        # Extract readable content
        text = soup.get_text(
            separator=" ",
            strip=True
        )

        if not text:
            return "No readable content found on this webpage."

        # Limit extracted content
        extracted_content = text[:7000]

        return (
            f"PAGE TITLE: {title}\n\n"
            f"URL: {response.url}\n\n"
            f"EXTRACTED CONTENT:\n"
            f"{extracted_content}"
        )

    except requests.exceptions.Timeout:

        return (
            "Scraping failed: Website request timed out."
        )

    except requests.exceptions.HTTPError as e:

        return f"Scraping failed: HTTP error: {str(e)}"

    except requests.exceptions.RequestException as e:

        return f"Scraping failed: Network error: {str(e)}"

    except Exception as e:

        return f"Scraping failed: {str(e)}"


# --------------------------------------------------
# 7. CONFIGURATION CHECK
# --------------------------------------------------

def check_tools_configuration():

    tavily_key = get_tavily_api_key()

    return {
        "status": "configured",
        "tavily_api_key_loaded": bool(tavily_key),
        "tools": [
            "web_search",
            "scrape_url"
        ]
    }
