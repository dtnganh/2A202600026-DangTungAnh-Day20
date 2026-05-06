"""Command-line entrypoint for the lab starter."""

import os
from dotenv import load_dotenv
load_dotenv()

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    try:
        from multi_agent_research_lab.services.llm_client import LLMClient
        client = LLMClient()
        system_prompt = "You are a helpful research assistant. Answer the user's query comprehensively."
        response = client.complete(system_prompt=system_prompt, user_prompt=query)
        
        state.final_answer = response.content
        console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline Result"))
        
        if response.cost_usd or response.input_tokens:
            metrics_str = f"Tokens: In={response.input_tokens}, Out={response.output_tokens}"
            console.print(Panel.fit(metrics_str, title="Metrics"))
            
    except Exception as e:
        console.print(Panel.fit(f"Error calling LLM: {e}", style="red"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
