from __future__ import annotations

from urllib.parse import quote

import requests
import streamlit as st


HUMAN_AND_ANIMAL_KEYWORDS = {
    "person",
    "people",
    "human",
    "face",
    "man",
    "woman",
    "child",
    "kid",
    "boy",
    "girl",
    "dog",
    "cat",
    "bird",
    "cow",
    "horse",
    "sheep",
    "goat",
    "bear",
    "deer",
    "elephant",
    "monkey",
    "lion",
    "tiger",
    "zebra",
    "giraffe",
    "rabbit",
    "fish",
    "snake",
    "frog",
    "mouse",
    "rat",
    "pig",
    "chicken",
}


def is_filterable_label(label: str) -> bool:
    normalized = label.strip().lower()
    return any(keyword in normalized for keyword in HUMAN_AND_ANIMAL_KEYWORDS)


def _search_wikipedia_title(query: str) -> str | None:
    response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "utf8": 1,
            "srlimit": 1,
        },
        timeout=8,
    )
    response.raise_for_status()
    payload = response.json()
    search_results = payload.get("query", {}).get("search", [])
    if not search_results:
        return None
    return search_results[0].get("title")


@st.cache_data(show_spinner=False, ttl=24 * 60 * 60)
def lookup_object_info(query: str) -> dict[str, str]:
    cleaned_query = query.strip()
    if not cleaned_query:
        return {
            "title": "",
            "summary": "No object name was provided.",
            "url": "",
            "source": "unknown",
        }

    try:
        page_title = _search_wikipedia_title(cleaned_query) or cleaned_query
        summary_response = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(page_title)}",
            timeout=8,
        )
        summary_response.raise_for_status()
        summary_data = summary_response.json()

        return {
            "title": summary_data.get("title", page_title),
            "summary": summary_data.get("extract")
            or f"A public summary for {cleaned_query} was not available.",
            "url": summary_data.get(
                "content_urls", {}
            ).get("desktop", {}).get(
                "page", f"https://en.wikipedia.org/wiki/{quote(page_title)}"
            ),
            "source": "wikipedia",
        }
    except Exception:
        return {
            "title": cleaned_query,
            "summary": (
                f"A public summary for {cleaned_query} could not be fetched at the moment. "
                "The item is still searchable on the web."
            ),
            "url": f"https://en.wikipedia.org/w/index.php?search={quote(cleaned_query)}",
            "source": "search",
        }
