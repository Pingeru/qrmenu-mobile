import flet as ft
from pages import login, menu, register, dashboard, orders, forgot_password
from state import session


async def main(page: ft.Page):
    page.title = "Pingeru"
    ROUTES = {
        "/": login.build,
        "/login": login.build,
        "/register": register.build,
        "/forgot-password": forgot_password.build,  # Assuming forgot password uses the same login page
        "/dashboard": dashboard.build,
        "/menu": menu.build,
        "/orders": orders.build,
    }
    PROTECTED = {"/dashboard", "/menu", "/orders"}

    async def route_change(e):
        page.views.clear()
        # Redirect to login if token is missing on a protected route
        if page.route in PROTECTED and not session.token:
            await page.push_route("/login")
            return

        builder = ROUTES.get(page.route, login.build)
        page.views.append(builder(page))
        page.update()

    page.on_route_change = route_change
    await page.push_route("/login")


if __name__ == "__main__":
    ft.run(main)
