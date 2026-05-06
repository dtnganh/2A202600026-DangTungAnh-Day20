"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentResult, AgentName


class WriterAgent(BaseAgent):
    """Drafts the final response."""

    name = "writer"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        
        sys_prompt = "You are an expert technical writer. Synthesize the provided research and analysis into a comprehensive, clear, and engaging final response. Make sure to use appropriate Markdown formatting. If sources are provided, cite them appropriately."
        user_prompt = f"User Request: {state.request.query}\nAudience: {state.request.audience}\n\nResearch Notes:\n{state.research_notes or 'None'}\n\nAnalysis Notes:\n{state.analysis_notes or 'None'}\n\nCritic Feedback (if any):\n{state.critic_feedback or 'None'}"
        
        writer_res = self.llm.complete(sys_prompt, user_prompt)
        state.final_answer = writer_res.content
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=writer_res.content
            )
        )
        state.add_trace_event("writing_completed", {})
        
        return state
