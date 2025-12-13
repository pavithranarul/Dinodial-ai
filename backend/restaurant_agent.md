You are an expert Voice AI + Backend Engineer.

Build a Restaurant Voice Agent system using Dinodial.ai (telephony-based voice agent).

GOAL:
Create an automated restaurant calling agent that:
1. Collects customer name and mobile number from a UI
2. Stores customer data in a CSV file
3. Uses Dinodial.ai to make outbound calls
4. Handles order booking, arrival confirmation, and missed-customer recovery
5. Automatically follows up with customers who do not reach the restaurant

----------------------------------------
SYSTEM REQUIREMENTS
----------------------------------------

TECH STACK:
- Backend: Python (FastAPI preferred)
- Storage: CSV file (customers.csv)
- Voice Agent: Dinodial.ai (outbound calling)
- No database (CSV only)

----------------------------------------
DATA MODEL (CSV)
----------------------------------------

Create `customers.csv` with columns:

customer_id,
name,
mobile,
status,
order_details,
expected_arrival_time,
arrival_confirmed,
last_call_time,
remarks

Status values:
- new
- called
- order_confirmed
- arrived
- no_show
- follow_up_pending
- resolved

----------------------------------------
BACKEND API REQUIREMENTS
----------------------------------------

1. POST /customer
   - Input: name, mobile, optional expected_arrival_time
   - Action:
     - Generate customer_id
     - Append row to CSV
     - status = "new"

2. GET /customers
   - Returns all customer records from CSV

3. POST /trigger-call/{customer_id}
   - Triggers Dinodial.ai outbound call
   - Pass customer context to the voice agent

----------------------------------------
VOICE AGENT BEHAVIOR (Dinodial.ai)
----------------------------------------

The agent must behave like a polite restaurant assistant.

### Call Flow 1: Order Booking
Trigger when status = "new"

Script:
"Hello {{name}}, this is calling from {{Restaurant Name}}.
We noticed your interest in dining with us today.
I just want to confirm your order and any special requirements.

Are you planning to dine in or take away?
Do you have any special food preferences?
What time will you be arriving?"

Capture:
- order_details
- expected_arrival_time

Update CSV:
- status = "order_confirmed"

----------------------------------------

### Call Flow 2: Arrival Confirmation
Trigger when expected_arrival_time has passed and arrival_confirmed = false

Script:
"Hi {{name}}, this is {{Restaurant Name}}.
Just checking if you’ve reached the restaurant or are on the way?"

Responses:
- If arrived → arrival_confirmed = true, status = "arrived"
- If on the way → retry later
- If not coming → status = "no_show"

----------------------------------------

### Call Flow 3: Missed Customer Recovery
Trigger when status = "no_show"

Script:
"Hi {{name}}, this is {{Restaurant Name}}.
We noticed you couldn’t make it earlier, no worries at all.
Would you like to reschedule your visit, place a takeaway order, or cancel for today?"

Actions:
- Reschedule → update expected_arrival_time, status = "order_confirmed"
- Takeaway → update order_details, status = "resolved"
- Cancel → status = "resolved"

----------------------------------------
AUTOMATION LOGIC
----------------------------------------

Implement a background scheduler that:
- Scans the CSV every few minutes
- Triggers appropriate calls based on status and time
- Updates call outcomes back into the CSV

----------------------------------------
OUTPUT EXPECTATION
----------------------------------------
d
Generate:
1. FastAPI backend code
2. CSV read/write utilities
3. Dinodial.ai call trigger placeholders
4. Clear function separation for each call flow
5. Clean, readable, hackathon-ready code

Focus on simplicity, clarity, and demo readiness.
