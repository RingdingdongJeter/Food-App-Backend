from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone

from app.core.auth import get_current_user
from app.core.supabase_client import get_user_client

router = APIRouter()

@router.post("/sync/pull")
async def pull_changes(last_pulled_at: int | None = None, current_user: dict = Depends(get_current_user)):
    try:
        sb = get_user_client(current_user["token"])
        data = (
            sb.table("records")
              .select("*")
              .eq("user_id", current_user["id"])      # 應用層再保險一次
              .gt("updated_at", last_pulled_at or 0)
              .execute()
              .data
        )
        timestamp = int(datetime.now().timestamp() * 1000)
        return {"data": data, "timestamp": timestamp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/push")
async def push_changes(payload: dict, current_user: dict = Depends(get_current_user)):
    try:
        sb = get_user_client(current_user["token"])

        created = payload.get("created", [])
        updated = payload.get("updated", [])
        deleted = payload.get("deleted", [])

        for r in created:
            r["user_id"] = current_user["id"]
        for r in updated:
            r["user_id"] = current_user["id"]

        if created or updated:
            sb.table("records").upsert(created + updated).execute()

        if deleted:
            sb.table("records").update({"deleted": True}).in_("local_id", deleted).execute()

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
