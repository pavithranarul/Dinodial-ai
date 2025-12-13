import csv
import os
from typing import List, Dict, Optional

CSV_FILE = "customers.csv"
CSV_COLUMNS = ["customer_id", "name", "mobile"]


# --------------------------------------------------
# CSV Initialization
# --------------------------------------------------

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()


# --------------------------------------------------
# Read / Write Helpers
# --------------------------------------------------

def read_customers() -> List[Dict[str, str]]:
    init_csv()
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_customers(customers: List[Dict[str, str]]) -> None:
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(customers)


# --------------------------------------------------
# CRUD Operations
# --------------------------------------------------

def add_customer(name: str, mobile: str) -> str:
    customers = read_customers()

    customer_id = f"CUST{len(customers) + 1:06d}"

    customers.append({
        "customer_id": customer_id,
        "name": name,
        "mobile": mobile
    })

    write_customers(customers)
    return customer_id


def get_customer_by_id(customer_id: str) -> Optional[Dict[str, str]]:
    for customer in read_customers():
        if customer["customer_id"] == customer_id:
            return customer
    return None


def get_all_customers() -> List[Dict[str, str]]:
    return read_customers()
