import requests
from typing import Dict, Optional
from datetime import datetime
import csv_utils

DINODIAL_API_BASE = "https://api.dinodial.ai"
DINODIAL_API_KEY = ""  
RESTAURANT_NAME = "Dino Restaurant"

def trigger_call(customer_id: str, call_flow: str, context: Dict[str, str]) -> Dict:
    customer = csv_utils.get_customer_by_id(customer_id)
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
            "restaurant_name": RESTAURANT_NAME,
            **context
        }
    }
    
    csv_utils.update_customer(customer_id, {
        "last_call_time": datetime.now().isoformat()
    })
    
    try:
        response = requests.post(
            f"{DINODIAL_API_BASE}/v1/calls",
            json=call_data,
            headers={
                "Authorization": f"Bearer {DINODIAL_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return {"success": True, "call_id": response.json().get("call_id")}
        else:
            return {"success": False, "error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def trigger_order_booking_call(customer_id: str) -> Dict:
    customer = csv_utils.get_customer_by_id(customer_id)
    if not customer or customer.get("status") != "new":
        return {"success": False, "error": "Invalid customer status for order booking"}
    
    script = (
        f"Hello {customer.get('name', 'there')}, this is calling from {RESTAURANT_NAME}. "
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
    
    result = trigger_call(customer_id, "order_booking", context)
    
    if result.get("success"):
        csv_utils.update_customer(customer_id, {"status": "called"})
    
    return result

def trigger_arrival_confirmation_call(customer_id: str) -> Dict:
    customer = csv_utils.get_customer_by_id(customer_id)
    if not customer:
        return {"success": False, "error": "Customer not found"}
    
    script = (
        f"Hi {customer.get('name', 'there')}, this is {RESTAURANT_NAME}. "
        f"Just checking if you've reached the restaurant or are on the way?"
    )
    
    context = {
        "script": script,
        "flow_type": "arrival_confirmation",
        "capture_fields": ["arrival_status"]
    }
    
    return trigger_call(customer_id, "arrival_confirmation", context)

def trigger_missed_customer_recovery_call(customer_id: str) -> Dict:
    customer = csv_utils.get_customer_by_id(customer_id)
    if not customer or customer.get("status") != "no_show":
        return {"success": False, "error": "Invalid customer status for recovery call"}
    
    script = (
        f"Hi {customer.get('name', 'there')}, this is {RESTAURANT_NAME}. "
        f"We noticed you couldn't make it earlier, no worries at all. "
        f"Would you like to reschedule your visit, place a takeaway order, or cancel for today?"
    )
    
    context = {
        "script": script,
        "flow_type": "missed_customer_recovery",
        "capture_fields": ["action", "new_arrival_time", "takeaway_order"]
    }
    
    return trigger_call(customer_id, "missed_customer_recovery", context)

def handle_call_webhook(webhook_data: Dict) -> Dict:
    customer_id = webhook_data.get("customer_id")
    call_flow = webhook_data.get("call_flow")
    call_result = webhook_data.get("result", {})
    
    if not customer_id:
        return {"success": False, "error": "Missing customer_id"}
    
    customer = csv_utils.get_customer_by_id(customer_id)
    if not customer:
        return {"success": False, "error": "Customer not found"}
    
    if call_flow == "order_booking":
        updates = {"status": "order_confirmed"}
        if "order_details" in call_result:
            updates["order_details"] = call_result["order_details"]
        if "expected_arrival_time" in call_result:
            updates["expected_arrival_time"] = call_result["expected_arrival_time"]
        csv_utils.update_customer(customer_id, updates)
    
    elif call_flow == "arrival_confirmation":
        arrival_status = call_result.get("arrival_status", "").lower()
        if arrival_status == "arrived":
            csv_utils.update_customer(customer_id, {
                "arrival_confirmed": "true",
                "status": "arrived"
            })
        elif arrival_status == "on the way":
            pass
        elif arrival_status in ["not coming", "cancel"]:
            csv_utils.update_customer(customer_id, {"status": "no_show"})
    
    elif call_flow == "missed_customer_recovery":
        action = call_result.get("action", "").lower()
        if action == "reschedule":
            updates = {"status": "order_confirmed"}
            if "new_arrival_time" in call_result:
                updates["expected_arrival_time"] = call_result["new_arrival_time"]
            csv_utils.update_customer(customer_id, updates)
        elif action == "takeaway":
            updates = {"status": "resolved"}
            if "takeaway_order" in call_result:
                updates["order_details"] = call_result["takeaway_order"]
            csv_utils.update_customer(customer_id, updates)
        elif action == "cancel":
            csv_utils.update_customer(customer_id, {"status": "resolved"})
    
    return {"success": True}

