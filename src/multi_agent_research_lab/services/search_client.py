"""Search client abstraction for ResearcherAgent."""

import os
from langchain_community.tools.tavily_search import TavilySearchResults
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def __init__(self):
        self.tavily = TavilySearchResults(max_results=5)

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        self.tavily.max_results = max_results
        results = self.tavily.invoke({"query": query})
        
        source_docs = []
        for res in results:
            source_docs.append(
                SourceDocument(
                    title=res.get("title", "Unknown Title"),
                    url=res.get("url"),
                    snippet=res.get("content", ""),
                    metadata={"score": res.get("score")}
                )
            )
        return source_docs
