# Restaurant Voice Agent System

Automated restaurant calling agent using Dinodial.ai for outbound calls, order booking, arrival confirmation, and missed-customer recovery.

## Features

- **Customer Management**: Add customers via API, stored in CSV
- **Automated Calling**: Background scheduler triggers calls based on customer status
- **Three Call Flows**:
  1. Order Booking (for new customers)
  2. Arrival Confirmation (when expected time passes)
  3. Missed Customer Recovery (for no-shows)

## Setup

1. Install Poetry (if not already installed):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies using Poetry:

```bash
poetry install
```

Alternatively, using pip:

```bash
pip install -r requirements.txt
```

3. Configure Dinodial.ai API key in `dinodial_client.py`:

```python
DINODIAL_API_KEY = "your-api-key-here"
```

4. Run the application:

Using Poetry:

```bash
poetry run python main.py
```

Or directly:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /customer

Create a new customer record.

**Request Body:**

```json
{
  "name": "John Doe",
  "mobile": "+1234567890",
  "expected_arrival_time": "2024-01-15T19:00:00" // optional
}
```

### GET /customers

Get all customer records.

### GET /customer/{customer_id}

Get a specific customer by ID.

### POST /trigger-call/{customer_id}

Manually trigger a call for a customer based on their current status.

### POST /webhook/call-result

Webhook endpoint for Dinodial.ai to send call results.

**Request Body:**

```json
{
  "customer_id": "CUST000001",
  "call_flow": "order_booking",
  "result": {
    "order_details": "2 pizzas, 1 pasta",
    "expected_arrival_time": "2024-01-15T19:00:00"
  }
}
```

### GET /health

Health check endpoint.

## Background Scheduler

The system includes a background scheduler that runs every 5 minutes to:

- Trigger order booking calls for new customers
- Check for customers past their expected arrival time
- Trigger recovery calls for no-show customers

## Data Model

Customers are stored in `customers.csv` with the following columns:

- `customer_id`: Unique identifier
- `name`: Customer name
- `mobile`: Phone number
- `status`: Current status (new, called, order_confirmed, arrived, no_show, follow_up_pending, resolved)
- `order_details`: Order information
- `expected_arrival_time`: Expected arrival datetime
- `arrival_confirmed`: Boolean flag
- `last_call_time`: Timestamp of last call
- `remarks`: Additional notes

## Call Flows

### Order Booking

Triggered when `status = "new"`

- Confirms order details
- Captures arrival time
- Updates status to `order_confirmed`

### Arrival Confirmation

Triggered when expected arrival time has passed and `arrival_confirmed = false`

- Checks if customer has arrived
- Updates status based on response

### Missed Customer Recovery

Triggered when `status = "no_show"`

- Offers reschedule, takeaway, or cancellation
- Updates status accordingly
