import asyncio

import flet as ft
from state import session
from services import auth
from utils.validators import (
    validate_email,
    validate_password,
    validate_name,
    validate_phone,
)
from view.app_bottom_bar import build_bottom_bar


def build(page: ft.Page) -> ft.View:
    user = session.user or {}
    editing = [False]

    error_text = ft.Text("", color=ft.Colors.RED)

    first_name_field = ft.TextField(
        label="First Name:",
        value=user.get("first_name", ""),
        read_only=True,
        width=300,
    )
    last_name_field = ft.TextField(
        label="Last Name:",
        value=user.get("last_name", ""),
        read_only=True,
        width=300,
    )
    email_field = ft.TextField(
        label="Email:",
        value=user.get("email", ""),
        read_only=True,
        width=300,
    )
    phone_field = ft.TextField(
        label="Phone:",
        value=user.get("phone_number", ""),
        read_only=True,
        width=300,
    )
    password_field = ft.TextField(
        label="Password:",
        value="",
        password=True,
        read_only=True,
        width=300,
        tooltip="Leave blank to keep current password when editing profile",
        visible=False,
    )
    delete_button = ft.Button(
        "Delete Account",
        bgcolor=ft.Colors.RED,
        disabled=False,
    )
    edit_button = ft.TextButton("Edit")

    def set_edit_mode(enabled: bool):
        editing[0] = enabled
        first_name_field.read_only = not enabled
        last_name_field.read_only = not enabled
        email_field.read_only = not enabled
        phone_field.read_only = not enabled
        password_field.read_only = not enabled
        password_field.visible = enabled
        delete_button.disabled = enabled
        edit_button.content = "Save" if enabled else "Edit"
        if not enabled:
            error_text.value = ""
        page.update()

    async def on_delete(e):
        confirm_deletion_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Account Deletion"),
            content=ft.Text(
                "Are you sure you want to delete your account? This action cannot be undone."
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda _: setattr(confirm_deletion_dialog, "open", False),
                ),
                ft.TextButton(
                    "Delete", on_click=lambda _: asyncio.create_task(confirm_delete())
                ),
            ],
        )
        page.show_dialog(confirm_deletion_dialog)
        page.update()

        async def confirm_delete():
            result = await auth.delete_account()
            if result is None:
                await page.push_route("/login")
            else:
                page.show_dialog(
                    ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Error"),
                        content=ft.Text(result),
                        actions=[ft.TextButton("OK", on_click=page.pop_dialog)],
                    )
                )
                page.update()

    async def on_edit(e):
        if not editing[0]:
            set_edit_mode(True)
            return

        current_user = session.user or {}
        errors = []

        new_first_name = first_name_field.value.strip()
        new_last_name = last_name_field.value.strip()
        new_email = email_field.value.strip()
        new_phone = phone_field.value.strip()
        new_password = password_field.value.strip() or None

        first_name = (
            new_first_name
            if new_first_name != current_user.get("first_name", "")
            else None
        )
        last_name = (
            new_last_name
            if new_last_name != current_user.get("last_name", "")
            else None
        )
        email = new_email if new_email != current_user.get("email", "") else None
        phone = new_phone if new_phone != current_user.get("phone_number", "") else None
        password = new_password

        if first_name is not None:
            error = validate_name(first_name, "First name")
            if error:
                errors.append(error)
        if last_name is not None:
            error = validate_name(last_name, "Last name")
            if error:
                errors.append(error)
        if email is not None:
            error = validate_email(email)
            if error:
                errors.append(error)
        if phone is not None:
            error = validate_phone(phone)
            if error:
                errors.append(error)
        if password is not None:
            error = validate_password(password)
            if error:
                errors.append(error)

        if errors:
            error_text.value = "\n".join(errors)
            error_text.color = ft.Colors.RED
            page.update()
            return

        result = await auth.update_profile(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            password=password,
        )

        if result is not None:
            error_text.value = result
            error_text.color = ft.Colors.RED
            page.update()
            return

        first_name_field.value = new_first_name
        last_name_field.value = new_last_name
        email_field.value = new_email
        phone_field.value = new_phone
        password_field.value = ""
        set_edit_mode(False)
        error_text.value = (
            ""
            if not any([first_name, last_name, email, phone, password])
            else "Profile updated successfully."
        )
        error_text.color = ft.Colors.GREEN
        page.update()

    delete_button.on_click = on_delete
    edit_button.on_click = on_edit

    nav_bar = ft.Container(
        content=build_bottom_bar(page),
        align=ft.Alignment.BOTTOM_CENTER,
    )

    content = ft.Column(
        expand=True,
        controls=[
            error_text,
            first_name_field,
            last_name_field,
            email_field,
            phone_field,
            password_field,
            ft.Row(
                controls=[delete_button],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(expand=True),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
    )

    page_body = ft.Column(
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Profile"),
                center_title=True,
                actions=[edit_button],
            ),
            content,
        ],
    )

    return ft.View(
        route="/dashboard",
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[page_body, nav_bar],
                ),
            )
        ],
        padding=0,
    )
