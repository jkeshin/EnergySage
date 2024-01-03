from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

DATABASE_URL = "mysql+pymysql://root:Mysql12345@localhost:3306/energysage_takehome" # Local testing
# DATABASE_URL = "mysql+pymysql://root:Mysql12345@host.docker.internal:3306/energysage_takehome" # Docker Deployment URL to interact with local DB


# SQLAlchemy models
Base = declarative_base()

# Create the database tables
engine = create_engine(DATABASE_URL)

# Dependency to get the database session
def get_db():
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


TEST_DATABASE_URL = "sqlite:///./test.db"  # SQLite database file path

# Dependency to get the database session
def get_test_db():
    testEngine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=testEngine)

    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=testEngine)
    db = TestSessionLocal()
    try:
        return db
    finally:
        db.close()