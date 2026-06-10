import asyncio

import flet as ft
import services.order as order_service
from view.app_bottom_bar import build_bottom_bar

# ── colour helpers ────────────────────────────────────────────────────────────

_STATUS_COLORS: dict[str, ft.Colors] = {
    "placed": ft.Colors.BLUE,
    "preparing": ft.Colors.ORANGE,
    "ready": ft.Colors.GREEN,
    "delivered": ft.Colors.GREEN_700,
    "cancelled": ft.Colors.RED,
}


def _status_badge(status: str) -> ft.Container:
    color = _STATUS_COLORS.get(status, ft.Colors.GREY)
    return ft.Container(
        content=ft.Text(
            status.capitalize(),
            size=11,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.WHITE,
        ),
        bgcolor=color,
        border_radius=20,
        padding=ft.Padding(left=10, right=10, top=3, bottom=3),
    )


# ── page builder ──────────────────────────────────────────────────────────────


def build(page: ft.Page) -> ft.View:
    nav_bar = ft.Container(
        content=build_bottom_bar(page),
        align=ft.Alignment.BOTTOM_CENTER,
    )

    # ── mutable body container ────────────────────────────────────────────────
    body = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=12,
        controls=[],
    )

    # ── loading / error helpers ───────────────────────────────────────────────

    def show_loading():
        body.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.ProgressRing(),
                        ft.Text("Loading orders…", size=14, color=ft.Colors.GREY),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        ]
        page.update()

    def show_error(msg: str):
        body.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400
                        ),
                        ft.Text(
                            msg,
                            size=14,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.RED_400,
                        ),
                        ft.TextButton(
                            "Retry",
                            on_click=lambda _: asyncio.create_task(load_orders()),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
                padding=32,
            )
        ]
        page.update()

    def show_empty():
        body.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.RECEIPT_LONG_OUTLINED,
                            size=64,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.Text(
                            "No orders yet",
                            size=16,
                            weight=ft.FontWeight.W_500,
                            color=ft.Colors.GREY,
                        ),
                        ft.Text(
                            "Scan a QR code on the Menu tab to place your first order.",
                            size=13,
                            color=ft.Colors.GREY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
                padding=32,
            )
        ]
        page.update()

    # ── order card ────────────────────────────────────────────────────────────

    def build_order_card(order: dict) -> ft.Container:
        order_id = order.get("_id", "")
        status = order.get("status", "placed")
        items = order.get("items", [])
        # Backend returns total_amount, map to total for display
        total = order.get("total_amount", 0.0)
        created_at = order.get("created_at", "")

        # Format date nicely if ISO string present
        date_str = created_at[:10] if len(created_at) >= 10 else created_at

        item_rows = [
            ft.Row(
                controls=[
                    ft.Text(
                        f"{it.get('product_name', 'Item')}  ×{it.get('quantity', 1)}",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        expand=True,
                    ),
                    ft.Text(
                        # Backend returns price_at_purchase, multiply by quantity for item total
                        f"${it.get('price_at_purchase', 0.0) * it.get('quantity', 1):.2f}",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
            )
            for it in items
        ]

        # Cancel button — only visible when status is "placed"
        cancel_btn_row: list[ft.Control] = []
        if status == "placed":

            async def on_cancel(e, oid=order_id):
                ok, err = await order_service.cancel_order(oid)
                if ok:
                    await load_orders()
                else:
                    page.show_dialog(
                        ft.AlertDialog(
                            modal=True,
                            title=ft.Text("Cannot cancel"),
                            content=ft.Text(err or "Unknown error"),
                            actions=[
                                ft.TextButton(
                                    "OK", on_click=lambda _: page.pop_dialog()
                                )
                            ],
                        )
                    )
                    page.update()

            cancel_btn_row = [
                ft.Divider(height=1),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Cancel Order",
                            icon=ft.Icons.CANCEL_OUTLINED,
                            style=ft.ButtonStyle(color=ft.Colors.RED),
                            on_click=on_cancel,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ]

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header row: date + status badge
                    ft.Row(
                        controls=[
                            ft.Text(
                                date_str,
                                size=12,
                                color=ft.Colors.GREY,
                                expand=True,
                            ),
                            _status_badge(status),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1),
                    # Item rows
                    *item_rows,
                    ft.Divider(height=1),
                    # Total row
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Total",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                expand=True,
                            ),
                            ft.Text(
                                f"${total:.2f}", size=14, weight=ft.FontWeight.BOLD
                            ),
                        ],
                    ),
                    *cancel_btn_row,
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=14,
            padding=16,
            margin=ft.Margin(left=16, right=16, top=0, bottom=0),
        )

    # ── data loader ───────────────────────────────────────────────────────────

    async def load_orders():
        show_loading()
        orders, err = await order_service.get_orders()

        if err:
            show_error(err)
            return

        if not orders:
            show_empty()
            return

        # Newest first
        orders_sorted = sorted(
            orders,
            key=lambda o: o.get("created_at", ""),
            reverse=True,
        )

        body.controls = [build_order_card(o) for o in orders_sorted]
        page.update()

    # ── app bar with refresh ──────────────────────────────────────────────────

    app_bar = ft.AppBar(
        title=ft.Text("My Orders"),
        center_title=True,
        actions=[
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh",
                on_click=lambda _: asyncio.create_task(load_orders()),
            ),
        ],
    )

    # ── trigger initial load via page lifecycle ───────────────────────────────

    async def on_view_added(e):
        if page.route == "/orders":
            await load_orders()

    page.on_view_pop = on_view_added  # reloads on back-navigation too

    # Kick off load immediately
    show_loading()
    asyncio.create_task(load_orders())

    main_content = ft.Container(
        expand=True,
        content=body,
    )

    return ft.View(
        route="/orders",
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[
                        app_bar,
                        main_content,
                    ],
                ),
            ),
            nav_bar,
        ],
        padding=0,
        on_scroll=None,
    )
