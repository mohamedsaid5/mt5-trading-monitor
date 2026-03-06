# MT5 Trading Monitor

A Python-based monitoring system for MetaTrader 5 that sends real-time email notifications for trading activities. Monitor your MT5 account and receive beautifully formatted HTML email alerts for new positions, pending orders, order deletions, and position closures.

## Features

- 🔔 **Real-time Monitoring**: Continuously monitors MT5 account for trading activities
- 📧 **HTML Email Notifications**: Professional, styled HTML email templates
- 🎯 **Multiple Event Types**: 
  - New positions opened
  - New pending orders placed
  - Pending orders deleted
  - Positions closed
- ⚡ **Optimized Performance**: 
  - Thread-safe MT5 initialization
  - Account info caching
  - Efficient data structures (sets for O(1) lookups)
- 🔒 **Secure Configuration**: Environment variables for sensitive data
- 🌐 **Internet Monitoring**: Automatic shutdown if connection is lost

## Requirements

- Python 3.7+
- MetaTrader 5 terminal installed
- Active MT5 account
- SMTP email account for sending notifications

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mohamedsaid5/mt5-trading-monitor.git
   cd mt5-trading-monitor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   # Email Configuration
   SENDER_EMAIL=your_email@example.com
   SENDER_PASSWORD=your_email_password
   RECIPIENT_EMAIL=recipient@example.com
   SMTP_SERVER=smtp.example.com
   SMTP_PORT=587
   
   # MetaTrader 5 Configuration
   MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
   ACCOUNT_ID=your_account_id
   SERVER=your_broker_server
   PASS=your_mt5_password
   
   # Monitoring Configuration
   DELAY=0.1
   ```

## Usage

Run the monitoring script:

```bash
python mt5_monitor.py
```

The script will:
1. Initialize connection to MT5
2. Start monitoring threads for different event types
3. Send email notifications when events occur
4. Continue running until interrupted (Ctrl+C) or internet connection is lost

## Configuration

### Email Settings
- `SENDER_EMAIL`: Email address to send notifications from
- `SENDER_PASSWORD`: Password for the sender email account
- `RECIPIENT_EMAIL`: Email address to receive notifications
- `SMTP_SERVER`: SMTP server address (e.g., smtp.gmail.com)
- `SMTP_PORT`: SMTP port (usually 587 for TLS)

### MT5 Settings
- `MT5_PATH`: Full path to MT5 terminal executable
- `ACCOUNT_ID`: Your MT5 account number
- `SERVER`: Your broker's MT5 server name
- `PASS`: Your MT5 account password

### Monitoring Settings
- `DELAY`: Delay between checks in seconds (default: 0.1)

## Project Structure

```
mt5-trading-monitor/
├── mt5_monitor.py          # Main monitoring script
├── email_templates.py      # HTML email template functions
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Email Templates

The system uses professional HTML email templates with:
- Responsive design
- Color-coded headers (green for opens, red for closes)
- Structured tables for trade information
- Account balance and equity information
- Timestamps for all events

## Security Notes

- **Never commit your `.env` file** - it contains sensitive credentials
- Use app-specific passwords for email accounts when possible
- Keep your MT5 credentials secure
- The `.env` file is automatically ignored by git

## Troubleshooting

### MT5 Connection Issues
- Ensure MT5 terminal is installed and accessible
- Verify account credentials are correct
- Check that the MT5 path in `.env` is correct

### Email Not Sending
- Verify SMTP credentials are correct
- Check firewall settings for SMTP port
- Ensure sender email allows "less secure apps" or use app password

### No Notifications
- Check that MT5 account has active positions/orders
- Verify internet connection is stable
- Check console output for error messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided for educational and monitoring purposes only. Trading involves risk, and you should always do your own research before making trading decisions. The authors are not responsible for any financial losses.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
