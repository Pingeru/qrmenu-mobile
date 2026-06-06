import flet as ft
from services import auth


def build_bottom_bar(page: ft.Page):
    """
    Build a collapsible side panel with hamburger menu at the top.
    Shows/hides the sidebar options when hamburger icon is clicked.
    """
    panel_visible = [False]  # Track panel visibility state

    async def on_profile_click(e):
        await page.push_route("/dashboard")

    async def on_menu_click(e):
        await page.push_route("/menu")

    async def on_logout_click(e):
        auth.logout()
        await page.push_route("/login")

    # lets build bottom app bar
    bottom_appbar = ft.BottomAppBar(
        bgcolor=ft.Colors.BLUE,
        shape=ft.CircularRectangleNotchShape(),
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.FOOD_BANK, icon_color=ft.Colors.WHITE, on_click=on_menu_click),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.PERSON, icon_color=ft.Colors.WHITE, on_click=on_profile_click),
                ft.IconButton(icon=ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE, on_click=on_logout_click),
            ],
        ),
        height=60,
        align=ft.Alignment.BOTTOM_CENTER,
    )

    return bottom_appbar
    