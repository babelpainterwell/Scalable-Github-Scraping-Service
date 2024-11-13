import logging
from datetime import datetime

log_filename = f"app_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(), 
        logging.FileHandler(log_filename)
    ]
)