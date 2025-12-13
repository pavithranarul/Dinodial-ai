from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
import csv_utils
import scheduler
import client_handler
import phone_handler
import uvicorn
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await csv_utils.init_csv()
    await scheduler.start_scheduler()
    yield
    # Shutdown
    await scheduler.stop_scheduler()
    
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
        customer_id = await csv_utils.add_customer(
            name=customer.name,
            mobile=customer.mobile
        )
        return {"success": True, "customer_id": customer_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/customers", response_model=List[CustomerResponse])
async def get_customers():
    customers = await csv_utils.get_all_customers()
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
    customer = await csv_utils.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return CustomerResponse(**customer)


@app.post("/trigger-call/{customer_id}", response_model=dict)
async def trigger_call(customer_id: str, payload: TriggerCallRequest):
    customer = await csv_utils.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    call_context = {
        "customer_id": customer["customer_id"],
        "name": customer["name"],
        "mobile": customer["mobile"],
        "flow": payload.flow
    }

    result = await client_handler.trigger_call(
        customer_id,
        payload.flow,
        call_context
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Call failed"))

    return result


@app.post("/webhook/call-result", response_model=dict)
async def handle_call_webhook(webhook: WebhookData):
    """
    Dinodial.ai sends call outcome here.
    """
    return await client_handler.handle_call_webhook(webhook.dict())


# --------------------------------------------------
# Phone Call Handler Endpoints
# --------------------------------------------------

class MakeCallRequest(BaseModel):
    prompt: Optional[str] = None
    evaluation_tool: Optional[dict] = None
    vad_engine: Optional[str] = None


@app.post("/api/phone-calls/make-call", response_model=dict)
async def api_make_call(request: MakeCallRequest):
    """
    Main endpoint to initiate/connect a call for AI voice bot using POST method.
    Uses the payload structure from model_config.py with prompt, evaluation_tool, and vad_engine.
    """
    result = await phone_handler.make_call(
        prompt=request.prompt,
        evaluation_tool=request.evaluation_tool,
        vad_engine=request.vad_engine
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Call initiation failed")
        )
    
    return result


@app.get("/api/phone-calls/list", response_model=dict)
async def api_get_calls_list(
    page: Optional[int] = Query(None, description="Page number"),
    limit: Optional[int] = Query(None, description="Items per page")
):
    """
    Get list of calls.
    """
    params = {}
    if page is not None:
        params["page"] = page
    if limit is not None:
        params["limit"] = limit
    
    result = await phone_handler.get_calls_list(params if params else None)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to fetch calls list")
        )
    
    return result


@app.get("/api/phone-calls/{call_id}/detail", response_model=dict)
async def api_get_call_detail(call_id: int):
    """
    Get details of a specific call.
    """
    result = await phone_handler.get_call_detail(call_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get("error", "Call not found")
        )
    
    return result


@app.get("/api/phone-calls/{call_id}/recording-url", response_model=dict)
async def api_get_recording_url(call_id: int):
    """
    Get recording URL for a specific call.
    """
    result = await phone_handler.get_recording_url(call_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Recording URL not found")
        )
    
    return result


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
