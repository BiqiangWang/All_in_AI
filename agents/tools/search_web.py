"""Search web tool."""

from langchain_core.tools import tool
from pydantic import Field


@tool
def search_web(query: str = Field(description="The search query to look up on the web")) -> str:
    """Search the web for information about a topic or question.

    Use this when you need to find current information, facts, news, or answers
    that require looking up on the internet. Particularly useful for:
    - Looking up documentation for libraries, frameworks, APIs
    - Finding recent events or news
    - Verifying facts you're uncertain about
    - Getting technical specifications

    Args:
        query: The search query to look up. Be specific and include key terms.

    Returns:
        Search results with titles and snippets from DuckDuckGo.
        Results are typically limited to 5 high-quality matches.
    """
    from ddgs import DDGS

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "No results found."
            # Format results cleanly
            formatted = []
            for r in results:
                title = r.get("title", "").strip()
                body = r.get("body", "").strip()
                if title and body:
                    formatted.append(f"{title}\n{body}")
            return "\n\n".join(formatted) if formatted else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"
