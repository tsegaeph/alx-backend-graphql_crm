import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Log CRM heartbeat and optionally query GraphQL hello field"""
    now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{now} CRM is alive"

    # Optional GraphQL check
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql("{ hello }")
        response = client.execute(query)
        message += f" | GraphQL says: {response.get('hello', 'No response')}"
    except Exception as e:
        message += f" | GraphQL check failed: {e}"

    # Append to log
    with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
        log_file.write(message + "\n")

    print(message)


def update_low_stock():
    """Runs the GraphQL mutation to restock low-stock products."""
    now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{now} - Starting low stock update\n"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        mutation = gql("""
        mutation {
            updateLowStockProducts {
                success
                message
                updatedProducts {
                    id
                    name
                    stock
                }
            }
        }
        """)
        
        result = client.execute(mutation)
        data = result.get("updateLowStockProducts", {})
        log_message += f"{data.get('message', 'No message')}\n"

        updated = data.get("updatedProducts", [])
        for p in updated:
            log_message += f"Product: {p['name']}, New stock: {p['stock']}\n"

    except Exception as e:
        log_message += f"Error occurred: {e}\n"

    # Write to log file
    with open("/tmp/low_stock_updates_log.txt", "a") as log:
        log.write(log_message + "\n")

    print(log_message)

