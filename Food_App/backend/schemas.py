import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecordCreate(BaseModel):
    id: Optional[str] = None
    remote_id: Optional[str] = None
    user_id: str
    title: Optional[str]
    local_uri: Optional[str]
    remote_uri: Optional[str]
    calories: Optional[float]
    protein: Optional[float]
    fat: Optional[float]
    carbohydrate: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    city: Optional[str]
    district: Optional[str]
    taken_at: Optional[str]
    sync_state: Optional[str]
    deleted: Optional[bool]


class RecordOut(BaseModel):
    id: uuid.UUID
    remote_id: Optional[str]
    user_id: str
    title: Optional[str]
    local_uri: Optional[str]
    remote_uri: Optional[str]
    calories: Optional[float]
    protein: Optional[float]
    fat: Optional[float]
    carbohydrate: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    city: Optional[str]
    district: Optional[str]
    taken_at: Optional[str]
    sync_state: Optional[str]
    deleted: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
