import flet as ft
import asyncio
from utils.validators import validate_email, validate_password
from services import auth

def build(page: ft.Page) -> ft.View:
    email_field = ft.TextField(label="E-mail", width=300)
    password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
    login_button = ft.Button("Login")          # ← define first, no on_click yet

    async def on_login(_):
        email_error = validate_email(email_field.value)
        password_error = validate_password(password_field.value)

        email_field.error = email_error
        password_field.error = password_error

        if email_error or password_error:
            page.update()
            return

        login_button.disabled = True           # ← now login_button is already defined
        page.update()

        error = await auth.login(email_field.value, password_field.value)

        if error:
            login_button.disabled = False
            page.show_dialog(ft.AlertDialog(modal=True, title=ft.Text("Error"), content=ft.Text(error), actions=[ft.TextButton("OK", on_click=page.pop_dialog)]))
            page.update()
        else:
            await page.push_route("/dashboard")

    login_button.on_click = on_login           # ← wire up after defining on_login

    return ft.View(
        route="/login",
        controls=[
            ft.AppBar(title=ft.Text("Welcome"), center_title=True),
            email_field,
            password_field,
            login_button,
            ft.TextButton(
                "No account? Sign up",
                on_click=lambda _: asyncio.create_task(page.push_route("/register"))
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )  