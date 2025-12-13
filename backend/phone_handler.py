"""
Phone call handler for Dinodial Proxy API.
Contains all functions related to making and managing phone calls.
"""
import httpx
import smtplib
import os
from typing import Dict, Optional
from email.mime.text import MIMEText
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


async def _send_email(email: str, subject: str, message_text: str) -> Dict:
    """
    Common function to send email via SMTP.
    
    Args:
        email: Recipient email address
        subject: Email subject
        message_text: Email body text
        
    Returns:
        Dict with success status and message
    """
    if not email:
        return {"success": False, "message": "Email address is required"}
    
    # Debug: Print email content before sending
    print("=" * 60)
    print("📧 EMAIL DEBUG INFO")
    print("=" * 60)
    print(f"To: {email}")
    print(f"From: pavithranarul7@gmail.com")
    print(f"Subject: {subject}")
    print("-" * 60)
    print("Message Content:")
    print(message_text)
    print("=" * 60)
    
    msg = MIMEText(message_text)
    msg['Subject'] = subject
    msg['From'] = "pavithranarul7@gmail.com"
    msg['To'] = email
    
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 465
        smtp_user = "pavithranarul7@gmail.com"
        smtp_password = "flmj pxnk fkkq sqdx"
        
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        server.quit()
        print(f"✅ Email sent successfully to {email}")
        return {"success": True, "message": "Email sent", "email": email}
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")
        return {"success": False, "error": str(e), "email": email}


async def send_reservation_email(email: str, customer_name: str, date: str, time: str, number_of_people: str, call_data: Optional[Dict] = None) -> Dict:
    """
    Single optimized function to send reservation/order emails based on call status.
    - If status is "in_progress": sends "wait for order" email
    - If status is "completed": sends reservation confirmation email with details
    
    Args:
        email: Customer email address (required)
        customer_name: Customer name (optional, defaults to "Valued Customer")
        date: Reservation date (optional)
        time: Reservation time (optional)
        number_of_people: Number of people (optional)
        call_data: Call detail data to extract info from
        
    Returns:
        Dict with success status and message
    """
    import csv_utils
    
    # If call_data provided, extract information from it
    if call_data:
        try:
            call_status = call_data.get("status", "")
            phone_number = call_data.get("phone_number", "")
            
            # Get customer email from database if not provided
            if not email and phone_number:
                try:
                    customer = await csv_utils.get_customer_by_mobile(phone_number)
                    if customer and customer.get("email"):
                        email = customer.get("email")
                        if not customer_name:
                            customer_name = customer.get("name", customer_name)
                except Exception as e:
                    print(f"⚠️ Could not fetch customer by mobile: {e}")
            
            # Handle in_progress status - send wait email
            if call_status == "in_progress":
                if not customer_name:
                    customer_name = "Valued Customer"
                
                message_text = f"Hi {customer_name},\n\nThank you for your call. We are currently processing your order/reservation. Please wait while we confirm the details.\n\nWe will send you a confirmation email shortly.\n\nBest regards,\n{config.RESTAURANT_NAME} Team"
                subject = f"Processing Your Request - {config.RESTAURANT_NAME}"
                result = await _send_email(email, subject, message_text)
                if result.get("success"):
                    result["message"] = "Wait email sent"
                return result
            
            # Handle completed status - send reservation confirmation
            elif call_status == "completed":
                call_details = call_data.get("call_details", {})
                call_outcomes = call_details.get("callOutcomesData", {})
                
                # Check if outcome is reservation_confirmed
                if call_outcomes.get("outcome") != "reservation_confirmed":
                    return {"success": False, "message": "No reservation confirmed in this call"}
                
                reservation_details = call_outcomes.get("reservation_details", {})
                if not reservation_details or reservation_details.get("status") != "confirmed":
                    return {"success": False, "message": "Reservation not confirmed"}
                
                # Extract reservation details
                date = reservation_details.get("date") or date
                time = reservation_details.get("time") or time
                number_of_people = reservation_details.get("number_of_people") or number_of_people
                customer_name = reservation_details.get("customer_name") or customer_name
                
                # Try to get email from reservation_details first
                email = reservation_details.get("email") or email
                
                # If no email in reservation, try to get from customer database
                if not email and phone_number:
                    try:
                        customer = await csv_utils.get_customer_by_mobile(phone_number)
                        if customer and customer.get("email"):
                            email = customer.get("email")
                            if not customer_name:
                                customer_name = customer.get("name", customer_name)
                    except Exception as e:
                        print(f"⚠️ Could not fetch customer by mobile: {e}")
                
                # Validate required fields
                if not date or not time or not number_of_people:
                    return {"success": False, "message": "Reservation details incomplete"}
                
                # Default customer name if not provided
                if not customer_name:
                    customer_name = "Valued Customer"
                
                # Prepare confirmation email
                message_text = f"Hi {customer_name},\n\nYour table reservation at {config.RESTAURANT_NAME} is confirmed:\n\nDate: {date}\nTime: {time}\nNumber of guests: {number_of_people}\n\nWe look forward to serving you!\n\nBest regards,\n{config.RESTAURANT_NAME} Team"
                subject = f"Reservation Confirmation - {config.RESTAURANT_NAME}"
                result = await _send_email(email, subject, message_text)
                if result.get("success"):
                    result["message"] = "Reservation confirmation sent"
                return result
            else:
                return {"success": False, "message": f"Call status '{call_status}' not handled"}
            
        except Exception as e:
            return {"success": False, "error": f"Error extracting call data: {str(e)}"}
    
    # If no call_data, use provided parameters (for direct calls)
    if not date or not time or not number_of_people:
        return {"success": False, "message": "Reservation details incomplete"}
    
    if not customer_name:
        customer_name = "Valued Customer"
    
    message_text = f"Hi {customer_name},\n\nYour table reservation at {config.RESTAURANT_NAME} is confirmed:\n\nDate: {date}\nTime: {time}\nNumber of guests: {number_of_people}\n\nWe look forward to serving you!\n\nBest regards,\n{config.RESTAURANT_NAME} Team"
    subject = f"Reservation Confirmation - {config.RESTAURANT_NAME}"
    result = await _send_email(email, subject, message_text)
    if result.get("success"):
        result["message"] = "Reservation confirmation sent"
    return result

