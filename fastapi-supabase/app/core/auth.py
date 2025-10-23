from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Security
from jose import jwt, JWTError
from app.core.config import settings

#bearer_scheme = HTTPBearer(auto_error=False)
bearer_scheme = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    if not creds or not creds.credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = creds.credentials.strip()
    # 有人會在 Swagger Authorize 貼入 "Bearer xxx"；這裡幫忙剝掉一次
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.SUPABASE_JWT_ALG],
            options={"verify_aud": False},  # Supabase token 有 aud，但我們不驗 aud
        )
        uid = payload.get("sub")
        if not uid:
            raise HTTPException(status_code=401, detail="Invalid token (no sub)")
        email = (payload.get("email")
                 or (payload.get("user_metadata") or {}).get("email"))
        return {"id": uid, "email": email, "token": token}
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
