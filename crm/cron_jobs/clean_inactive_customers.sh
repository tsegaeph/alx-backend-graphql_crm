#!/bin/bash

# Navigate to project directory (update path if needed)
cd "$(dirname "$0")/../.." || exit

# Activate virtual environment if you use one (optional)
# source venv/bin/activate

# Run Django shell command to delete inactive customers
deleted_count=$(python3 manage.py shell <<EOF
from crm.models import Customer
from datetime import timedelta
from django.utils import timezone

one_year_ago = timezone.now() - timedelta(days=365)
deleted, _ = Customer.objects.filter(last_order_date__lt=one_year_ago).delete()
print(deleted)
EOF
)

# Log results with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
