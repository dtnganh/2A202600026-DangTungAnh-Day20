"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any
import os

# Optionally import langsmith if enabled
try:
    from langsmith.run_helpers import trace
except ImportError:
    trace = None


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context used by the skeleton."""

    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    
    # If LangSmith is enabled via env variables, use it
    if trace and os.getenv("LANGSMITH_API_KEY"):
        with trace(name=name, inputs=attributes or {}) as ls_run:
            try:
                yield span
                if ls_run:
                    ls_run.end(outputs=span)
            finally:
                span["duration_seconds"] = perf_counter() - started
    else:
        try:
            yield span
        finally:
            span["duration_seconds"] = perf_counter() - started
