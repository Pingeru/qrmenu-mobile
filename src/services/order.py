import httpx
from services.auth import API_BASE
from state import session


async def create_order(business_id: str, items: list[dict]) -> tuple[dict | None, str | None]:
    """
    Create an order for the authenticated client.

    Args:
        business_id: The business to place the order for.
        items: List of {"product_id": str, "quantity": int} dicts.

    Returns:
        (order_data, None)  on success (HTTP 201)
        (None, error_msg)   on failure
    """
    if not session.token:
        return None, "You must be logged in to place an order."

    payload = {
        "business_id": business_id,
        "items": items,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/client/orders",
                headers={"Authorization": f"Bearer {session.token}"},
                json=payload,
                timeout=15,
            )
    except httpx.RequestError:
        return None, "Cannot reach server. Check your connection."

    if response.status_code == 201:
        return response.json().get("order"), None
    elif response.status_code == 400:
        return None, "Invalid order data. Please check your items."
    elif response.status_code == 401:
        return None, "Session expired. Please log in again."
    elif response.status_code == 404:
        return None, "One or more products were not found."
    else:
        try:
            detail = response.json().get("detail", "")
        except Exception:
            detail = ""
        return None, f"Failed to place order. {detail}".strip()


async def get_orders() -> tuple[list[dict] | None, str | None]:
    """
    Fetch all orders for the authenticated client.

    Returns:
        (orders_list, None)  on success
        (None, error_msg)    on failure
    """
    if not session.token:
        return None, "You must be logged in to view orders."

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/client/orders",
                headers={"Authorization": f"Bearer {session.token}"},
                timeout=15,
            )
    except httpx.RequestError:
        return None, "Cannot reach server. Check your connection."

    if response.status_code == 200:
        data = response.json()
        # Backend returns {"orders": [...]} - extract the list
        orders = data.get("orders", []) if isinstance(data, dict) else data
        return orders, None
    elif response.status_code == 401:
        return None, "Session expired. Please log in again."
    else:
        try:
            detail = response.json().get("detail", "")
        except Exception:
            detail = ""
        return None, f"Failed to load orders. {detail}".strip()


async def cancel_order(order_id: str) -> tuple[bool, str | None]:
    """
    Cancel (soft-delete) an order owned by the authenticated client.
    Server sets status to 'cancelled'; the order is not hard-deleted.

    Args:
        order_id: The _id of the order to cancel.

    Returns:
        (True, None)       on success
        (False, error_msg) on failure
    """
    if not session.token:
        return False, "You must be logged in to cancel an order."

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{API_BASE}/client/orders/{order_id}",
                headers={"Authorization": f"Bearer {session.token}"},
                timeout=15,
            )
    except httpx.RequestError:
        return False, "Cannot reach server. Check your connection."

    if response.status_code == 200:
        return True, None
    elif response.status_code == 401:
        return False, "Session expired. Please log in again."
    elif response.status_code == 403:
        return False, "You can only cancel your own orders."
    elif response.status_code == 404:
        return False, "Order not found."
    elif response.status_code == 409:
        return False, "Only placed orders can be cancelled."
    else:
        try:
            detail = response.json().get("detail", "")
        except Exception:
            detail = ""
        return False, f"Failed to cancel order. {detail}".strip()
