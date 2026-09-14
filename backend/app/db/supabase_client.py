"""
ATHLETIX — Database Client (Supabase Service Role Connection)
backend/app/db/supabase_client.py

Provides server-side database connectivity via the official Supabase Python client.

Working & Architecture:
- Uses the high-privilege SERVICE_ROLE_KEY to perform administrative, cross-table queries,
  verification checks, and background batch jobs without Row Level Security (RLS) constraints.
- Crucial Security Rule: The Service Role Key is strictly confined to the backend server
  and must never be bundled into the mobile or web client builds.
"""

from functools import lru_cache

# pyrefly: ignore [missing-import]
from supabase import Client, create_client

from app.core.config import settings


@lru_cache()
def get_supabase_client() -> Client:
    """
    Initializes and returns a cached singleton Supabase client configured with the service role key.
    """
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY,
    )
