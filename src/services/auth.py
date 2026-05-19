import httpx
from state import session

API_BASE = "https://qrmenu.dovanay.com/api/v1"  # Change to your actual backend URL

async def login(email: str, password: str) -> str | None:
    """
    Returns None on success (token saved to session),
    or an error message string on failure.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE}/client/auth/login", json={
                "email": email,
                "password": password,
            })

        if response.status_code == 200:
            data = response.json()
            session.token = data["access_token"]   # store JWT
            session.refresh_token = data.get("refresh_token")  # store refresh token
            session.user = data["user"]             # store user info
            return None                             # success
        elif response.status_code == 401:
            return "Invalid email or password."
        else:
            return "Something went wrong. Please try again."

    except httpx.ConnectError:
        return "Cannot reach server. Check your connection."


async def register(
    first_name: str,
    last_name: str,
    phone: str,
    email: str,
    password: str,
) -> str | None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE}/client/auth/register", json={
                "first_name": first_name,
                "last_name":  last_name,
                "phone_number": phone,
                "email": email,
                "password": password,
            })

        if response.status_code == 201:
            return None
        elif response.status_code == 409:
            return "An account with this email already exists."
        elif response.status_code == 404:
            return "Registration endpoint not found. Check your backend URL."
        elif response.status_code == 400:
            return "Missing or invalid fields. Please check your input."
        else:
            return "Something went wrong. Please try again."

    except httpx.RequestError:
        return "Cannot reach server. Check your connection."


async def refresh() -> str | None:
    """
    Refresh the access token using the refresh token.
    Returns None on success (token updated in session),
    or an error message string on failure.
    """
    if not session.refresh_token:
        return "No refresh token available."
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE}/client/auth/refresh", json={
                "refresh_token": session.refresh_token,
            })

        if response.status_code == 200:
            data = response.json()
            session.token = data["access_token"]   # update JWT
            return None                             # success
        elif response.status_code == 401:
            return "Refresh token expired. Please log in again."
        else:
            return "Failed to refresh token. Please try again."

    except httpx.RequestError:
        return "Cannot reach server. Check your connection."


async def delete_account() -> str | None:
    if not session.token:
        return "Not authenticated."

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{API_BASE}/client/auth/delete",
                headers={"Authorization": f"Bearer {session.token}"}
            )

        if response.status_code == 200:
            logout()  # Clear session on successful deletion
            return None
        elif response.status_code == 401:
            return "Unauthorized. Please log in again."
        elif response.status_code == 403:
            return "Forbidden. You do not have permission to delete this account."
        elif response.status_code == 404:
            return "User not found."
        else:
            return "Failed to delete account. Please try again."

    except httpx.RequestError:
        return "Cannot reach server. Check your connection."


async def update_profile(
    first_name: str,
    last_name: str,
    phone: str,
    email: str,
    password: str | None = None,
) -> str | None:
    if not session.token:
        return "Not authenticated."

    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone,
        "email": email,
    }
    if password is not None:
        payload["password"] = password

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_BASE}/client/auth/edit",
                headers={"Authorization": f"Bearer {session.token}"},
                json=payload,
            )

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and data.get("user"):
                session.user = data["user"]
            else:
                session.user = {
                    **session.user,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone_number": phone,
                }
            return None
        elif response.status_code == 400:
            return "Invalid input data."
        elif response.status_code == 401:
            return "Unauthorized. Please log in again."
        elif response.status_code == 409:
            return "Email already in use."
        else:
            return "Failed to update profile. Please try again."

    except httpx.RequestError:
        return "Cannot reach server. Check your connection."


def logout():
    session.token = None
    session.refresh_token = None
    session.user = None