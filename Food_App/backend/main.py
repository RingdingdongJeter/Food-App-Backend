import os
from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import engine, Base, get_db
from models import Record
from schemas import RecordCreate, RecordOut

app = FastAPI(title="FastAPI Starter")

# CORS
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 先快速可用：啟動時建立表（之後上 Alembic 就把這段拿掉）
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/records", response_model=RecordOut)
async def create_record(record: RecordCreate, db: AsyncSession = Depends(get_db)):
    new_record = Record(**record.dict())
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    return new_record


# 讀取所有紀錄
@app.get("/records", response_model=list[RecordOut])
async def get_records(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Record))
    records = result.scalars().all()
    return records


# 讀取單筆紀錄
@app.get("/records/{record_id}", response_model=RecordOut)
async def get_record(record_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Record).where(Record.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


# 更新紀錄
@app.put("/records/{record_id}", response_model=RecordOut)
async def update_record(record_id: UUID, updated: RecordCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Record).where(Record.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    for key, value in updated.dict().items():
        setattr(record, key, value)

    await db.commit()
    await db.refresh(record)
    return record


# 刪除紀錄
@app.delete("/records/{record_id}")
async def delete_record(record_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Record).where(Record.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    await db.delete(record)
    await db.commit()
    return {"status": "deleted", "id": str(record_id)}