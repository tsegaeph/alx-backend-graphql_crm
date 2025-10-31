#!/usr/bin/env python3
import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
log_file = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

try:
    # Set up GraphQL client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Define GraphQL query
    query = gql("""
        query GetRecentOrders {
            allOrders {
                id
                orderDate
                customer {
                    email
                }
            }
        }
    """)

    # Execute query
    response = client.execute(query)

    # Filter orders within the last 7 days
    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(days=7)

    for order in response.get("allOrders", []):
        order_date = datetime.datetime.fromisoformat(order["orderDate"])
        if order_date >= seven_days_ago:
            customer_email = order["customer"]["email"]
            logging.info(f"Reminder: Order {order['id']} for {customer_email}")

    print("Order reminders processed!")

except Exception as e:
    print(f"Error occurred: {e}")
    logging.error(f"Error: {e}")
