"""
HTML Email Templates for MT5 Trading Notifications
"""
from datetime import datetime
from typing import List
import MetaTrader5 as mt5

# Constants
ORDER_TYPE_DICT = {
    2: 'BUY_LIMIT',
    3: 'SELL_LIMIT',
    4: 'BUY_STOP',
    5: 'SELL_STOP',
    6: 'BUY_STOP_LIMIT',
    7: 'SELL_STOP_LIMIT'
}


def get_html_template(title: str, account_name: str, content: str, color: str = "#2196F3") -> str:
    """Generate HTML email template with styling."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, {color} 0%, #1976D2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px;
            }}
            .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: #f9f9f9;
                border-radius: 6px;
                overflow: hidden;
            }}
            .info-table th {{
                background-color: {color};
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }}
            .info-table td {{
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
            }}
            .info-table tr:last-child td {{
                border-bottom: none;
            }}
            .info-table tr:nth-child(even) {{
                background-color: #ffffff;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            .badge-buy {{
                background-color: #4CAF50;
                color: white;
            }}
            .badge-sell {{
                background-color: #F44336;
                color: white;
            }}
            .badge-pending {{
                background-color: #FF9800;
                color: white;
            }}
            .footer {{
                background-color: #f5f5f5;
                padding: 15px;
                text-align: center;
                color: #666;
                font-size: 12px;
                border-top: 1px solid #e0e0e0;
            }}
            .account-info {{
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 6px;
                margin: 15px 0;
            }}
            .account-info strong {{
                color: {color};
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{title}</h1>
            </div>
            <div class="content">
                <div class="account-info">
                    <strong>Account:</strong> {account_name}<br>
                    <strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")}
                </div>
                {content}
            </div>
            <div class="footer">
                <p>MetaTrader 5 Trading Bot Notification System</p>
            </div>
        </div>
    </body>
    </html>
    """


def format_position_html(positions: List, account_name: str, account_balance: float, 
                         account_equity: float, is_new: bool = True) -> tuple:
    """Format HTML and plain text for position notifications."""
    action = "Opened" if is_new else "Closed"
    color = "#4CAF50" if is_new else "#F44336"
    
    html_rows = []
    plain_parts = [f"Position {action} on {account_name}\n\n"]
    
    for pos in positions:
        order_type = "Buy" if pos.type == mt5.ORDER_TYPE_BUY else "Sell"
        badge_class = "badge-buy" if pos.type == mt5.ORDER_TYPE_BUY else "badge-sell"
        
        html_rows.append(f"""
        <tr>
            <td><strong>Order ID</strong></td>
            <td>{pos.ticket}</td>
        </tr>
        <tr>
            <td><strong>Symbol</strong></td>
            <td>{pos.symbol}</td>
        </tr>
        <tr>
            <td><strong>Type</strong></td>
            <td><span class="badge {badge_class}">{order_type}</span></td>
        </tr>
        <tr>
            <td><strong>Lots</strong></td>
            <td>{pos.volume}</td>
        </tr>
        <tr>
            <td><strong>Open Price</strong></td>
            <td>{pos.price_open}</td>
        </tr>
        <tr>
            <td><strong>Stop Loss</strong></td>
            <td>{pos.sl if pos.sl > 0 else 'Not Set'}</td>
        </tr>
        <tr>
            <td><strong>Take Profit</strong></td>
            <td>{pos.tp if pos.tp > 0 else 'Not Set'}</td>
        </tr>
        """)
        
        plain_parts.append(f"Position info:\n")
        plain_parts.append(f"Order ID: {pos.ticket}\n")
        plain_parts.append(f"Symbol: {pos.symbol}\n")
        plain_parts.append(f"Type: {order_type}\n")
        plain_parts.append(f"Lots: {pos.volume}\n")
        plain_parts.append(f"Open price: {pos.price_open}\n")
        plain_parts.append(f"Stop Loss: {pos.sl if pos.sl > 0 else 'Not Set'}\n")
        plain_parts.append(f"Take Profit: {pos.tp if pos.tp > 0 else 'Not Set'}\n")
        plain_parts.append(f"Balance: {account_balance}\n")
        plain_parts.append(f"Equity: {account_equity}\n\n")
    
    html_content = f"""
    <table class="info-table">
        <thead>
            <tr>
                <th colspan="2">Position Details</th>
            </tr>
        </thead>
        <tbody>
            {''.join(html_rows)}
            <tr>
                <td><strong>Account Balance</strong></td>
                <td>{account_balance:.2f}</td>
            </tr>
            <tr>
                <td><strong>Account Equity</strong></td>
                <td>{account_equity:.2f}</td>
            </tr>
        </tbody>
    </table>
    """
    
    html_body = get_html_template(f"Position {action}", account_name, html_content, color)
    plain_body = "".join(plain_parts)
    
    return html_body, plain_body


