import flet as ft
import asyncio
import services.menu as menu_service
from services.qr_scanner import scan_qr_code
from view.sidebar import build_sidebar


def build(page: ft.Page) -> ft.View:
    sidebar = build_sidebar(page)

    async def on_qr_click(e):
        # Show loading state
        content_area.controls = [
            ft.Text("Opening camera... Scanning QR code", size=18, weight=ft.FontWeight.BOLD),
            ft.ProgressBar(value=None, width=300),
        ]
        page.update()

        # Scan QR code
        qr_data = await scan_qr_code()

        if not qr_data:
            content_area.controls = [
                ft.Text("No QR code detected or scan cancelled.", size=16),
                ft.ElevatedButton(
                    "Try Again",
                    on_click=on_qr_click,
                ),
            ]
            page.update()
            return

        # QR scanned successfully, now fetch and display all categories
        content_area.controls = [
            ft.Text("Loading menu...", size=18, weight=ft.FontWeight.BOLD),
            ft.ProgressBar(value=None, width=300),
        ]
        page.update()


    qr_button = ft.IconButton(
        icon=ft.Icons.QR_CODE_SCANNER,
        icon_size=100,
        alignment=ft.Alignment.CENTER,
        bgcolor=ft.Colors.CYAN,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        width=200,
        height=200,
        on_click=on_qr_click,
    )

    intro_text = ft.Text(
        "Scan the QR code on your table to view the menu and place your order.",
        text_align=ft.TextAlign.CENTER,
        width=300,
    )

    content_area = ft.Column(
        expand=True,
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            intro_text,
            qr_button,
        ],
    )

    # Page body fills the full width — sidebar is layered on top via Stack
    page_body = ft.Column(
        expand=True,
        controls=[
            ft.AppBar(title=ft.Text("Menu"), center_title=True),
            content_area,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    main_content = ft.Stack(
        expand=True,
        controls=[
            page_body,
            sidebar,   # overlays the body; does not push it
        ],
    )

    return ft.View(
        route="/menu",
        controls=[main_content],
        padding=0,
    )

