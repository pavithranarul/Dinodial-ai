"""
Model configuration for Dinodial Proxy API make-call endpoint.
Loads default payload structure from make-call-request.json file.
"""
import json
import os
from pathlib import Path

# Path to the JSON file with default configuration
JSON_CONFIG_PATH = Path(__file__).parent / "make-call-request.json"

# Load defaults from JSON file
def _load_defaults():
    """Load default configuration from JSON file."""
    try:
        with open(JSON_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("prompt", ""), config.get("evaluation_tool", {}), config.get("vad_engine", "CAWL")
    except FileNotFoundError:
        # Fallback if JSON file doesn't exist
        return "", {}, "CAWL"
    except json.JSONDecodeError:
        # Fallback if JSON is invalid
        return "", {}, "CAWL"

# Load defaults from JSON file
DEFAULT_PROMPT, DEFAULT_EVALUATION_TOOL, DEFAULT_VAD_ENGINE = _load_defaults()


def get_make_call_payload(
    prompt: str = None,
    evaluation_tool: dict = None,
    vad_engine: str = None
) -> dict:
    """
    Get the payload structure for make-call API.
    
    Args:
        prompt: Custom prompt string. If None, uses DEFAULT_PROMPT
        evaluation_tool: Custom evaluation tool config. If None, uses DEFAULT_EVALUATION_TOOL
        vad_engine: VAD engine name. If None, uses DEFAULT_VAD_ENGINE
        
    Returns:
        Dict with prompt, evaluation_tool, and vad_engine
    """
    return {
        "prompt": prompt or DEFAULT_PROMPT,
        "evaluation_tool": evaluation_tool or DEFAULT_EVALUATION_TOOL,
        "vad_engine": vad_engine or DEFAULT_VAD_ENGINE
    }

