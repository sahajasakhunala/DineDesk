import sys
import logging
from sqlalchemy import text
from app.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
            sys.exit(0)
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_connection()
