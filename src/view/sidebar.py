import flet as ft
from services import auth


def build_sidebar(page: ft.Page) -> ft.Row:
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

    # Hamburger menu button (always visible at the top)
    hamburger_button = ft.IconButton(
        icon=ft.Icons.MENU,
        icon_size=28,
        tooltip="Menu",
        style=ft.ButtonStyle(
            color={
                ft.ControlState.DEFAULT: ft.Colors.WHITE,
                ft.ControlState.HOVERED: ft.Colors.CYAN,
            }
        ),
    )

    # Navigation options (shown/hidden based on panel state)
    navigation_panel = ft.Column(
        expand=True,
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # Top spacing
            ft.Container(height=20),
            # Profile button
            ft.IconButton(
                icon=ft.Icons.PERSON,
                icon_size=32,
                tooltip="Profile",
                on_click=on_profile_click,
                style=ft.ButtonStyle(
                    color={
                        ft.ControlState.DEFAULT: ft.Colors.WHITE,
                        ft.ControlState.HOVERED: ft.Colors.CYAN,
                    }
                ),
            ),
            ft.Text("Profile", color=ft.Colors.WHITE, size=12),
            ft.Divider(height=1, color=ft.Colors.BLUE_GREY_700),
            # Menu button
            ft.IconButton(
                icon=ft.Icons.RESTAURANT_MENU,
                icon_size=32,
                tooltip="Menu",
                on_click=on_menu_click,
                style=ft.ButtonStyle(
                    color={
                        ft.ControlState.DEFAULT: ft.Colors.WHITE,
                        ft.ControlState.HOVERED: ft.Colors.CYAN,
                    }
                ),
            ),
            ft.Text("Menu", color=ft.Colors.WHITE, size=12),
            ft.Divider(height=1, color=ft.Colors.BLUE_GREY_700),
            # Spacer to push logout to bottom
            ft.Container(expand=True),
            # Logout button
            ft.IconButton(
                icon=ft.Icons.LOGOUT,
                icon_size=32,
                tooltip="Logout",
                on_click=on_logout_click,
                style=ft.ButtonStyle(
                    color={
                        ft.ControlState.DEFAULT: ft.Colors.WHITE,
                        ft.ControlState.HOVERED: ft.Colors.RED,
                    }
                ),
            ),
            ft.Text("Logout", color=ft.Colors.WHITE, size=12),
            # Bottom spacing
            ft.Container(height=20),
        ],
    )

    # Navigation panel container (initially hidden)
    nav_container = ft.Container(
        width=200,
        bgcolor=ft.Colors.BLUE_GREY_900,
        content=navigation_panel,
        visible=False,
    )

    def toggle_sidebar(e):
        panel_visible[0] = not panel_visible[0]
        hamburger_button.icon = ft.Icons.CLOSE if panel_visible[0] else ft.Icons.MENU
        nav_container.visible = panel_visible[0]
        page.update()

    hamburger_button.on_click = toggle_sidebar

    # Hamburger container (always visible)
    hamburger_container = ft.Container(
        width=60,
        bgcolor=ft.Colors.BLUE_GREY_900,
        content=hamburger_button,
        alignment=ft.Alignment.TOP_CENTER,
    )

    # Return the combined sidebar with hamburger and expandable panel
    return ft.Row(
        spacing=0,
        controls=[
            hamburger_container,
            nav_container,
        ],
    )
