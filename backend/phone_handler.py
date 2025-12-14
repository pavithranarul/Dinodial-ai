"""
Phone call handler for Dinodial Proxy API.
Contains all functions related to making and managing phone calls.
"""
import httpx
import config
import model_config
import asyncio
import smtplib
import json
import re
from google import genai
from typing import Dict, Optional
from email.mime.text import MIMEText

client = genai.Client(api_key=config.GOOGLE_API_KEY)
model = "gemini-2.5-flash"

import json
import asyncio
import re
from typing import Dict, Optional


async def _extract_reservation_details_via_llm(
    call_data: Dict
) -> Optional[Dict]:
    """
    LAST-RESORT extraction using Gemini (sync SDK wrapped for async).
    Returns reservation_details dict or None.
    """

    prompt = f"""
You are a strict JSON extractor.

Rules:
- Use ONLY the provided JSON
- Do NOT guess or invent values
- If reservation details are not present, return null
- Output MUST be valid JSON only
- No explanations

Expected JSON format:
{{
  "date": string,
  "time": string,
  "number_of_people": string,
  "status": string
}}

CALL DATA:
{json.dumps(call_data, indent=2)}
"""

    loop = asyncio.get_running_loop()

    try:
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=model,
                contents=prompt
            )
        )

        raw = response.text.strip()
        print("🧠 LLM RAW OUTPUT:", raw)

        if not raw:
            return None

        # ✅ STRIP MARKDOWN CODE FENCES
        cleaned = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.IGNORECASE).strip()

        if cleaned.lower() == "null":
            return None

        data = json.loads(cleaned)

        # ✅ Defensive validation
        if not isinstance(data, dict):
            return None

        required_keys = {"date", "time", "number_of_people", "status"}
        if not required_keys.issubset(data.keys()):
            return None

        return data

    except Exception as e:
        print("❌ LLM extraction failed:", e)
        return None



async def make_call(
    prompt: Optional[str] = None,
    evaluation_tool: Optional[Dict] = None,
    vad_engine: Optional[str] = None,
    customer_name: Optional[str] = None,
    admin_token: Optional[str] = None
) -> Dict:
    """
    Initiate a call for AI voice bot using POST method.
    
    Args:
        prompt: Custom prompt string. If None, uses default from model_config
        evaluation_tool: Custom evaluation tool config. If None, uses default from model_config
        vad_engine: VAD engine name. If None, uses default from model_config
        customer_name: Customer name for dynamic prompt generation
        admin_token: Admin token from CSV. If provided, used as bearer token instead of env var
        
    Returns:
        Dict with success status and call details
    """
    bearer_token = None
    
    if admin_token:
        bearer_token = admin_token
    if not bearer_token:
        bearer_token = config.DINODIAL_PROXY_BEARER_TOKEN
    
    if not bearer_token:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{config.DINODIAL_PROXY_BASE}/make-call/"
    
    payload = model_config.get_make_call_payload(
        prompt=prompt,
        evaluation_tool=evaluation_tool,
        vad_engine=vad_engine,
        customer_name=customer_name,
        admin_token=admin_token
    )
    headers = {
        "Authorization": f"Bearer {bearer_token}",
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


async def get_calls_list(params: Optional[Dict] = None, admin_token: Optional[str] = None) -> Dict:
    """
    Get list of calls.
    
    Args:
        params: Optional query parameters (e.g., page, limit)
        
    Returns:
        Dict with success status and list of calls
    """
    bearer_token = None
    
    if admin_token:
        bearer_token = admin_token
    if not bearer_token:
        bearer_token = config.DINODIAL_PROXY_BEARER_TOKEN
    
    if not bearer_token:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{config.DINODIAL_PROXY_BASE}/calls/list/"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
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


async def get_call_detail(call_id: int, admin_token: Optional[str] = None) -> Dict:
    """
    Get details of a specific call.
    
    Args:
        call_id: The ID of the call
        
    Returns:
        Dict with success status and call details
    """
    bearer_token = None
    
    if admin_token:
        bearer_token = admin_token
    if not bearer_token:
        bearer_token = config.DINODIAL_PROXY_BEARER_TOKEN
    
    if not bearer_token:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{config.DINODIAL_PROXY_BASE}/call/detail/{call_id}/"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
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


async def get_recording_url(call_id: int, admin_token: Optional[str] = None) -> Dict:
    """
    Get recording URL for a specific call.
    
    Args:
        call_id: The ID of the call
        
    Returns:
        Dict with success status and recording URL
    """
    bearer_token = None
    
    if admin_token:
        bearer_token = admin_token
    if not bearer_token:
        bearer_token = config.DINODIAL_PROXY_BEARER_TOKEN
    if not bearer_token:
        return {"success": False, "error": "Bearer token not configured"}
    
    url = f"{config.DINODIAL_PROXY_BASE}/recording-url/{call_id}/"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
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



async def _send_email(email: str, subject: str, message_text: str) -> dict:
    if not email:
        return {"success": False, "message": "Email address is required"}

    print("🚀 _send_email CALLED")
    print("email:", email)

    def send():
        msg = MIMEText(message_text)
        msg["Subject"] = subject
        msg["From"] = "pavithranarul7@gmail.com"
        msg["To"] = email

        smtp_server = "smtp.gmail.com"
        smtp_port = 465
        smtp_user = "pavithranarul7@gmail.com"
        smtp_password = "flmj pxnk fkkq sqdx"  # app password

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())

    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, send)
        print(f"✅ Email sent successfully to {email}")
        return {"success": True, "message": "Email sent", "email": email}
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return {"success": False, "error": str(e), "email": email}

