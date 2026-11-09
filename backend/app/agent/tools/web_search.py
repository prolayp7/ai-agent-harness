from duckduckgo_search import DDGS
from .base import BaseTool

class WebSearchTool(BaseTool):
    name = "web_search"
    description = (
        "Search the web for current information. "
        "Input should be a clear search query. "
        "Returns top search results with title, link and snippet."
    )

    def run(self, query: str = "") -> str:
        if not query:
            return "Error: query is required"

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

            if not results:
                return "No results found."

            formatted = []
            for i, r in enumerate(results, 1):
                formatted.append(
                    f"{i}. {r.get('title')}\n"
                    f"   URL: {r.get('href')}\n"
                    f"   {r.get('body')}"
                )
            return "\n\n".join(formatted)

        except Exception as e:
            return f"Search error: {str(e)}"