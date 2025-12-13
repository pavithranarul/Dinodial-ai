from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import csv_utils
import dinodial_client
from datetime import datetime
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def scan_and_trigger_calls():
    logger.info("Scanning customers for automated calls...")
    
    new_customers = await csv_utils.get_customers_by_status("new")
    for customer in new_customers:
        customer_id = customer.get("customer_id")
        if customer_id:
            logger.info(f"Triggering order booking call for {customer_id}")
            result = await dinodial_client.trigger_order_booking_call(customer_id)
            if not result.get("success"):
                logger.warning(f"Failed to trigger call for {customer_id}: {result.get('error')}")
    
    arrival_check_customers = await csv_utils.get_customers_for_arrival_check()
    for customer in arrival_check_customers:
        customer_id = customer.get("customer_id")
        arrival_confirmed = customer.get("arrival_confirmed", "false").lower() == "true"
        
        if customer_id and not arrival_confirmed:
            status = customer.get("status", "")
            if status in ["order_confirmed", "called"]:
                logger.info(f"Triggering arrival confirmation call for {customer_id}")
                result = await dinodial_client.trigger_arrival_confirmation_call(customer_id)
                if not result.get("success"):
                    logger.warning(f"Failed to trigger arrival call for {customer_id}: {result.get('error')}")
    
    no_show_customers = await csv_utils.get_customers_by_status("no_show")
    for customer in no_show_customers:
        customer_id = customer.get("customer_id")
        last_call_time_str = customer.get("last_call_time", "")
        
        should_call = True
        if last_call_time_str:
            try:
                last_call_time = datetime.fromisoformat(last_call_time_str.replace('Z', '+00:00'))
                time_since_call = (datetime.now() - last_call_time.replace(tzinfo=None)).total_seconds() / 60
                if time_since_call < 30:
                    should_call = False
            except (ValueError, AttributeError):
                pass
        
        if customer_id and should_call:
            logger.info(f"Triggering missed customer recovery call for {customer_id}")
            result = await dinodial_client.trigger_missed_customer_recovery_call(customer_id)
            if not result.get("success"):
                logger.warning(f"Failed to trigger recovery call for {customer_id}: {result.get('error')}")

async def start_scheduler():
    scheduler.add_job(
        scan_and_trigger_calls,
        trigger=IntervalTrigger(minutes=5),
        id='scan_customers',
        name='Scan and trigger customer calls',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Background scheduler started (runs every 5 minutes)")

async def stop_scheduler():
    scheduler.shutdown()
    logger.info("Background scheduler stopped")

