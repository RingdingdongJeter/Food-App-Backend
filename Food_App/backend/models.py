from sqlalchemy import Column, String, Float, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from db import Base
import uuid

class Record(Base):
    __tablename__ = "records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    remote_id = Column(String, nullable=True)
    user_id = Column(String, index=True)
    title = Column(String)
    local_uri = Column(String, nullable=True)
    remote_uri = Column(String, nullable=True)
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbohydrate = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String)
    district = Column(String)
    taken_at = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    sync_state = Column(String, nullable=True)
    deleted = Column(Boolean, default=False)
