from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import csv_utils
import dinodial_client
import scheduler
import uvicorn
from datetime import datetime

app = FastAPI(title="Restaurant Voice Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CustomerCreate(BaseModel):
    name: str
    mobile: str
    expected_arrival_time: Optional[str] = None

class CustomerResponse(BaseModel):
    customer_id: str
    name: str
    mobile: str
    status: str
    order_details: str
    expected_arrival_time: str
    arrival_confirmed: bool
    last_call_time: str
    remarks: str

class WebhookData(BaseModel):
    customer_id: str
    call_flow: str
    result: dict

@app.on_event("startup")
async def startup_event():
    csv_utils.init_csv()
    scheduler.start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.stop_scheduler()

@app.post("/customer", response_model=dict)
async def create_customer(customer: CustomerCreate):
    try:
        customer_data = {
            "name": customer.name,
            "mobile": customer.mobile,
            "expected_arrival_time": customer.expected_arrival_time or ""
        }
        customer_id = csv_utils.add_customer(customer_data)
        return {
            "success": True,
            "customer_id": customer_id,
            "message": "Customer created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customers", response_model=List[CustomerResponse])
async def get_customers():
    try:
        customers = csv_utils.read_customers()
        result = []
        for customer in customers:
            result.append(CustomerResponse(
                customer_id=customer.get("customer_id", ""),
                name=customer.get("name", ""),
                mobile=customer.get("mobile", ""),
                status=customer.get("status", ""),
                order_details=customer.get("order_details", ""),
                expected_arrival_time=customer.get("expected_arrival_time", ""),
                arrival_confirmed=customer.get("arrival_confirmed", "false").lower() == "true",
                last_call_time=customer.get("last_call_time", ""),
                remarks=customer.get("remarks", "")
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customer/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    customer = csv_utils.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return CustomerResponse(
        customer_id=customer.get("customer_id", ""),
        name=customer.get("name", ""),
        mobile=customer.get("mobile", ""),
        status=customer.get("status", ""),
        order_details=customer.get("order_details", ""),
        expected_arrival_time=customer.get("expected_arrival_time", ""),
        arrival_confirmed=customer.get("arrival_confirmed", "false").lower() == "true",
        last_call_time=customer.get("last_call_time", ""),
        remarks=customer.get("remarks", "")
    )

@app.post("/trigger-call/{customer_id}", response_model=dict)
async def trigger_call(customer_id: str):
    customer = csv_utils.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    status = customer.get("status", "")
    
    if status == "new":
        result = dinodial_client.trigger_order_booking_call(customer_id)
    elif status in ["order_confirmed", "called"]:
        result = dinodial_client.trigger_arrival_confirmation_call(customer_id)
    elif status == "no_show":
        result = dinodial_client.trigger_missed_customer_recovery_call(customer_id)
    else:
        result = {"success": False, "error": f"Cannot trigger call for status: {status}"}
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to trigger call"))
    
    return result

@app.post("/webhook/call-result", response_model=dict)
async def handle_call_webhook(webhook: WebhookData):
    try:
        result = dinodial_client.handle_call_webhook(webhook.dict())
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

