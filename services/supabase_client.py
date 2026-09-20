"""Supabase wrapper. Not wired into the flow yet — MVP has no persistence.
Add a call to log_request() from graph/nodes.py once you need history/credits."""
from supabase import create_client
import config

_client = None


def get_client():
    global _client
    if _client is None:
        _client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    return _client


def log_request(user_id: int, product_name: str, category: str) -> None:
    get_client().table("requests").insert(
        {"user_id": user_id, "product_name": product_name, "category": category}
    ).execute()
