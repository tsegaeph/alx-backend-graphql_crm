# CRM Celery and Redis Setup Guide

## 1. Install Dependencies
Make sure the following are installed and listed in `requirements.txt`:

- celery  
- django-celery-beat  
- redis  
- requests  

# Install dependencies
# bash
pip install -r requirements.txt

---

## 2. Install and Start Redis
Redis is required as the Celery message broker.

### On Ubuntu:

# bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

### Verify Redis is running:

# bash
redis-cli ping
# Should return "PONG"

---

## 3. Run Django Migrations
# bash
python manage.py migrate

---

## 4. Start Celery Worker
# bash
celery -A crm worker -l info

---

## 5. Start Celery Beat
# bash
celery -A crm beat -l info

---

## 6. Verify CRM Report Generation
After setup, Celery Beat will automatically generate a CRM report every Monday at 6:00 AM.

Logs are stored in:

```
/tmp/crm_report_log.txt
```

Each log line will look like:

```
2025-10-30 06:00:00 - Report: 10 customers, 20 orders, 5600.0 revenue
```

---

✅ **Done!**

Your Celery and Redis setup is complete, and weekly CRM reports will be generated automatically.