def format_order_html(orders: List, account_name: str, account_balance: float, 
                     account_equity: float, action: str) -> tuple:
    """Format HTML and plain text for order notifications."""
    color = "#FF9800" if action == "Placed" else "#F44336"
    
    html_rows = []
    plain_parts = [f"Pending Order {action} on {account_name}\n\n"]
    
    for order in orders:
        order_type = ORDER_TYPE_DICT.get(order.type, 'UNKNOWN')
        
        html_rows.append(f"""
        <tr>
            <td><strong>Order ID</strong></td>
            <td>{order.ticket}</td>
        </tr>
        <tr>
            <td><strong>Symbol</strong></td>
            <td>{order.symbol}</td>
        </tr>
        <tr>
            <td><strong>Type</strong></td>
            <td><span class="badge badge-pending">{order_type}</span></td>
        </tr>
        <tr>
            <td><strong>Lots</strong></td>
            <td>{order.volume_current}</td>
        </tr>
        <tr>
            <td><strong>Price</strong></td>
            <td>{order.price_open}</td>
        </tr>
        <tr>
            <td><strong>Stop Loss</strong></td>
            <td>{order.sl if order.sl > 0 else 'Not Set'}</td>
        </tr>
        <tr>
            <td><strong>Take Profit</strong></td>
            <td>{order.tp if order.tp > 0 else 'Not Set'}</td>
        </tr>
        """)
        
        plain_parts.append(f"Order info:\n")
        plain_parts.append(f"Order ID: {order.ticket}\n")
        plain_parts.append(f"Symbol: {order.symbol}\n")
        plain_parts.append(f"Type: {order_type}\n")
        plain_parts.append(f"Lots: {order.volume_current}\n")
        plain_parts.append(f"Price: {order.price_open}\n")
        plain_parts.append(f"Stop Loss: {order.sl if order.sl > 0 else 'Not Set'}\n")
        plain_parts.append(f"Take Profit: {order.tp if order.tp > 0 else 'Not Set'}\n")
        plain_parts.append(f"Balance: {account_balance}\n")
        plain_parts.append(f"Equity: {account_equity}\n\n")
    
    html_content = f"""
    <table class="info-table">
        <thead>
            <tr>
                <th colspan="2">Order Details</th>
            </tr>
        </thead>
        <tbody>
            {''.join(html_rows)}
            <tr>
                <td><strong>Account Balance</strong></td>
                <td>{account_balance:.2f}</td>
            </tr>
            <tr>
                <td><strong>Account Equity</strong></td>
                <td>{account_equity:.2f}</td>
            </tr>
        </tbody>
    </table>
    """
    
    html_body = get_html_template(f"Pending Order {action}", account_name, html_content, color)
    plain_body = "".join(plain_parts)
    
    return html_body, plain_body


def format_closed_order_html(deleted_order, account_name: str, account_balance: float, 
                            account_equity: float) -> tuple:
    """Format HTML and plain text for closed order notifications."""
    order_type = "Buy" if deleted_order.type == mt5.ORDER_TYPE_BUY else "Sell"
    badge_class = "badge-buy" if deleted_order.type == mt5.ORDER_TYPE_BUY else "badge-sell"
    
    html_content = f"""
    <table class="info-table">
        <thead>
            <tr>
                <th colspan="2">Closed Order Details</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Order ID</strong></td>
                <td>{deleted_order.ticket}</td>
            </tr>
            <tr>
                <td><strong>Symbol</strong></td>
                <td>{deleted_order.symbol}</td>
            </tr>
            <tr>
                <td><strong>Type</strong></td>
                <td><span class="badge {badge_class}">{order_type}</span></td>
            </tr>
            <tr>
                <td><strong>Lots</strong></td>
                <td>{deleted_order.volume_initial}</td>
            </tr>
            <tr>
                <td><strong>Close Price</strong></td>
                <td>{deleted_order.price_current}</td>
            </tr>
            <tr>
                <td><strong>Stop Loss</strong></td>
                <td>{deleted_order.sl if deleted_order.sl > 0 else 'Not Set'}</td>
            </tr>
            <tr>
                <td><strong>Take Profit</strong></td>
                <td>{deleted_order.tp if deleted_order.tp > 0 else 'Not Set'}</td>
            </tr>
            <tr>
                <td><strong>Account Balance</strong></td>
                <td>{account_balance:.2f}</td>
            </tr>
            <tr>
                <td><strong>Account Equity</strong></td>
                <td>{account_equity:.2f}</td>
            </tr>
        </tbody>
    </table>
    """
    
    html_body = get_html_template("Order Closed", account_name, html_content, "#F44336")
    
    plain_body = f"""Order Closed on {account_name}

Order info:
Order ID: {deleted_order.ticket}
Symbol: {deleted_order.symbol}
Type: {order_type}
Lots: {deleted_order.volume_initial}
Price: {deleted_order.price_current}
Stop Loss: {deleted_order.sl if deleted_order.sl > 0 else 'Not Set'}
Take Profit: {deleted_order.tp if deleted_order.tp > 0 else 'Not Set'}
Balance: {account_balance}
Equity: {account_equity}
"""
    
    return html_body, plain_body
