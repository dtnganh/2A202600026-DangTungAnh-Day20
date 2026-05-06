"""Optional critic agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentResult, AgentName


class CriticAgent(BaseAgent):
    """Provides feedback and fact-checking."""

    name = "critic"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Evaluate current findings or final answer."""
        
        sys_prompt = "You are a harsh critic and fact checker. Review the current draft and research notes. If there are unsupported claims, missing citations, or hallucinations, point them out clearly. If the draft looks perfect, just output 'PASS'."
        
        content_to_review = state.final_answer or state.research_notes or "Nothing to review."
        
        user_prompt = f"User Request: {state.request.query}\n\nContent to review:\n{content_to_review}"
        
        critic_res = self.llm.complete(sys_prompt, user_prompt)
        
        feedback = critic_res.content.strip()
        if feedback.upper() == "PASS":
            state.critic_feedback = None
        else:
            state.critic_feedback = feedback
            
        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=feedback
            )
        )
        state.add_trace_event("critique_completed", {"passed": state.critic_feedback is None})
        
        return state
