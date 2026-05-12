import flet as ft
from state import session
from services import auth

def build(page: ft.Page) -> ft.View:
    user = session.user  # already populated by auth.login()

    async def on_logout(_):
        auth.logout()
        await page.push_route("/login")

    return ft.View(
        route="/dashboard",
        controls=[
            ft.AppBar(title=ft.Text("Dashboard"), center_title=True),
            ft.Text(f"Welcome, {user.get('first_name', '-')}!", size=24),
            ft.Divider(),
            ft.Text(f"User Name: {user.get('first_name', '-')} {user.get('last_name', '-')}"),
            ft.Text(f"Created at: {user.get('created_at', '-')}"),
            # add more fields as your API returns them
            ft.Button("Logout", on_click=on_logout),

        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )






