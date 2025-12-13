import csv
import os
import asyncio
from typing import List, Dict, Optional
from datetime import datetime

CSV_FILE = "customers.csv"
CSV_COLUMNS = ["customer_id", "name", "mobile"]


# --------------------------------------------------
# CSV Initialization
# --------------------------------------------------

async def init_csv():
    if not os.path.exists(CSV_FILE):
        # Use sync file operation for initialization
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()


# --------------------------------------------------
# Read / Write Helpers
# --------------------------------------------------

async def read_customers() -> List[Dict[str, str]]:
    await init_csv()
    # Use asyncio.to_thread for file I/O to avoid blocking
    def _read():
        customers = []
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                customers.append(dict(row))
        return customers
    
    return await asyncio.to_thread(_read)


async def write_customers(customers: List[Dict[str, str]]) -> None:
    await init_csv()
    # Use asyncio.to_thread for file I/O to avoid blocking
    def _write():
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for customer in customers:
                # Only write the columns that exist in CSV_COLUMNS
                row = {col: customer.get(col, "") for col in CSV_COLUMNS}
                writer.writerow(row)
    
    await asyncio.to_thread(_write)


# --------------------------------------------------
# CRUD Operations
# --------------------------------------------------

async def add_customer(name: str, mobile: str) -> str:
    customers = await read_customers()

    customer_id = f"CUST{len(customers) + 1:06d}"

    customers.append({
        "customer_id": customer_id,
        "name": name,
        "mobile": mobile
    })

    await write_customers(customers)
    return customer_id


async def get_customer_by_id(customer_id: str) -> Optional[Dict[str, str]]:
    customers = await read_customers()
    for customer in customers:
        if customer["customer_id"] == customer_id:
            return customer
    return None


async def get_all_customers() -> List[Dict[str, str]]:
    return await read_customers()


async def get_customers_by_status(status: str) -> List[Dict[str, str]]:
    """Get all customers with a specific status."""
    customers = await read_customers()
    return [c for c in customers if c.get("status", "") == status]


async def get_customers_for_arrival_check() -> List[Dict[str, str]]:
    """Get customers who are past their expected arrival time."""
    customers = await read_customers()
    now = datetime.now()
    result = []
    
    for customer in customers:
        expected_time_str = customer.get("expected_arrival_time", "")
        if expected_time_str:
            try:
                expected_time = datetime.fromisoformat(expected_time_str.replace('Z', '+00:00'))
                if expected_time.replace(tzinfo=None) < now:
                    result.append(customer)
            except (ValueError, AttributeError):
                pass
    
    return result


async def update_customer(customer_id: str, updates: Dict[str, str]) -> bool:
    """Update customer fields."""
    customers = await read_customers()
    updated = False
    
    for customer in customers:
        if customer["customer_id"] == customer_id:
            customer.update(updates)
            updated = True
            break
    
    if updated:
        await write_customers(customers)
    
    return updated
