"""
Model configuration for Dinodial Proxy API make-call endpoint.
Loads default payload structure from make-call-request.json file.
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict

JSON_CONFIG_PATH = Path(__file__).parent / "make-call-request.json"

def _load_defaults():
    """Load default configuration from JSON file."""
    try:
        with open(JSON_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("prompt", ""), config.get("evaluation_tool", {}), config.get("vad_engine", "CAWL")
    except FileNotFoundError:
        return "", {}, "CAWL"
    except json.JSONDecodeError:
        return "", {}, "CAWL"

DEFAULT_PROMPT, DEFAULT_EVALUATION_TOOL, DEFAULT_VAD_ENGINE = _load_defaults()

def generate_dynamic_prompt(customer_name: str, base_prompt: Optional[str] = None) -> str:
    prompt = base_prompt or DEFAULT_PROMPT
    
    if not customer_name:
        customer_name = "Hi there"
    else:
        customer_name = customer_name
    prompt = prompt.replace("{{customer_name}}", customer_name)
    print("prompt: ", prompt)
    return prompt


def get_make_call_payload(
    prompt: str = None,
    evaluation_tool: dict = None,
    vad_engine: str = None,
    customer_name: Optional[str] = None,
    admin_token: Optional[str] = None,
) -> dict:
    """
    Get the payload structure for make-call API.
    
    Args:
        prompt: Custom prompt string. If None, uses DEFAULT_PROMPT or generates dynamic prompt
        evaluation_tool: Custom evaluation tool config. If None, uses DEFAULT_EVALUATION_TOOL
        vad_engine: VAD engine name. If None, uses DEFAULT_VAD_ENGINE
        customer_name: Customer name for dynamic prompt generation
        admin_token: Admin token for dynamic prompt generation
        
    Returns:
        Dict with prompt, evaluation_tool, vad_engine
    """
    if customer_name or admin_token:
        final_prompt = generate_dynamic_prompt(
            customer_name=customer_name or "",
            base_prompt=prompt
        )
    else:
        final_prompt = prompt or DEFAULT_PROMPT
    
    payload = {
        "prompt": final_prompt,
        "evaluation_tool": evaluation_tool or DEFAULT_EVALUATION_TOOL,
        "vad_engine": vad_engine or DEFAULT_VAD_ENGINE
    }
    
    return payload

