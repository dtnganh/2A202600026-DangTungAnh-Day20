"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.config import get_settings


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self):
        self.llm = LLMClient()
        self.settings = get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        
        if state.iteration >= self.settings.max_iterations:
            next_route = "done"
            state.add_trace_event("supervisor_decision", {"route": next_route, "reason": "max_iterations_reached"})
            state.record_route(next_route)
            return state

        sys_prompt = """You are a Supervisor Agent coordinating a research team.
Your available agents are:
- researcher: to gather information from the web.
- analyst: to analyze the gathered research.
- writer: to draft the final response.
- critic: to review the draft and fact-check.
- done: to finish the workflow.

Rules:
1. Start with researcher.
2. If research is sufficient, go to analyst.
3. If analysis is done, go to writer.
4. If a draft is written, go to critic.
5. If critic provides feedback, go to researcher or writer to fix it.
6. If critic says PASS (no feedback) or draft is satisfactory, output 'done'.

Output ONLY the exact name of the next agent (researcher, analyst, writer, critic, or done)."""

        user_prompt = f"""User Request: {state.request.query}
Current State:
- Route History: {state.route_history}
- Research Notes: {"Yes" if state.research_notes else "No"}
- Analysis Notes: {"Yes" if state.analysis_notes else "No"}
- Final Answer Drafted: {"Yes" if state.final_answer else "No"}
- Critic Feedback: {state.critic_feedback if state.critic_feedback else "None"}"""

        decision_res = self.llm.complete(sys_prompt, user_prompt)
        next_route = decision_res.content.strip().lower()
        
        valid_routes = ["researcher", "analyst", "writer", "critic", "done"]
        if next_route not in valid_routes:
            next_route = "done" # fallback
            
        state.add_trace_event("supervisor_decision", {"route": next_route})
        state.record_route(next_route)
        
        return state
