"""Actions for Google Search

Currently supporting:
- google search
"""

from sema4ai.actions import action, Secret, ActionError

from dotenv import load_dotenv

import os
from pathlib import Path
import requests

from models import (
    SearchResultList,
    SearchResult,
)


load_dotenv(Path(__file__).absolute().parent / "devdata" / ".env")

API_KEY_FIELD = "GOOGLE_SEARCH_API_KEY"
CONTEXT_FIELD = "GOOGLE_SEARCH_CONTEXT"


@action(is_consequential=False)
def google_search(
    topic: str,
    count: int = 10,
    api_key: Secret = Secret.model_validate(os.getenv(API_KEY_FIELD, "")),
    context: Secret = Secret.model_validate(os.getenv(CONTEXT_FIELD, "")),
) -> SearchResultList:
    """Performs Google Search to find information about a topic.

    Secrets are required. Do not call if they are given.

    To list all possible results use count=0.

    Args:
        topic: topic to search on
        count: count on how many results to retrieve
        api_key: the Google Custom Search API key
        context: the Custom Search Engine ID

    Returns:
        Titles and links of the results.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key.value or os.getenv(API_KEY_FIELD, ""),
        "cx": context.value or os.getenv(CONTEXT_FIELD, ""),
        "q": topic,
    }
    response = requests.get(url, params=params)
    if response.status_code not in [200, 201]:
        raise ActionError(f"Failed to search. Error: {response.text}")
    result = response.json()
    items = []
    if "items" in result.keys():
        for item in result["items"]:
            items.append(
                SearchResult(
                    title=item["title"], link=item["link"], desc=item["snippet"]
                )
            )

    message = f"Found {len(items)} results for '{topic}'"
    if count > 0:
        message += f" and returning {count} of those."
    print(message)
    return (
        SearchResultList(results=items[:count])
        if count > 0
        else SearchResultList(results=items)
    )
