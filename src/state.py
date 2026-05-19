class AppState:
    token: str | None = None
    refresh_token: str | None = None
    user: dict | None = None

# Single shared instance imported everywhere
session = AppState()