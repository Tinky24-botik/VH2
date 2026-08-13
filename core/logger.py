import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("voicehelper")
logger.setLevel(logging.INFO)

handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_DIR, "voicehelper.log"),
    when="midnight",
    backupCount=7,
    encoding="utf-8",
)

handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
)

logger.addHandler(handler)