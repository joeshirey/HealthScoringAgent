"""
This module defines the shared generation configuration for all LLM agents.
"""

from google.genai import types

GENERATE_CONTENT_CONFIG = types.GenerateContentConfig(
    temperature=0.0, max_output_tokens=8192
)
