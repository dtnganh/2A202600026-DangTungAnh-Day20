"""LangGraph workflow skeleton."""

from langgraph.graph import StateGraph, START, END
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.agents.critic import CriticAgent


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.critic = CriticAgent()
        self.app = self.build()

    def build(self) -> object:
        """Create a LangGraph graph."""
        
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("supervisor", self.supervisor.run)
        workflow.add_node("researcher", self.researcher.run)
        workflow.add_node("analyst", self.analyst.run)
        workflow.add_node("writer", self.writer.run)
        workflow.add_node("critic", self.critic.run)
        
        # Add edges
        workflow.add_edge(START, "supervisor")
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")
        workflow.add_edge("critic", "supervisor")
        
        # Conditional edge from supervisor
        def route_condition(state: ResearchState) -> str:
            if state.route_history:
                next_route = state.route_history[-1]
                if next_route in ["researcher", "analyst", "writer", "critic"]:
                    return next_route
            return "done"

        workflow.add_conditional_edges(
            "supervisor",
            route_condition,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "critic": "critic",
                "done": END
            }
        )
        
        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        
        # Invoke the graph
        result = self.app.invoke(state)
        
        # LangGraph returns a dict, so we convert it back to ResearchState
        if isinstance(result, dict):
            return ResearchState(**result)
        return result
