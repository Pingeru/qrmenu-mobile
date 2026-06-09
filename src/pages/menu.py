import flet as ft
import asyncio
import services.menu as menu_service
import services.order as order_service
from services.qr_scanner import scan_qr_code
from state import session
from view.app_bottom_bar import build_bottom_bar


def build(page: ft.Page) -> ft.View:
    nav_bar = ft.Container(
        content=build_bottom_bar(page),
        align=ft.Alignment.BOTTOM_CENTER,
    )
    current_business_id = session.menu_business_id or ""
    current_categories: list[dict] = list(session.menu_categories)

    # ── FAB (cart badge) ──────────────────────────────────────────────────────

    cart_count_text = ft.Text(
        str(session.cart_item_count()),
        size=12,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
    )

    cart_fab = ft.FloatingActionButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.SHOPPING_CART, color=ft.Colors.WHITE, size=20),
                cart_count_text,
            ],
            tight=True,
            spacing=4,
        ),
        bgcolor=ft.Colors.BLUE,
        visible=False,
        on_click=lambda e: open_cart_sheet(),
    )

    def refresh_fab():
        count = session.cart_item_count()
        cart_count_text.value = str(count)
        cart_fab.visible = count > 0
        page.update()

    # ── cart bottom sheet ─────────────────────────────────────────────────────

    def open_cart_sheet():
        if not session.cart:
            refresh_fab()
            return

        # Store references to controls we'll update
        item_controls_map = {}  # product_id -> {qty_text, remove_btn, add_btn, total_text, row}
        item_row_map = {}  # product_id -> row control
        total_price_text = None
        items_column = None

        def rebuild_item_row(it):
            """Build a row for a single cart item with update-friendly controls."""
            def make_remove(product_id):
                def _remove(e):
                    session.remove_from_cart(product_id)
                    if not session.cart:
                        page.pop_dialog()
                        refresh_fab()
                    else:
                        refresh_sheet_display()
                        refresh_fab()
                return _remove

            def make_add(product_id, name, price):
                def _add(e):
                    session.add_to_cart(
                        {"_id": product_id, "name": name, "price": price},
                        session.cart_business_id or "",
                    )
                    refresh_sheet_display()
                    refresh_fab()
                return _add

            qty_text = ft.Text(
                str(it["quantity"]),
                size=14,
                weight=ft.FontWeight.BOLD,
                width=20,
                text_align=ft.TextAlign.CENTER,
            )
            total_text = ft.Text(
                f"${it['price'] * it['quantity']:.2f}",
                size=14,
                width=60,
                text_align=ft.TextAlign.RIGHT,
            )
            remove_btn = ft.IconButton(
                icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                icon_size=20,
                icon_color=ft.Colors.RED_300,
                on_click=make_remove(it["product_id"]),
            )
            add_btn = ft.IconButton(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                icon_size=20,
                icon_color=ft.Colors.BLUE_300,
                on_click=make_add(it["product_id"], it["name"], it["price"]),
            )

            item_row = ft.Row(
                controls=[
                    ft.Text(it["name"], size=14, expand=True),
                    remove_btn,
                    qty_text,
                    add_btn,
                    total_text,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )

            item_controls_map[it["product_id"]] = {
                "qty_text": qty_text,
                "total_text": total_text,
                "remove_btn": remove_btn,
                "add_btn": add_btn,
                "row": item_row,
            }
            item_row_map[it["product_id"]] = item_row

            return item_row

        def refresh_sheet_display():
            """Update only the changed values without rebuilding the entire sheet."""
            nonlocal total_price_text, items_column
            
            # Check for removed items and remove their rows
            removed_product_ids = [pid for pid in item_controls_map if not any(item["product_id"] == pid for item in session.cart)]
            for pid in removed_product_ids:
                row_to_remove = item_row_map.get(pid)
                if row_to_remove and items_column and row_to_remove in items_column.controls:
                    items_column.controls.remove(row_to_remove)
                del item_controls_map[pid]
                del item_row_map[pid]
            
            # Update quantities and totals for remaining items
            for item in session.cart:
                pid = item["product_id"]
                if pid in item_controls_map:
                    controls = item_controls_map[pid]
                    controls["qty_text"].value = str(item["quantity"])
                    controls["total_text"].value = f"${item['price'] * item['quantity']:.2f}"
                    controls["qty_text"].update()
                    controls["total_text"].update()
            
            if total_price_text:
                total_price_text.value = f"${session.cart_total():.2f}"
                total_price_text.update()
            
            # Update the column to reflect the removed rows
            if items_column:
                items_column.update()

        status_text = ft.Text("", color=ft.Colors.RED, size=13)

        async def on_place_order(e):
            place_btn.disabled = True
            status_text.value = "Placing order…"
            page.update()
         
            order_items = [
                {"product_id": i["product_id"], "quantity": i["quantity"]}
                for i in session.cart
            ]
            order, err = await order_service.create_order(
                business_id=session.cart_business_id or "",
                items=order_items,
            )

            if err:
                status_text.value = err
                place_btn.disabled = False
                page.update()
                return

            session.clear_cart()
            refresh_fab()

            # Close the cart sheet
            page.pop_dialog()

            # Small delay to prevent WebSocket race condition when closing/opening dialogs
            # await asyncio.sleep(0.3)

            page.show_dialog(ft.AlertDialog(
                modal=True,
                title=ft.Text("Order placed! 🎉"),
                content=ft.Text(
                    f"Your order has been received.\n"
                    f"Total: ${order.get('total_amount', 0.0):.2f}"
                ),
                actions=[
                    ft.TextButton("View Orders", on_click=lambda _: asyncio.create_task(_go_orders())),
                    ft.TextButton("OK", on_click=lambda _: page.pop_dialog()),
                ],
            ))
            page.update()

        async def _go_orders():
            page.pop_dialog()
            await page.push_route("/orders")

        place_btn = ft.Button(
            "Place Order",
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=lambda e: asyncio.create_task(on_place_order(e)),
            expand=True,
        )

        total_price_text = ft.Text(
            f"${session.cart_total():.2f}",
            size=15,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE,
        )

        item_rows = [rebuild_item_row(it) for it in session.cart]

        items_column = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Your Cart", size=18, weight=ft.FontWeight.BOLD, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=20,
                            on_click=lambda _: page.pop_dialog(),
                        ),
                    ],
                ),
                ft.Divider(),
                *item_rows,
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Text("Total", size=15, weight=ft.FontWeight.W_600, expand=True),
                        total_price_text,
                    ],
                ),
                status_text,
                ft.Row(controls=[place_btn]),
            ],
            spacing=8,
            tight=True,
            scroll=ft.ScrollMode.AUTO,
        )

        sheet_container = ft.Container(
            content=items_column,
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
        )

        sheet = ft.BottomSheet(
            content=sheet_container,
            open=True,
        )
        page.show_dialog(sheet)
        page.update()



    # ── cart helpers on product cards ─────────────────────────────────────────

    def build_cart_controls(product: dict, business_id: str) -> ft.IconButton:
        """Returns add to cart button for product card."""
        def on_add(e):
            session.add_to_cart(product, business_id)
            refresh_fab()

        return ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            icon_size=24,
            icon_color=ft.Colors.BLUE_300,
            on_click=on_add,
        )

    # ── QR scan ───────────────────────────────────────────────────────────────

    async def on_qr_click(e):
        page_body.controls = [
            ft.Text("Opening camera… Scanning QR code", size=18, weight=ft.FontWeight.BOLD),
            ft.ProgressBar(value=None, width=300),
        ]
        page.update()

        business_id = await scan_qr_code()
        if not business_id:
            page_body.controls = [
                ft.Text("No QR code detected or scan cancelled.", size=16),
                ft.Button("Try Again", on_click=on_qr_click),
            ]
            page.update()
            return

        page_body.controls = [
            ft.Text("Loading menu…", size=18, weight=ft.FontWeight.BOLD),
            ft.ProgressBar(value=None, width=300),
        ]
        page.update()

        nonlocal current_business_id, current_categories
        current_business_id = business_id
        session.menu_business_id = business_id
        current_categories = await menu_service.fetch_categories(business_id)
        session.menu_categories = current_categories
        await build_category_grid()

    # ── category grid ─────────────────────────────────────────────────────────

    async def build_category_grid():
        categories = current_categories

        if not categories:
            page_body.controls = [
                ft.Text("No categories found.", size=16),
                ft.Button("Try Again", on_click=on_qr_click),
            ]
            page.update()
            return

        category_grid = ft.GridView(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.FOOD_BANK, size=40),
                            ft.Text(
                                category["name"],
                                text_align=ft.TextAlign.CENTER,
                                size=14,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=16,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    alignment=ft.Alignment.CENTER,
                    on_click=lambda e, cat_id=category["_id"]: asyncio.create_task(
                        build_product_grid(cat_id)
                    ),
                )
                for category in categories
            ],
            runs_count=2,
            spacing=10,
            run_spacing=10,
            expand=True,
        )

        def on_back_to_qr_scanner(_):
            page_body.controls = [intro_text, qr_button]
            session.clear_menu()
            page.update()

        category_area = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=on_back_to_qr_scanner,
                        ),
                        ft.Text("Categories", size=18, weight=ft.FontWeight.BOLD),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=category_grid,
                    expand=True,
                    margin=ft.Margin.all(20),
                ),
            ],
            expand=True,
        )
        page_body.controls = [category_area]
        page.update()

    # ── product grid ──────────────────────────────────────────────────────────

    async def build_product_grid(category_id: str):
        products = await menu_service.fetch_products_for_category(category_id)
        if not products:
            page_body.controls = [
                ft.Text("No products found in this category.", size=16),
                ft.Button(
                    "Back to Categories",
                    on_click=lambda e: asyncio.create_task(build_category_grid()),
                ),
            ]
            page.update()
            return

        def make_product_card(product: dict) -> ft.Container:
            cart_row = build_cart_controls(product, current_business_id)
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Image(
                                src=(
                                    product.get("image_path", "")
                                    .replace("http://", "https://")
                                    or "https://via.placeholder.com/150?text=No+Image"
                                ),
                                fit=ft.BoxFit.FILL,
                                error_content=ft.Icon(
                                    ft.Icons.IMAGE_NOT_SUPPORTED, size=50, color=ft.Colors.GREY
                                ),
                                border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
                                expand=True,
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(product["name"], size=13, weight=ft.FontWeight.W_500, expand=True),
                                            ft.Text(
                                                f"${product['price']:.2f}",
                                                size=13,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.GREEN,
                                            ),
                                        ],
                                        margin=ft.Margin(bottom=0, top=4, left=0, right=0),
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Text(
                                        product.get("description", ""),
                                        size=11,
                                        color=ft.Colors.GREY_700,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    cart_row,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=6,
                            ),
                            padding=ft.Padding.only(left=12, right=12, bottom=12),
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    alignment=ft.MainAxisAlignment.START,
                    spacing=0,
                ),
                padding=0,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                alignment=ft.Alignment.CENTER,
            )

        product_grid = ft.GridView(
            controls=[make_product_card(p) for p in products],
            runs_count=2,
            spacing=10,
            run_spacing=10,
            expand=True,
        )

        async def on_back_to_categories(_):
            await build_category_grid()

        product_area = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda e: asyncio.create_task(on_back_to_categories(e)),
                        ),
                        ft.Text("Products", size=18, weight=ft.FontWeight.BOLD),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=product_grid,
                    expand=True,
                    margin=ft.Margin.all(20),
                ),
            ],
            expand=True,
        )

        page_body.controls = [product_area]
        page.update()

    # ── initial state ─────────────────────────────────────────────────────────

    qr_button = ft.IconButton(
        icon=ft.Icons.QR_CODE_SCANNER,
        icon_size=100,
        alignment=ft.Alignment.CENTER,
        bgcolor=ft.Colors.CYAN,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        width=200,
        height=200,
        on_click=on_qr_click,
    )

    intro_text = ft.Text(
        "Scan the QR code on your table to view the menu and place your order.",
        text_align=ft.TextAlign.CENTER,
        width=300,
    )

    page_body = ft.Column(
        expand=True,
        spacing=20,
        controls=[intro_text, qr_button],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    main_content = ft.Container(
        expand=True,
        content=page_body,
        align=ft.Alignment.CENTER,
    )

    # Sync FAB badge with any leftover cart from a previous visit
    refresh_fab()

    # If a restaurant was already scanned this session, restore the category grid
    if session.menu_business_id and session.menu_categories:
        asyncio.create_task(build_category_grid())

    return ft.View(
        route="/menu",
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[main_content, nav_bar],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                )
            )
        ],
        padding=0,
        floating_action_button=cart_fab,
        floating_action_button_location=ft.FloatingActionButtonLocation.CENTER_DOCKED,
    )

