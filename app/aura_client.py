# app/aura_client.py
import time, uuid
from app.logger import logger

class AuraClient:
    def __init__(self):
        self._token = None

    def login(self):
        time.sleep(0.3)  # simulate latency
        self._token = "sim-token"
        logger.info("Simulated Aura login")

    def create_quote(self, payload):
        """
        Simulate quote creation. Returns dict with id, premium, etc.
        """
        time.sleep(0.5)
        emp = int(payload.get("employee_count", 0) or 0)
        premium = 1000 + emp * 10
        resp = {
            "id": str(uuid.uuid4()),
            "client_name": payload.get("client_name"),
            "employee_count": emp,
            "insurance_type": payload.get("insurance_type"),
            "premium": premium,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        logger.info(f"Simulated Aura quote {resp['id']} premium={premium}")
        return resp
