"""Telemetry and tracing utilities."""

import logging

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

logger = logging.getLogger("agent-recruiter")

def setup_telemetry(service_name: str = "agent-recruiter"):
    """Initialize OpenTelemetry tracing."""
    
    # Initialize the TracerProvider
    provider = TracerProvider()
    
    # Export to console by default (can be piped to other collectors)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    
    trace.set_tracer_provider(provider)
    
    # Instrument OpenAI
    OpenAIInstrumentor().instrument()
    
    logger.debug(f"Telemetry initialized for {service_name}")

def get_tracer(name: str = "agent-recruiter"):
    return trace.get_tracer(name)
