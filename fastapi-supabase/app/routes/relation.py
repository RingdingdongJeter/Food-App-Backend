# app/routes/relationships.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from app.core.auth import get_current_user
from app.core.supabase_client import get_admin_client

router = APIRouter(prefix="/friends", tags=["friends"])
TABLE = "relationships"

class RequestBody(BaseModel):
    user_id: str = Field(..., description="對方的 user_id (UUID)")

# --- 共用：用「無序」條件抓現有關係 ---
def find_pair(sb, a: str, b: str):
    cond = (
        f"and(user_id.eq.{a},friend_id.eq.{b}),"
        f"and(user_id.eq.{b},friend_id.eq.{a})"
    )
    res = (
        sb.table("relationships")
          .select("*")
          .or_(cond)     # supabase-py 會幫你包 or=
          .limit(1)
          .execute()
    )
    data = res.data or []
    return data[0] if data else None



# 1) 送出好友請求（只靠邏輯）
@router.post("/request")
def request_friend(body: RequestBody, current_user: dict = Depends(get_current_user)):
    me, other = current_user["id"], body.user_id
    if me == other:
        raise HTTPException(status_code=400, detail="Cannot befriend yourself")

    sb = get_admin_client()
    existing = find_pair(sb, me, other)

    if existing:
        status = existing["status"]
        req_by = existing.get("requested_by")
        # 已是好友
        if status == "accepted":
            raise HTTPException(status_code=409, detail="Already friends")
        # 已有待處理請求
        if status == "pending":
            if req_by == me:
                raise HTTPException(status_code=409, detail="Request already sent")
            else:
                # 對方先發的；你也可以選擇在這裡直接自動接受，或維持 pending 交由 /accept 處理
                return {"status": "pending", "requested_by": req_by, "pair_id": existing["id"]}
        # 被封鎖/其他狀態：此處給出通用訊息（如需細化可自行分流）
        if status == "blocked":
            raise HTTPException(status_code=403, detail="Blocked")

    # 沒有既有關係 → 插入一筆（誰在左誰在右不重要）
    row = {
        "user_id": me,
        "friend_id": other,
        "requested_by": me,
        "status": "pending",
        # 若你用 BIGINT(ms) 的 created_at/updated_at，請在這裡覆寫為伺服器毫秒
    }
    sb.table(TABLE).insert(row).execute()
    return {"status": "pending"}

# 2) 接受好友
@router.post("/accept")
def accept_friend(body: RequestBody, current_user: dict = Depends(get_current_user)):
    me, other = current_user["id"], body.user_id
    sb = get_admin_client()
    existing = find_pair(sb, me, other)

    if not existing or existing["status"] != "pending":
        raise HTTPException(status_code=404, detail="No pending request")

    # 合法接受條件：必須「存在 pending」，且 pending 可以是任一方發起
    updated = (
        sb.table(TABLE)
          .update({"status": "accepted"})
          .eq("id", existing["id"])
          .execute()
          .data
    )

    if not updated:
        raise HTTPException(status_code=409, detail="Accept failed")
    return {"status": "accepted"}

# 3) 拒絕/取消（刪掉 pending）
@router.post("/reject")
def reject_friend(body: RequestBody, current_user: dict = Depends(get_current_user)):
    me, other = current_user["id"], body.user_id
    sb = get_admin_client()
    existing = find_pair(sb, me, other)

    if not existing or existing["status"] != "pending":
        raise HTTPException(status_code=404, detail="No pending request to reject/cancel")

    # 允許任一方取消/拒絕 pending
    sb.table(TABLE).delete().eq("id", existing["id"]).execute()
    return {"status": "rejected"}

# 4) 解除好友（只在 accepted 才能移除）
@router.delete("/{other_user_id}")
def unfriend(other_user_id: str, current_user: dict = Depends(get_current_user)):
    me = current_user["id"]
    sb = get_admin_client()
    existing = find_pair(sb, me, other_user_id)

    if not existing or existing["status"] != "accepted":
        raise HTTPException(status_code=404, detail="Not friends")

    sb.table(TABLE).delete().eq("id", existing["id"]).execute()
    return {"status": "removed"}

# 5) 列出好友（accepted）
@router.get("")
def list_friends(current_user: dict = Depends(get_current_user)):
    me = current_user["id"]
    sb = get_admin_client()

    rows = (
        sb.table(TABLE)
          .select("id,user_id,friend_id,status,requested_by,updated_at,created_at")
          .eq("status", "accepted")
          .or_(f"user_id.eq.{me},friend_id.eq.{me}")
          .order("updated_at", desc=True)
          .execute()
          .data
        or []
    )

    friends: List[Dict[str, Any]] = []
    for r in rows:
        other = r["friend_id"] if r["user_id"] == me else r["user_id"]
        friends.append({
            "relationship_id": r["id"],
            "user_id": other,
            "since": r.get("updated_at") or r.get("created_at"),
        })
    return {"friends": friends}

# 6) 列出 pending（我發出 / 我收到）
@router.get("/requests")
def list_requests(current_user: dict = Depends(get_current_user)):
    me = current_user["id"]
    sb = get_admin_client()

    rows = (
        sb.table(TABLE)
          .select("id,user_id,friend_id,status,requested_by,created_at")
          .eq("status", "pending")
          .or_(f"user_id.eq.{me},friend_id.eq.{me}")
          .order("created_at", desc=True)
          .execute()
          .data
        or []
    )

    outgoing, incoming = [], []
    for r in rows:
        other = r["friend_id"] if r["user_id"] == me else r["user_id"]
        if r["requested_by"] == me:
            outgoing.append({"relationship_id": r["id"], "user_id": other, "requested_at": r["created_at"]})
        else:
            incoming.append({"relationship_id": r["id"], "user_id": other, "requested_at": r["created_at"]})
    return {"outgoing": outgoing, "incoming": incoming}
