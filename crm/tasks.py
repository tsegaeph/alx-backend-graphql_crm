from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    try:
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            verify=False,
            retries=3,
        )

        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("""
        {
            allCustomers { totalCount }
            allOrders {
                edges { node { totalAmount } }
            }
        }
        """)

        result = client.execute(query)
        total_customers = result.get("allCustomers", {}).get("totalCount", 0)
        orders = result.get("allOrders", {}).get("edges", [])
        total_orders = len(orders)
        total_revenue = sum(o["node"]["totalAmount"] for o in orders if o["node"]["totalAmount"])

        with open("/tmp/crm_report_log.txt", "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n")

        print("CRM weekly report generated successfully!")

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(f"Error occurred: {str(e)}\n")
