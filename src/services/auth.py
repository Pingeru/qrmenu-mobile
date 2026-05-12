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


def logout():
    session.token = None
    session.user = None