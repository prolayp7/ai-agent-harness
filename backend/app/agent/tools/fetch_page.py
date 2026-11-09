import httpx
from bs4 import BeautifulSoup
from .base import BaseTool

class FetchPageTool(BaseTool):
    name = "fetch_page"
    description = (
        "Fetch the text content of a webpage. "
        "Input should be a full URL (starting with http). "
        "Returns cleaned text content (truncated)."
    )

    def run(self, url: str = "") -> str:
        if not url.startswith("http"):
            return "Error: URL must start with http or https"

        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove scripts and styles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)

            # Limit length so we don't blow the context window
            if len(text) > 3000:
                text = text[:3000] + "\n\n...[truncated]"

            return text if text else "No readable text found on the page."

        except Exception as e:
            return f"Fetch error: {str(e)}"