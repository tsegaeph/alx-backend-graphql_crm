import datetime
import requests

def log_crm_heartbeat():
    """
    Logs a timestamped heartbeat message every 5 minutes.
    Optionally pings the GraphQL endpoint for health verification.
    """
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    # Optional: check GraphQL endpoint health
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200:
            log_message = f"{timestamp} CRM is alive and GraphQL responded OK\n"
        else:
            log_message = f"{timestamp} CRM heartbeat - GraphQL ERROR {response.status_code}\n"
    except Exception as e:
        log_message = f"{timestamp} CRM heartbeat failed: {e}\n"

    # Append to heartbeat log
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message)
