import asyncio

import flet as ft
from state import session
from services import auth
from utils.validators import validate_email, validate_password, validate_name, validate_phone
from view.sidebar import build_sidebar


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
        label="Password (leave empty to keep current)",
        value="",
        password=True,
        can_reveal_password=True,
        read_only=True,
        width=300,
    )

    delete_button = ft.Button(
        "Delete Account",
        bgcolor=ft.Colors.RED,
        disabled=False,
    )
    edit_button = ft.TextButton(
        "Edit"
    )

    def set_edit_mode(enabled: bool):
        editing[0] = enabled
        first_name_field.read_only = not enabled
        last_name_field.read_only = not enabled
        email_field.read_only = not enabled
        phone_field.read_only = not enabled
        password_field.read_only = not enabled
        delete_button.disabled = enabled
        edit_button.content = "Save" if enabled else "Edit"
        if not enabled:
            error_text.value = ""
        page.update()

    async def on_delete(e):
        confirm_deletion_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Account Deletion"),
            content=ft.Text("Are you sure you want to delete your account? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(confirm_deletion_dialog, "open", False)),
                ft.TextButton("Delete", on_click=lambda _: asyncio.create_task(confirm_delete())),
            ],
        )
        page.show_dialog(confirm_deletion_dialog)
        page.update()

        async def confirm_delete():
            result = await auth.delete_account()
            if result is None:
                await page.push_route("/login")
            else:
                page.show_dialog(ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Error"),
                    content=ft.Text(result),
                    actions=[ft.TextButton("OK", on_click=page.pop_dialog)]
                ))
                page.update()

    async def on_edit(e):
        if not editing[0]:
            set_edit_mode(True)
            return

        current_user = session.user or {}
        errors = []
        first_name = first_name_field.value.strip() or current_user.get("first_name", "")
        last_name = last_name_field.value.strip() or current_user.get("last_name", "")
        email = email_field.value.strip() or current_user.get("email", "")
        phone = phone_field.value.strip() or current_user.get("phone_number", "")
        password = password_field.value.strip() or None

        if first_name_field.value.strip():
            error = validate_name(first_name, "First name")
            if error:
                errors.append(error)
        if last_name_field.value.strip():
            error = validate_name(last_name, "Last name")
            if error:
                errors.append(error)
        if email_field.value.strip():
            error = validate_email(email)
            if error:
                errors.append(error)
        if phone_field.value.strip():
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

        session.user = {
            **current_user,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone,
        }

        first_name_field.value = first_name
        last_name_field.value = last_name
        email_field.value = email
        phone_field.value = phone
        password_field.value = ""
        set_edit_mode(False)
        error_text.value = "Profile updated successfully."
        error_text.color = ft.Colors.GREEN
        page.update()

    delete_button.on_click = on_delete
    edit_button.on_click = on_edit

    sidebar_component = build_sidebar(page)

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

    # Page body fills the full width — sidebar is layered on top via Stack
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

    main_content = ft.Stack(
        expand=True,
        controls=[
            page_body,
            sidebar_component,   # overlays the body; does not push it
        ],
    )

    return ft.View(
        route="/dashboard",
        controls=[main_content],
        padding=0,
    )






