import sys
import threading
import time
import MetaTrader5 as mt5
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
from typing import Optional, List, Set
from dataclasses import dataclass
from email_templates import (
    format_position_html,
    format_order_html,
    format_closed_order_html
)

# Load environment variables
load_dotenv()

# Global variables
internet_available = False
mt5_initialized = False
mt5_lock = threading.Lock()


@dataclass
class Config:
    """Configuration class to hold all settings"""
    sender_email: str
    sender_password: str
    recipient_email: str
    smtp_server: str
    smtp_port: int
    delay: float
    account_id: int
    server: str
    password: str
    mt5_path: str


def check_internet() -> bool:
    """Check if internet connection is available and update the global variable."""
    global internet_available
    try:
        requests.get("https://www.google.com", timeout=3)
        internet_available = True
        return True
    except (requests.ConnectionError, requests.Timeout):
        internet_available = False
        return False


def initialize_mt5(config: Config) -> bool:
    """Initialize MT5 connection (thread-safe)."""
    global mt5_initialized
    with mt5_lock:
        if mt5_initialized:
            return True
        if mt5.initialize(path=config.mt5_path, login=config.account_id, 
                         server=config.server, password=config.password):
            mt5_initialized = True
            return True
        else:
            print(f"initialize() failed, error code = {mt5.last_error()}")
            return False


def get_account_info():
    """Get account information from MT5."""
    account_info = mt5.account_info()
    if account_info is None:
        return None, None, None
    return account_info.name, account_info.balance, account_info.equity


def send_email(config: Config, subject: str, html_body: str, plain_body: str, log_message: str) -> bool:
    """Send HTML email notification with error handling."""
    try:
        message = MIMEMultipart("alternative")
        message["From"] = config.sender_email
        message["To"] = config.recipient_email
        message["Subject"] = subject
        
        # Add both plain text and HTML versions
        message.attach(MIMEText(plain_body, "plain"))
        message.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            server.starttls()
            server.login(config.sender_email, config.sender_password)
            server.sendmail(config.sender_email, config.recipient_email, message.as_string())
        
        date = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        print(f"[{date}] {log_message}")
        return True
    except Exception as e:
        date = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        print(f"[{date}] Error sending email: {e}")
        return False


def get_email_on_new_positions(config: Config):
    """Monitor and send email notifications for new positions."""
    date = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    print(f"[{date}] Starting MetaTrader 5 Server...")
    print(f"MetaTrader5 package author: {mt5.__author__}")
    print(f"MetaTrader5 package version: {mt5.__version__}\n")
    
    if not initialize_mt5(config):
        return
    
    prev_positions_ids: Set[int] = set()
    
    # Initialize with current positions
    positions = mt5.positions_get()
    if positions is None:
        print(f"No Active positions Now, error code={mt5.last_error()}")
    else:
        prev_positions_ids = {pos.ticket for pos in positions}
        print(f"Total Active positions: {len(positions)}")
    
    account_info_cache = None
    cache_time = 0
    cache_ttl = 5  # Cache account info for 5 seconds
    
    while internet_available:
        # Cache account info to reduce API calls
        current_time = time.time()
        if current_time - cache_time > cache_ttl:
            account_info_cache = get_account_info()
            cache_time = current_time
        
        if account_info_cache[0] is None:
            time.sleep(config.delay)
            continue
        
        account_name, account_balance, account_equity = account_info_cache
        
        positions = mt5.positions_get()
        if positions is None:
            time.sleep(config.delay)
            continue
        
        current_ids = {pos.ticket for pos in positions}
        new_ids = current_ids - prev_positions_ids
        
        if new_ids:
            new_positions = [pos for pos in positions if pos.ticket in new_ids]
            html_body, plain_body = format_position_html(new_positions, account_name, account_balance, account_equity, is_new=True)
            subject = f"New Position Opened on {account_name}"
            
            # Send email notification
            send_email(config, subject, html_body, plain_body, "Email sent for new position opened")
            prev_positions_ids.update(new_ids)
        
        time.sleep(config.delay)


def get_email_on_new_orders(config: Config):
    """Monitor and send email notifications for new pending orders."""
    time.sleep(2)  # Stagger startup
    
    if not initialize_mt5(config):
        return
    
    prev_orders_ids: Set[int] = set()
    
    # Initialize with current orders
    orders = mt5.orders_get()
    if orders is None:
        print(f"No pending orders Now, error code={mt5.last_error()}")
    else:
        prev_orders_ids = {order.ticket for order in orders if order.type not in [0, 1]}
        print(f"Total pending orders: {len(orders)}")
    
    account_info_cache = None
    cache_time = 0
    cache_ttl = 5
    
    while internet_available:
        current_time = time.time()
        if current_time - cache_time > cache_ttl:
            account_info_cache = get_account_info()
            cache_time = current_time
        
        if account_info_cache[0] is None:
            time.sleep(config.delay)
            continue
        
        account_name, account_balance, account_equity = account_info_cache
        
        orders = mt5.orders_get()
        if orders is None:
            time.sleep(config.delay)
            continue
        
        current_ids = {order.ticket for order in orders if order.type not in [0, 1]}
        new_ids = current_ids - prev_orders_ids
        
        if new_ids:
            new_orders = [order for order in orders if order.ticket in new_ids and order.type not in [0, 1]]
            html_body, plain_body = format_order_html(new_orders, account_name, account_balance, account_equity, "Placed")
            subject = f"New Pending Order Placed On {account_name}"
            
            # Send email notification
            send_email(config, subject, html_body, plain_body, "Email sent for new pending order placed")
            prev_orders_ids.update(new_ids)
        
        time.sleep(config.delay)


