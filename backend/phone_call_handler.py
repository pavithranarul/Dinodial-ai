import httpx
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv

load_dotenv()

DINODIAL_PROXY_BASE = "https://api-dinodial-proxy.cyces.co/api/proxy"
DINODIAL_PROXY_BEARER_TOKEN = os.getenv("DINODIAL_PROXY_BEARER_TOKEN", "")


async def make_call(phone_number: str, context: Optional[Dict] = None) -> Dict:
    """
    Initiate a call for AI voice bot.
    
    Args:
        phone_number: The phone number to call
        context: Optional context data for the call
        
    Returns:
        Dict with success status and call details
    """
    if not DINODIAL_PROXY_BEARER_TOKEN:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{DINODIAL_PROXY_BASE}/make-call/"
    
    payload = {
        "phone_number": phone_number
    }
    
    if context:
        payload.update(context)
    
    headers = {
        "Authorization": f"Bearer {DINODIAL_PROXY_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "status_code": data.get("status_code")
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Unknown error"),
                    "data": data
                }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP error: {e.response.status_code}",
            "details": e.response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_calls_list(params: Optional[Dict] = None) -> Dict:
    """
    Get list of calls.
    
    Args:
        params: Optional query parameters (e.g., page, limit)
        
    Returns:
        Dict with success status and list of calls
    """
    if not DINODIAL_PROXY_BEARER_TOKEN:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{DINODIAL_PROXY_BASE}/calls/list/"
    
    headers = {
        "Authorization": f"Bearer {DINODIAL_PROXY_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params or {})
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "status_code": data.get("status_code")
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Unknown error"),
                    "data": data
                }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP error: {e.response.status_code}",
            "details": e.response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_call_detail(call_id: int) -> Dict:
    """
    Get details of a specific call.
    
    Args:
        call_id: The ID of the call
        
    Returns:
        Dict with success status and call details
    """
    if not DINODIAL_PROXY_BEARER_TOKEN:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{DINODIAL_PROXY_BASE}/call/detail/{call_id}/"
    
    headers = {
        "Authorization": f"Bearer {DINODIAL_PROXY_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "status_code": data.get("status_code")
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Unknown error"),
                    "data": data
                }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP error: {e.response.status_code}",
            "details": e.response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_recording_url(call_id: int) -> Dict:
    """
    Get recording URL for a specific call.
    
    Args:
        call_id: The ID of the call
        
    Returns:
        Dict with success status and recording URL
    """
    if not DINODIAL_PROXY_BEARER_TOKEN:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{DINODIAL_PROXY_BASE}/recording-url/{call_id}/"
    
    headers = {
        "Authorization": f"Bearer {DINODIAL_PROXY_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "status_code": data.get("status_code")
                }
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Unknown error"),
                    "data": data
                }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP error: {e.response.status_code}",
            "details": e.response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

