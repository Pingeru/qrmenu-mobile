import flet as ft
import asyncio
from services import auth
from utils.validators import (
    validate_email,
    validate_password,
    validate_name,
    validate_phone,
)

def build(page: ft.Page) -> ft.View:
    first_name_field  = ft.TextField(label="First Name", width=300)
    last_name_field   = ft.TextField(label="Last Name", width=300)
    phone_field       = ft.TextField(label="Phone Number", width=300, keyboard_type=ft.KeyboardType.PHONE)
    email_field       = ft.TextField(label="E-mail", width=300, keyboard_type=ft.KeyboardType.EMAIL)
    password_field    = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
    register_button   = ft.Button("Register")

    async def on_register(_):
        first_name_error  = validate_name(first_name_field.value, "First name")
        last_name_error   = validate_name(last_name_field.value, "Last name")
        phone_error       = validate_phone(phone_field.value)
        email_error       = validate_email(email_field.value)
        password_error    = validate_password(password_field.value)

        first_name_field.error  = first_name_error
        last_name_field.error  = last_name_error
        phone_field.error      = phone_error
        email_field.error      = email_error
        password_field.error   = password_error

        if any([first_name_error, last_name_error, phone_error, email_error, password_error]):
            page.update()
            return

        register_button.disabled = True
        page.update()

        error = await auth.register(
            first_name=first_name_field.value.strip(),
            last_name=last_name_field.value.strip(),
            phone=phone_field.value.strip(),
            email=email_field.value.strip(),
            password=password_field.value,
        )

        if error:
            register_button.disabled = False
            page.update()
        else:
            async def on_ok(_):
                success_dialog.open = False
                page.update()
                await page.push_route("/login")

            success_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Success"),
                content=ft.Text("Your account has been created. Please log in."),
                actions=[ft.TextButton("OK", on_click=on_ok)],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.show_dialog(success_dialog)
            page.update()

    register_button.on_click = on_register

    return ft.View(
        route="/register",
        controls=[
            ft.AppBar(title=ft.Text("Register"), center_title=True),
            first_name_field,
            last_name_field,
            phone_field,
            email_field,
            password_field,
            register_button,
            ft.TextButton(
                "Already have an account? Login",
                on_click=lambda _: asyncio.create_task(page.push_route("/login")),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )