"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a placeholder metric object."""

    started = perf_counter()
    try:
        state = runner(query)
        error_rate = 0.0
    except Exception as e:
        state = ResearchState(request={"query": query}) # fallback
        state.errors.append(str(e))
        error_rate = 1.0

    latency = perf_counter() - started
    
    # Calculate estimated cost (assume gpt-4o-mini prices: roughly $0.15/1M input, $0.60/1M output)
    total_in = sum(res.metadata.get("input_tokens", 0) for res in state.agent_results)
    total_out = sum(res.metadata.get("output_tokens", 0) for res in state.agent_results)
    cost = (total_in * 0.15 / 1_000_000) + (total_out * 0.60 / 1_000_000)
    
    # Citation coverage (naive check: count "[Source" in final answer)
    has_citations = "[Source" in (state.final_answer or "")
    
    metrics = BenchmarkMetrics(
        run_name=run_name, 
        latency_seconds=latency,
        estimated_cost_usd=cost,
        quality_score=None, # Leave None for manual evaluation via Gemini
        notes=f"Error Rate: {error_rate}. Has Citations: {has_citations}. Evaluator: Manual via Gemini."
    )
    return state, metrics
