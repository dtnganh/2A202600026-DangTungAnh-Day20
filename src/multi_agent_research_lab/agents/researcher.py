"""Researcher agent skeleton."""

import json
from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient
from multi_agent_research_lab.core.schemas import AgentResult, AgentName


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self):
        self.llm = LLMClient()
        self.search_client = SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        
        # 1. Determine search query
        sys_prompt = "You are a smart researcher. Generate exactly ONE concise search query to find information for the user request. Output ONLY the query."
        user_prompt = f"Request: {state.request.query}"
        if state.critic_feedback:
            user_prompt += f"\nCritic Feedback: {state.critic_feedback}"
            
        search_query_res = self.llm.complete(sys_prompt, user_prompt)
        search_query = search_query_res.content.strip('"\'')
        
        # 2. Search
        docs = self.search_client.search(search_query, max_results=state.request.max_sources)
        state.sources.extend(docs)
        
        # 3. Compile notes
        doc_texts = "\n\n".join([f"Source {i+1} ({d.title}): {d.snippet}" for i, d in enumerate(docs)])
        notes_sys_prompt = "You are a researcher. Synthesize the provided sources into concise research notes with facts and citations (Source X)."
        notes_user_prompt = f"Sources:\n{doc_texts}\n\nUser Request: {state.request.query}"
        
        notes_res = self.llm.complete(notes_sys_prompt, notes_user_prompt)
        state.research_notes = notes_res.content
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=notes_res.content,
                metadata={"search_query": search_query, "sources_count": len(docs)}
            )
        )
        state.add_trace_event("research_completed", {"query": search_query})
        
        return state