def get_email_on_close_orders(config: Config):
    """Monitor and send email notifications for deleted pending orders."""
    if not initialize_mt5(config):
        return
    
    all_orders_ids: Set[int] = set()
    
    account_info_cache = None
    cache_time = 0
    cache_ttl = 5
    
    while internet_available:
        current_time = time.time()
        if current_time - cache_time > cache_ttl:
            account_info_cache = get_account_info()
            cache_time = current_time
        
        if account_info_cache[0] is None:
            time.sleep(config.delay)
            continue
        
        account_name, account_balance, account_equity = account_info_cache
        
        orders = mt5.orders_get()
        if orders is None:
            time.sleep(config.delay)
            continue
        
        current_ids = {order.ticket for order in orders}
        all_orders_ids.update(current_ids)
        
        deleted_ids = all_orders_ids - current_ids
        if deleted_ids:
            try:
                deleted_order = mt5.history_orders_get(ticket=list(deleted_ids)[0])
                if deleted_order and len(deleted_order) > 0:
                    deleted_order = deleted_order[0]
                    if deleted_order.type not in [0, 1]:
                        print(f"Pending Order with ID {deleted_ids} has been deleted.")
                        html_body, plain_body = format_order_html([deleted_order], account_name, account_balance, 
                                                                  account_equity, "Deleted")
                        subject = f"Pending Order Deleted On {account_name}"
                        
                        # Send email notification
                        send_email(config, subject, html_body, plain_body, "Email sent for Pending Order Deleted")
                        all_orders_ids = current_ids.copy()
            except Exception as e:
                print(f"Error processing deleted order: {e}")
        
        time.sleep(config.delay)


def get_email_on_close_positions(config: Config):
    """Monitor and send email notifications for closed positions."""
    if not initialize_mt5(config):
        return
    
    all_positions_ids: Set[int] = set()
    
    account_info_cache = None
    cache_time = 0
    cache_ttl = 5
    
    while internet_available:
        current_time = time.time()
        if current_time - cache_time > cache_ttl:
            account_info_cache = get_account_info()
            cache_time = current_time
        
        if account_info_cache[0] is None:
            time.sleep(config.delay)
            continue
        
        account_name, account_balance, account_equity = account_info_cache
        
        positions = mt5.positions_get()
        if positions is None:
            time.sleep(config.delay)
            continue
        
        current_ids = {pos.ticket for pos in positions}
        all_positions_ids.update(current_ids)
        
        closed_ids = all_positions_ids - current_ids
        if closed_ids:
            try:
                closed_order = mt5.history_orders_get(ticket=list(closed_ids)[0])
                if closed_order and len(closed_order) > 0:
                    closed_order = closed_order[0]
                    html_body, plain_body = format_closed_order_html(closed_order, account_name, account_balance, account_equity)
                    subject = f"Order Closed On {account_name}"
                    
                    # Send email notification
                    send_email(config, subject, html_body, plain_body, "Email sent for Order Closed")
                    all_positions_ids = current_ids.copy()
            except Exception as e:
                print(f"Error processing closed position: {e}")
        
        time.sleep(config.delay)


def main():
    """Main function to initialize and start monitoring threads."""
    # Load configuration from environment variables
    config = Config(
        sender_email=os.getenv('SENDER_EMAIL', ''),
        sender_password=os.getenv('SENDER_PASSWORD', ''),
        recipient_email=os.getenv('RECIPIENT_EMAIL', ''),
        smtp_server=os.getenv('SMTP_SERVER', ''),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        delay=float(os.getenv('DELAY', '0.1')),
        account_id=int(os.getenv('ACCOUNT_ID', '0')),
        server=os.getenv('SERVER', ''),
        password=os.getenv('PASS', ''),
        mt5_path=os.getenv('MT5_PATH', '')
    )
    
    # Validate configuration
    if not all([config.sender_email, config.recipient_email, config.smtp_server, 
                config.account_id, config.server, config.mt5_path]):
        print("Error: Missing required configuration. Please check your .env file.")
        sys.exit(1)
    
    check_internet()
    
    if not internet_available:
        print("Error: No internet connection available.")
        sys.exit(1)
    
    # Start monitoring threads
    threads = [
        threading.Thread(target=get_email_on_new_positions, args=(config,), daemon=True),
        threading.Thread(target=get_email_on_new_orders, args=(config,), daemon=True),
        threading.Thread(target=get_email_on_close_orders, args=(config,), daemon=True),
        threading.Thread(target=get_email_on_close_positions, args=(config,), daemon=True)
    ]
    
    for thread in threads:
        thread.start()
    
    # Monitor internet connection
    try:
        while True:
            time.sleep(30)
            if not check_internet():
                print("Internet connection lost. Exiting...")
                sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        mt5.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
