import logging
import sys
from app.config import settings
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s %(method)s %(path)s %(status_code)s %(latency_ms)s',
        rename_fields={"levelname": "level", "asctime": "timestamp"}
    )
    handler.setFormatter(formatter)
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(handler)
