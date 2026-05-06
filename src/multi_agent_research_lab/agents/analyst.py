"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentResult, AgentName


class AnalystAgent(BaseAgent):
    """Analyzes sources to find conflicts and missing info."""

    name = "analyst"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        
        sys_prompt = "You are a critical data analyst. Analyze the provided research notes. Extract key claims, compare viewpoints, and flag weak evidence or missing information. Output concise analysis."
        user_prompt = f"Research Notes:\n{state.research_notes or 'None'}\n\nUser Request: {state.request.query}"
        
        analysis_res = self.llm.complete(sys_prompt, user_prompt)
        state.analysis_notes = analysis_res.content
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content=analysis_res.content
            )
        )
        state.add_trace_event("analysis_completed", {})
        
        return state
