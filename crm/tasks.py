import requests
from datetime import datetime
from celery import shared_task

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

@shared_task
def generate_crm_report():
    query = """
    query {
        allCustomers {
            id
        }
        allOrders {
            totalAmount
        }
    }
    """

    try:
        response = requests.post(GRAPHQL_ENDPOINT, json={'query': query})
        data = response.json().get('data', {})

        total_customers = len(data.get('allCustomers', []))
        orders = data.get('allOrders', [])
        total_orders = len(orders)
        total_revenue = sum(order.get('totalAmount', 0) for order in orders)

        log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"

        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(log_message)

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error: {e}\n")

    print("CRM report generated!")
