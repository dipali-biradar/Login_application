# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.logger import logger

DATABASE_URL = "postgresql://postgres:Admin%40123@localhost:5432/Authentication_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    logger.info("Entering get_db()")
    db = SessionLocal()
    try:
        logger.info("Database session created successfully")
        yield db
        logger.info("Exiting get_db()")
    except Exception as e:
        logger.exception("Exception in get_db()")
        raise e
    finally:
        logger.info("Closing database session")
        db.close()

Base = declarative_base()