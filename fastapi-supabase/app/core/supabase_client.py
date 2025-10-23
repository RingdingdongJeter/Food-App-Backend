from supabase import create_client, Client
from app.core.config import settings


def get_public_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

def get_admin_client() -> Client:
    # service role：後端專用，可做管理動作（繞過 RLS）
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def get_user_client(user_jwt: str) -> Client:
    # 用使用者 token 讓 PostgREST 以該身分執行（RLS 生效）
    c = get_public_client()
    c.postgrest.auth(user_jwt)
    return c
