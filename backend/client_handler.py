"""
Client handler for restaurant/customer management.
Contains post-call functions, CSV related functionalities, and frontend related functionalities.
"""
import httpx
from typing import Dict
from datetime import datetime
import csv_utils
import config


async def trigger_call(customer_id: str, call_flow: str, context: Dict[str, str]) -> Dict:
    """
    Trigger a call for a customer using the Dinodial API.
    
    Args:
        customer_id: The customer ID
        call_flow: The type of call flow (order_booking, arrival_confirmation, etc.)
        context: Additional context data
        
    Returns:
        Dict with success status and call details
    """
    customer = await csv_utils.get_customer_by_id(customer_id)
    if not customer:
        return {"success": False, "error": "Customer not found"}
    
    phone_number = customer.get("mobile", "")
    if not phone_number:
        return {"success": False, "error": "Mobile number not found"}
    
    call_data = {
        "phone_number": phone_number,
        "customer_id": customer_id,
        "call_flow": call_flow,
        "context": {
            "name": customer.get("name", ""),
            "restaurant_name": config.RESTAURANT_NAME,
            **context
        }
    }
    
    await csv_utils.update_customer(customer_id, {
        "last_call_time": datetime.now().isoformat()
    })
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{config.DINODIAL_PROXY_BASE}/make-call/",
                json=call_data,
                headers={
                    "Authorization": f"Bearer {config.DINODIAL_PROXY_BEARER_TOKEN}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return {"success": True, "call_id": response.json().get("call_id")}
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def trigger_order_booking_call(customer_id: str) -> Dict:
    """
    Trigger an order booking call for a customer.
    
    Args:
        customer_id: The customer ID
        
    Returns:
        Dict with success status and call details
    """
    customer = await csv_utils.get_customer_by_id(customer_id)
    if not customer or customer.get("status") != "new":
        return {"success": False, "error": "Invalid customer status for order booking"}
    
    phone_number = customer.get("mobile", "")
    if not phone_number:
        return {"success": False, "error": "Mobile number not found"}
    
    script = (
        f"Hello {customer.get('name', 'there')}, this is calling from {config.RESTAURANT_NAME}. "
        f"We noticed your interest in dining with us today. "
        f"I just want to confirm your order and any special requirements. "
        f"Are you planning to dine in or take away? "
        f"Do you have any special food preferences? "
        f"What time will you be arriving?"
    )
    
    context = {
        "script": script,
        "flow_type": "order_booking",
        "capture_fields": ["order_details", "expected_arrival_time"]
    }
    
    result = await trigger_call(customer_id, "order_booking", context)
    
    if result.get("success"):
        await csv_utils.update_customer(customer_id, {"status": "called"})
    
    return result


async def trigger_arrival_confirmation_call(customer_id: str) -> Dict:
    """
    Trigger an arrival confirmation call for a customer.
    
    Args:
        customer_id: The customer ID
        
    Returns:
        Dict with success status and call details
    """
    customer = await csv_utils.get_customer_by_id(customer_id)
    if not customer:
        return {"success": False, "error": "Customer not found"}
    
    phone_number = customer.get("mobile", "")
    if not phone_number:
        return {"success": False, "error": "Mobile number not found"}
    
    script = (
        f"Hi {customer.get('name', 'there')}, this is {config.RESTAURANT_NAME}. "
        f"Just checking if you've reached the restaurant or are on the way?"
    )
    
    context = {
        "script": script,
        "flow_type": "arrival_confirmation",
        "capture_fields": ["arrival_status"]
    }
    
    return await trigger_call(customer_id, "arrival_confirmation", context)


async def trigger_missed_customer_recovery_call(customer_id: str) -> Dict:
    """
    Trigger a missed customer recovery call.
    
    Args:
        customer_id: The customer ID
        
    Returns:
        Dict with success status and call details
    """
    customer = await csv_utils.get_customer_by_id(customer_id)
    if not customer or customer.get("status") != "no_show":
        return {"success": False, "error": "Invalid customer status for recovery call"}
    
    phone_number = customer.get("mobile", "")
    if not phone_number:
        return {"success": False, "error": "Mobile number not found"}
    
    script = (
        f"Hi {customer.get('name', 'there')}, this is {config.RESTAURANT_NAME}. "
        f"We noticed you couldn't make it earlier, no worries at all. "
        f"Would you like to reschedule your visit, place a takeaway order, or cancel for today?"
    )
    
    context = {
        "script": script,
        "flow_type": "missed_customer_recovery",
        "capture_fields": ["action", "new_arrival_time", "takeaway_order"]
    }
    
    return await trigger_call(customer_id, "missed_customer_recovery", context)


async def handle_call_webhook(webhook_data: Dict) -> Dict:
    """
    Handle webhook data from Dinodial.ai after a call completes.
    Updates customer data in CSV based on call results.
    
    Args:
        webhook_data: Dictionary containing customer_id, flow, and result
        
    Returns:
        Dict with success status
    """
    customer_id = webhook_data.get("customer_id")
    call_flow = webhook_data.get("flow")
    call_result = webhook_data.get("result", {})
    
    if not customer_id:
        return {"success": False, "error": "Missing customer_id"}
    
    customer = await csv_utils.get_customer_by_id(customer_id)
    if not customer:
        return {"success": False, "error": "Customer not found"}
    
    if call_flow == "order_booking":
        updates = {"status": "order_confirmed"}
        if "order_details" in call_result:
            updates["order_details"] = call_result["order_details"]
        if "expected_arrival_time" in call_result:
            updates["expected_arrival_time"] = call_result["expected_arrival_time"]
        await csv_utils.update_customer(customer_id, updates)
    
    elif call_flow == "arrival_confirmation":
        arrival_status = call_result.get("arrival_status", "").lower()
        if arrival_status == "arrived":
            await csv_utils.update_customer(customer_id, {
                "arrival_confirmed": "true",
                "status": "arrived"
            })
        elif arrival_status == "on the way":
            pass
        elif arrival_status in ["not coming", "cancel"]:
            await csv_utils.update_customer(customer_id, {"status": "no_show"})
    
    elif call_flow == "missed_customer_recovery":
        action = call_result.get("action", "").lower()
        if action == "reschedule":
            updates = {"status": "order_confirmed"}
            if "new_arrival_time" in call_result:
                updates["expected_arrival_time"] = call_result["new_arrival_time"]
            await csv_utils.update_customer(customer_id, updates)
        elif action == "takeaway":
            updates = {"status": "resolved"}
            if "takeaway_order" in call_result:
                updates["order_details"] = call_result["takeaway_order"]
            await csv_utils.update_customer(customer_id, updates)
        elif action == "cancel":
            await csv_utils.update_customer(customer_id, {"status": "resolved"})
    
    return {"success": True}

