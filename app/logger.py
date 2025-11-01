# app/logger.py
import logging, sys

def get_logger(name="email_agent"):
    log = logging.getLogger(name)
    if not log.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
        log.addHandler(h)
        log.setLevel(logging.INFO)
    return log

logger = get_logger()
