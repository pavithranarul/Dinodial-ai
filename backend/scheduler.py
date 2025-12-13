from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import client_handler
import csv_utils
import phone_handler
from datetime import datetime
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# Track call IDs that have already sent reservation emails
sent_emails_cache = set()

async def scan_and_trigger_calls():
    logger.info("Scanning customers for automated calls...")
    
    new_customers = await csv_utils.get_customers_by_status("new")
    for customer in new_customers:
        customer_id = customer.get("customer_id")
        if customer_id:
            logger.info(f"Triggering order booking call for {customer_id}")
            result = await client_handler.trigger_order_booking_call(customer_id)
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
                result = await client_handler.trigger_arrival_confirmation_call(customer_id)
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
            result = await client_handler.trigger_missed_customer_recovery_call(customer_id)
            if not result.get("success"):
                logger.warning(f"Failed to trigger recovery call for {customer_id}: {result.get('error')}")

async def check_and_send_reservation_emails():
    """
    Automatically check completed calls and send reservation confirmation emails.
    """
    logger.info("Checking completed calls for reservation confirmations...")
    
    try:
        # Get list of completed calls
        calls_result = await phone_handler.get_calls_list({"limit": 50})
        
        if not calls_result.get("success"):
            logger.warning(f"Failed to get calls list: {calls_result.get('error')}")
            return
        
        calls_data = calls_result.get("data", {})
        calls = calls_data.get("results", [])
        
        # Filter for completed calls
        completed_calls = [call for call in calls if call.get("status") == "completed"]
        
        for call in completed_calls:
            call_id = call.get("id")
            call_id_str = str(call_id)
            
            # Skip if email already sent for this call
            if call_id_str in sent_emails_cache:
                continue
            
            try:
                # Get call details
                detail_result = await phone_handler.get_call_detail(call_id)
                
                if not detail_result.get("success"):
                    continue
                
                call_data = detail_result.get("data", {})
                
                # Check and send reservation email
                email_result = await phone_handler.send_reservation_email(
                    email="",  # Will be extracted from call_data
                    customer_name="",
                    date="",
                    time="",
                    number_of_people="",
                    call_data=call_data
                )
                
                if email_result.get("success"):
                    sent_emails_cache.add(call_id_str)
                    logger.info(f"✅ Reservation email sent for call ID {call_id}")
                elif email_result.get("message") == "No reservation confirmed in this call":
                    # Not a reservation call, mark as processed to avoid rechecking
                    sent_emails_cache.add(call_id_str)
                else:
                    logger.debug(f"⏭️ Skipping call ID {call_id}: {email_result.get('message')}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing call ID {call_id}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"❌ Error in check_and_send_reservation_emails: {e}")


async def start_scheduler():
    scheduler.add_job(
        scan_and_trigger_calls,
        trigger=IntervalTrigger(minutes=5),
        id='scan_customers',
        name='Scan and trigger customer calls',
        replace_existing=True
    )
    scheduler.add_job(
        check_and_send_reservation_emails,
        trigger=IntervalTrigger(minutes=2),
        id='check_reservation_emails',
        name='Check and send reservation emails',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Background scheduler started (runs every 5 minutes for calls, every 2 minutes for emails)")

async def stop_scheduler():
    scheduler.shutdown()
    logger.info("Background scheduler stopped")

