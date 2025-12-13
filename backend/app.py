from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
import csv_utils
import scheduler
import phone_handler
import uvicorn
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await csv_utils.init_csv()
    except Exception as e:
        print(f"⚠️ CSV init warning: {e}")
    try:
        await scheduler.start_scheduler()
    except Exception as e:
        print(f"⚠️ Scheduler warning: {e}")
    yield
    # Shutdown
    try:
        await scheduler.stop_scheduler()
    except Exception as e:
        print(f"⚠️ Shutdown warning: {e}")
    
app = FastAPI(
    title="Restaurant Voice Agent API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Models
# --------------------------------------------------

class CustomerCreate(BaseModel):
    name: str
    mobile: str
    email: Optional[str] = ""
    customer_id: Optional[str] = ""
    timestamp: Optional[str] = ""


class CustomerResponse(BaseModel):
    customer_id: str
    name: str
    mobile: str
    email: str
    timestamp: str


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.post("/customer", response_model=dict)
async def create_customer(customer: CustomerCreate):
    try:
        customer_id = await csv_utils.add_customer(
            name=customer.name,
            mobile=customer.mobile,
            email=customer.email or "",
            timestamp=customer.timestamp or "",
            customer_id=customer.customer_id or ""
        )
        return {"success": True, "customer_id": customer_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/customers", response_model=List[CustomerResponse])
async def get_customers():
    customers = await csv_utils.get_all_customers()
    return [
        CustomerResponse(
            customer_id=c.get("customer_id", ""),
            name=c.get("name", ""),
            mobile=c.get("mobile", ""),
            email=c.get("email", ""),
            timestamp=c.get("timestamp", "")
        )
        for c in customers
    ]


@app.get("/customer/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    customer = await csv_utils.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return CustomerResponse(**customer)


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
    Automatically sends email based on call status:
    - If status is "in_progress": sends wait email
    - If status is "completed": sends reservation confirmation email
    """
    result = await phone_handler.get_call_detail(call_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get("error", "Call not found")
        )
    
    # Send email based on call status
    call_data = result.get("data", {})
    call_status = call_data.get("status", "")
    
    if call_status in ["in_progress", "completed"]:
        await phone_handler.send_reservation_email(
            email="",
            customer_name="",
            date="",
            time="",
            number_of_people="",
            call_data=call_data
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
    """Health check endpoint for dev tunnel and monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Restaurant Voice Agent API"
    }

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle OPTIONS requests for CORS preflight."""
    return {"message": "OK"}


# --------------------------------------------------
# Run
# --------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
