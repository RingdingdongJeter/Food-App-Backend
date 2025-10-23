from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if not creds:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = creds.credentials
    try:
        payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=[settings.SUPABASE_JWT_ALG])
        uid = payload.get("sub")
        if not uid:
            raise HTTPException(status_code=401, detail="Invalid token")
        email = payload.get("email") or payload.get("user_metadata", {}).get("email")
        return {"id": uid, "email": email, "token": token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
