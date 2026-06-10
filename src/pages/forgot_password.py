import asyncio

import flet as ft
from utils.validators import validate_email
from services.auth import request_password_reset


def build(page: ft.Page) -> ft.View:
    email_field = ft.TextField(label="Email", width=300)

    async def request_password_reset_email() -> None:
        # Placeholder for actual email sending logic
        email_error = validate_email(email_field.value)
        email_field.error = email_error
        if email_field.error:
            page.update()
            return

        error = await request_password_reset(email_field.value)
        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(""),
                content=ft.Text(error),
                actions=[ft.TextButton("OK", on_click=lambda _: page.pop_dialog())],
                alignment=ft.Alignment.CENTER,
                modal=True,
            )
        )

    async def go_back_login(_):
        await page.push_route("/login")
        page.update()

    return ft.View(
        route="/forgot-password",
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.AppBar(title=ft.Text("Forgot Password"), center_title=True),
                        ft.Text(
                            "Enter your email to receive password reset instructions.",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        email_field,
                        ft.Button(
                            "Send Reset Instructions",
                            on_click=lambda _: asyncio.create_task(
                                request_password_reset_email()
                            ),
                            width=200,
                        ),
                        ft.TextButton(
                            "Back to Login", on_click=go_back_login, width=150
                        ),
                    ],
                ),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
