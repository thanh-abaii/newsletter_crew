from crewai_tools import BaseTool
from exa_py import Exa
from datetime import datetime, timedelta
import os


class Search(BaseTool):
    name: str = "Search Tool"
    description: str = (
        "Searches the web based on a search query. Results are only from the last week. Uses the Exa API."
    )

    def _run(self, search_query: str) -> str:

        one_week_ago = datetime.now() - timedelta(days=7)
        date_cutoff = one_week_ago.strftime("%Y-%m-%d")

        exa = Exa(os.getenv("EXA_API_KEY"))

        search_response = exa.search_and_contents(
            search_query,
            use_autoprompt=True,
            start_published_date=date_cutoff,
            text={"include_html_tags": False, "max_characters": 8000},
        )

        return search_response


class FindSimilar(BaseTool):
    name: str = "Find Similar Tool"
    description: str = (
        "Searches for similar articles to a given article using the Exa API. Takes in a URL of the article."
    )

    def _run(self, url: str) -> str:

        one_week_ago = datetime.now() - timedelta(days=4)
        date_cutoff = one_week_ago.strftime("%Y-%m-%d")

        exa = Exa(os.getenv("EXA_API_KEY"))

        search_response = exa.find_similar(url, start_published_date=date_cutoff)

        return search_response


class GetContents(BaseTool):
    name: str = "Get Contents Tool"
    description: str = (
        "Gets the contents of a specific article using the Exa API. Takes in the ID of the article in a list, like this: ['https://www.cnbc.com/2024/04/18/my-news-story']."
    )

    def _run(self, ids: list[str]) -> str:  # Accepts a list of strings
        exa = Exa(os.getenv("EXA_API_KEY"))
        contents_response = exa.get_contents(ids)
        return contents_response
