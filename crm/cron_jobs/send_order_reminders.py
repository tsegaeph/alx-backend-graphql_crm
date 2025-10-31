#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta

GRAPHQL_URL = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

# Calculate date range for the last 7 days
today = datetime.now()
seven_days_ago = today - timedelta(days=7)

# GraphQL query to fetch recent pending orders
query = """
{
  allOrders {
    id
    customer {
      email
    }
    orderDate
    status
  }
}
"""

try:
    response = requests.post(GRAPHQL_URL, json={'query': query})
    response.raise_for_status()
    data = response.json()

    if "data" not in data or "allOrders" not in data["data"]:
        raise ValueError("Invalid GraphQL response")

    orders = data["data"]["allOrders"]
    recent_orders = [
        o for o in orders
        if o.get("status") == "PENDING"
        and datetime.fromisoformat(o["orderDate"]) >= seven_days_ago
    ]

    # Write reminders to log file
    with open(LOG_FILE, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for order in recent_orders:
            f.write(f"{timestamp} - Reminder: Order {order['id']} for {order['customer']['email']}\n")

    print("Order reminders processed!")

except Exception as e:
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - Error: {e}\n")
    print(f"Error occurred: {e}")
