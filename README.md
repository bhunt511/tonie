# Ms Rachel Tonie Stock Watcher

A Python script that monitors the availability of the Ms Rachel Tonie on the Tonies US website and sends alerts when it comes back in stock.

## Features

- Polls the Tonies product JSON every 5 minutes
- Sends immediate SMS alerts via IFTTT when the variant flips to IN STOCK
- Sends daily 7 PM Eastern summary SMS with check statistics
- All messages include the product URL
- Comprehensive logging to `tonie_watch.log`

## Requirements

- Python 3.8+
- `requests`
- `python-dotenv`
- `backports.zoneinfo` (if using Python 3.8)

## Setup

1. Install dependencies:
   ```bash
   pip install requests python-dotenv
   # For Python 3.8 only:
   pip install backports.zoneinfo
   ```

2. Create a `.env` file with your IFTTT webhook configuration:
   ```
   IFTTT_WEBHOOK_KEY=your_webhook_key_here
   IFTTT_EVENT_NAME=tonie_alert
   ```

3. Set up IFTTT webhook to receive notifications (SMS, email, etc.)

## Usage

### Normal Operation
```bash
python3 tonies_watch.py
```

### Test Mode
Send a simulated in-stock alert immediately and exit:
```bash
python3 tonies_watch.py --test
# or
python3 tonies_watch.py -t
```

### Stock Check Test
Check current stock status without sending alerts or waiting:
```bash
python3 tonies_watch.py --stock-test
# or
python3 tonies_watch.py -s
```

## Configuration

The script is currently configured to monitor:
- **Product**: Ms Rachel Tonie
- **Variant ID**: 45452782502039
- **URL**: https://us.tonies.com/products/ms-rachel-tonie
- **Check Interval**: 5 minutes
- **Daily Summary**: 7 PM Eastern Time

To monitor a different product, update the `VARIANT_ID` and `URL` constants in the script.

## Logging

All activity is logged to `tonie_watch.log` with timestamps, including:
- Stock check results
- Notification attempts (success/failure)
- Error conditions

## How It Works

1. The script fetches the product's JSON data from the Tonies website
2. It checks the `available` status of the specific variant
3. When status changes from out-of-stock to in-stock, it triggers an IFTTT webhook
4. Daily summaries are sent at 7 PM Eastern with total checks and in-stock occurrences
5. All notifications include the direct product URL for quick purchasing