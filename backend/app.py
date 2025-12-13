from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List
import csv_utils
import dinodial_client
import uvicorn
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    csv_utils.init_csv()
    yield
    # Shutdown (if needed)
    
app = FastAPI(
    title="Restaurant Voice Agent API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Models
# --------------------------------------------------

class CustomerCreate(BaseModel):
    name: str
    mobile: str


class CustomerResponse(BaseModel):
    customer_id: str
    name: str
    mobile: str


class TriggerCallRequest(BaseModel):
    flow: str  # order_booking | arrival_check | missed_followup


class WebhookData(BaseModel):
    customer_id: str
    flow: str
    result: dict

# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.post("/customer", response_model=dict)
async def create_customer(customer: CustomerCreate):
    try:
        customer_id = csv_utils.add_customer(
            name=customer.name,
            mobile=customer.mobile
        )
        return {
            "success": True,
            "customer_id": customer_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/customers", response_model=List[CustomerResponse])
async def get_customers():
    customers = csv_utils.get_all_customers()
    return [
        CustomerResponse(
            customer_id=c["customer_id"],
            name=c["name"],
            mobile=c["mobile"]
        )
        for c in customers
    ]


@app.get("/customer/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    customer = csv_utils.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return CustomerResponse(**customer)


@app.post("/trigger-call/{customer_id}", response_model=dict)
async def trigger_call(customer_id: str, payload: TriggerCallRequest):
    customer = csv_utils.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    call_context = {
        "customer_id": customer["customer_id"],
        "name": customer["name"],
        "mobile": customer["mobile"],
        "flow": payload.flow
    }

    result = dinodial_client.trigger_call(call_context)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Call failed"))

    return result


@app.post("/webhook/call-result", response_model=dict)
async def handle_call_webhook(webhook: WebhookData):
    """
    Dinodial.ai sends call outcome here.
    No CSV mutation needed.
    """
    return dinodial_client.handle_call_webhook(webhook.dict())


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# --------------------------------------------------
# Run
# --------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