def _extract_reservation_details_via_regex(call_data: Dict) -> Optional[Dict]:
    """
    Primary extractor.
    Extracts reservation_details JSON object from the raw call payload
    using regex and parses it safely.
    """
    try:
        raw_text = json.dumps(call_data)

        pattern = (
            r'"reservation_details"\s*:\s*(\{.*?\})'
        )

        match = re.search(pattern, raw_text, re.DOTALL)
        if not match:
            return None

        reservation_json = match.group(1)
        return json.loads(reservation_json)

    except Exception:
        return None

def _extract_reservation_details_via_json(call_data: Dict) -> Optional[Dict]:
    """
    Fallback extractor.
    Uses structured JSON paths when evaluation exists.
    """
    return (
        call_data
        .get("data", {})
        .get("data", {})
        .get("call_details", {})
        .get("callOutcomesData", {})
        .get("reservation_details")
    )

async def send_reservation_email(
    email: str,
    customer_name: str,
    call_data: Dict
) -> Dict:
    print("🚀 ENTERED send_reservation_email")

    if not call_data:
        return {"success": False, "message": "Missing call data"}

    # ============================
    # 1️⃣ PRIMARY: REGEX EXTRACTION
    # ============================
    reservation = _extract_reservation_details_via_regex(call_data)
    print("🔍 reservation (regex):", reservation)

    # ============================
    # 2️⃣ FALLBACK: JSON EXTRACTION
    # ============================
    if not reservation:
        reservation = await _extract_reservation_details_via_llm(call_data)
        print("🔁 reservation (json fallback):", reservation)

    if not reservation:
        return {
            "success": False,
            "message": "Reservation details not found (regex + json failed)"
        }

    # ============================
    # 3️⃣ VALIDATION
    # ============================
    if reservation.get("status") != "confirmed":
        return {"success": False, "message": "Reservation not confirmed"}

    date = reservation.get("date")
    time_ = reservation.get("time")
    number_of_people = reservation.get("number_of_people")

    if not all([date, time_, number_of_people]):
        return {"success": False, "message": "Incomplete reservation details"}

    if not email:
        return {"success": False, "message": "Missing customer email"}

    if not customer_name:
        customer_name = "Valued Customer"

    # ============================
    # 4️⃣ SEND EMAIL
    # ============================
    subject = f"Reservation Confirmation - {config.RESTAURANT_NAME}"
    message = (
        f"Hi {customer_name},\n\n"
        f"Your table reservation at {config.RESTAURANT_NAME} is confirmed:\n\n"
        f"Date: {date}\n"
        f"Time: {time_}\n"
        f"Number of guests: {number_of_people}\n\n"
        f"We look forward to serving you!\n\n"
        f"Best regards,\n"
        f"{config.RESTAURANT_NAME} Team"
    )

    return await _send_email(email, subject, message)