"""
Phone call handler for Dinodial Proxy API.
Contains all functions related to making and managing phone calls.
"""
import httpx
from typing import Dict, Optional
import config
import model_config


async def make_call(
    prompt: Optional[str] = None,
    evaluation_tool: Optional[Dict] = None,
    vad_engine: Optional[str] = None
) -> Dict:
    """
    Initiate a call for AI voice bot using POST method.
    
    Args:
        prompt: Custom prompt string. If None, uses default from model_config
        evaluation_tool: Custom evaluation tool config. If None, uses default from model_config
        vad_engine: VAD engine name. If None, uses default from model_config
        
    Returns:
        Dict with success status and call details
    """
    if not config.DINODIAL_PROXY_BEARER_TOKEN:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{config.DINODIAL_PROXY_BASE}/make-call/"
    
    payload = model_config.get_make_call_payload(
        prompt=prompt,
        evaluation_tool=evaluation_tool,
        vad_engine=vad_engine
    )
    print(payload)
    headers = {
        "Authorization": f"Bearer {config.DINODIAL_PROXY_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return {"success": True, "data": data.get("data", {}), "status_code": data.get("status_code")}
            else:
                return {"success": False, "error": data.get("message", "Call initiation failed")}
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_calls_list(params: Optional[Dict] = None) -> Dict:
    """
    Get list of calls.
    
    Args:
        params: Optional query parameters (e.g., page, limit)
        
    Returns:
        Dict with success status and list of calls
    """
    if not config.DINODIAL_PROXY_BEARER_TOKEN:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{config.DINODIAL_PROXY_BASE}/calls/list/"
    
    headers = {
        "Authorization": f"Bearer {config.DINODIAL_PROXY_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params or {})
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return {"success": True, "data": data.get("data", {}), "status_code": data.get("status_code")}
            else:
                return {"success": False, "error": data.get("message", "Failed to fetch calls list")}
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_call_detail(call_id: int) -> Dict:
    """
    Get details of a specific call.
    
    Args:
        call_id: The ID of the call
        
    Returns:
        Dict with success status and call details
    """
    if not config.DINODIAL_PROXY_BEARER_TOKEN:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{config.DINODIAL_PROXY_BASE}/call/detail/{call_id}/"
    
    headers = {
        "Authorization": f"Bearer {config.DINODIAL_PROXY_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return {"success": True, "data": data.get("data", {}), "status_code": data.get("status_code")}
            else:
                return {"success": False, "error": data.get("message", "Call not found")}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": "Call not found"}
        return {"success": False, "error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_recording_url(call_id: int) -> Dict:
    """
    Get recording URL for a specific call.
    
    Args:
        call_id: The ID of the call
        
    Returns:
        Dict with success status and recording URL
    """
    if not config.DINODIAL_PROXY_BEARER_TOKEN:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{config.DINODIAL_PROXY_BASE}/recording-url/{call_id}/"
    
    headers = {
        "Authorization": f"Bearer {config.DINODIAL_PROXY_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return {"success": True, "data": data.get("data", {}), "status_code": data.get("status_code")}
            else:
                return {"success": False, "error": data.get("message", "Recording URL not found")}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return {"success": False, "error": "Recording URL not found"}
        return {"success": False, "error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

