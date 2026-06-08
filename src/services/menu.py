from typing import Any
import httpx
from services.auth import API_BASE


async def fetch_categories(business_id: str) -> list[dict[str, Any]]:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_BASE}/business/categories", timeout=10)
    except httpx.RequestError:
        return []

    if resp.status_code == 200:
        data = resp.json()
        # Additional client-side filter for safety
        return [
            category for category in data.get("categories", [])
            if category.get("is_active", True) and category.get("business_id") == business_id
        ]   

    return []


async def fetch_products_for_category(category_id: str) -> list[dict[str, Any]]:
    url = f"{API_BASE}/business/products?category_id={category_id}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
    except httpx.RequestError:
        return []

    if resp.status_code != 200:
        return []

    try:
        data = resp.json()
    except ValueError:
        return []

    if isinstance(data, dict) and isinstance(data.get("products"), list):
        return [product for product in data["products"] if product.get("is_active", True)]

    return []
