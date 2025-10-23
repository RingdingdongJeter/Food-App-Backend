from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.core.supabase_client import get_public_client, get_admin_client

router = APIRouter(prefix="/auth", tags=["auth"])

# ----------- Schemas -----------
class RegisterBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: Optional[str] = None   # 會放到 user_metadata
    phone: Optional[str] = None

class LoginBody(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

# ----------- Helpers -----------
def _safe_err(e: Exception) -> str:
    # Supabase 例外訊息有時是字典/物件，這裡做安全字串化
    return getattr(e, "message", None) or str(e)

# ----------- Routes -----------

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterBody, confirm_immediately: bool = False):
    """
    伺服器代客註冊。
    - 預設：用 anon key 呼叫 sign_up()，走 Email 驗證流程（回傳可能沒有 session，視專案設定）
    - confirm_immediately=True：用 service_role 直接建立並標記 email_confirmed（不經 Email）
    回傳 TokenResponse：若無 session，access_token 會是空字串。
    """
    try:
        if confirm_immediately:
            # 以 admin 權限直接建立帳號並標記已驗證
            admin = get_admin_client()
            res = admin.auth.admin.create_user({
                "email": body.email,
                "password": body.password,
                "email_confirm": True,
                "user_metadata": {
                    "display_name": body.display_name,
                    "phone": body.phone,
                },
            })
            # admin.create_user 不會自動登入，沒有 session
            return TokenResponse(access_token="")  # 前端需再打 /auth/login

        # 走一般註冊流程（是否自動回 session 取決於專案「Email confirmations」設定）
        pub = get_public_client()
        res = pub.auth.sign_up({
            "email": body.email,
            "password": body.password,
            "options": {
                "data": {
                    "display_name": body.display_name,
                    "phone": body.phone,
                }
            }
        })
        session = res.session
        if session:
            return TokenResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
            )
        # 沒有 session：多半是需要 Email 驗證
        return TokenResponse(access_token="")
    except Exception as e:
        msg = _safe_err(e)
        if "User already registered" in msg or "already registered" in msg or "duplicate" in msg:
            raise HTTPException(status_code=409, detail="Email already registered")
        raise HTTPException(status_code=500, detail=f"Supabase error: {msg}")

@router.post("/login", response_model=TokenResponse)
def login(body: LoginBody):
    """
    伺服器代客登入：向 Supabase Auth 換取 access_token / refresh_token。
    """
    try:
        pub = get_public_client()
        res = pub.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password,
        })
        if not res.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return TokenResponse(
            access_token=res.session.access_token,
            refresh_token=res.session.refresh_token,
        )
    except Exception as e:
        msg = _safe_err(e)
        # Supabase 一律回 error，這裡轉成 401
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/_env_ok")
def env_ok():
    from app.core.config import settings
    return {
        "has_url": bool(settings.SUPABASE_URL),
        "has_anon": bool(settings.SUPABASE_ANON_KEY),
        "has_service": bool(settings.SUPABASE_SERVICE_ROLE_KEY),
        "has_jwt_secret": bool(settings.SUPABASE_JWT_SECRET),
    }
    