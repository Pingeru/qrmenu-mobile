import httpx

from state import session
from services.auth import API_BASE


async def fetch_categories() -> dict[str, list[dict]]:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_BASE}/business/categories", timeout=10)
    except httpx.RequestError:
        return {}

    if resp.status_code == 200:
        data = resp.json()
        return data.get("categories", {}) if isinstance(data, dict) else {}

    return {}


async def fetch_products_for_category(category_id: str) -> dict[str, list[dict]]:
    url = f"{API_BASE}/business/products?category_id={category_id}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
    except httpx.RequestError:
        return {}

    if resp.status_code != 200:
        return {}

    try:
        data = resp.json()
    except ValueError:
        return {}

    if isinstance(data, dict) and isinstance(data.get("products"), list):
        return data.get("products")

    return {}
