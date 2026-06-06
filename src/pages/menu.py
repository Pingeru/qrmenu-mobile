import flet as ft
import asyncio
import services.menu as menu_service
from services.qr_scanner import scan_qr_code
from view.app_bottom_bar import build_bottom_bar

def build(page: ft.Page) -> ft.View:
    sidebar = build_bottom_bar(page)
    current_business_id = ""

    async def on_qr_click(e):
        # Show loading state
        content_area.controls = [
            ft.Text("Opening camera... Scanning QR code", size=18, weight=ft.FontWeight.BOLD),
            ft.ProgressBar(value=None, width=300),
        ]
        page.update()

        # Scan QR code
        business_id = await scan_qr_code()
        if not business_id:
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
        nonlocal current_business_id
        current_business_id = business_id
        await build_category_grid(business_id)

    # Build category grid
    async def build_category_grid(business_id: str):
        categories = await menu_service.fetch_categories(business_id)
        
        if not categories:
            content_area.controls = [
                ft.Text("No categories found.", size=16),
                ft.Button(
                    "Try Again",
                    on_click=on_qr_click,
                ),
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
                    on_click=lambda e, cat_id=category["_id"]: asyncio.create_task(build_product_grid(cat_id)),
                ) for category in categories
            ],
            runs_count=2,
            spacing=10,
            run_spacing=10,
            expand=True,
        )

        def on_back_to_qr_scanner(_):
            content_area.controls = [intro_text, qr_button]
            main_content.controls = [page_body, sidebar]
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
                    margin = ft.Margin.all(20),
                ),
            ],
            expand=True,
        )
        main_content.controls = [category_area, sidebar]
        page.update()

    async def build_product_grid(category_id: str):
        products = await menu_service.fetch_products_for_category(category_id)
        for product in products:
            print(product)
        if not products:
            content_area.controls = [
                ft.Text("No products found in this category.", size=16),
                ft.Button(
                    "Back to Categories",
                    on_click=lambda e: asyncio.create_task(build_category_grid(current_business_id)),
                ),
            ]
            page.update()
            return
        product_grid = ft.GridView(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Image(
                                src=product.get("image_path", "").replace("http://", "https://") or "https://via.placeholder.com/150?text=No+Image",
                                width=150,
                                height=150,
                                fit=ft.BoxFit.COVER,
                                error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=50, color=ft.Colors.GREY),
                                border_radius=12,
                                expand=True,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        product["name"],
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        f"${product['price']:.2f}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.GREEN,
                                    ),
                                ],
                                margin=ft.Margin(bottom=8),
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),  
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=16,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    alignment=ft.Alignment.CENTER,
                ) for product in products
            ],
            runs_count=2,
            spacing=10,
            run_spacing=10,
            expand=True,
        )
        async def on_back_to_categories(_):
            await build_category_grid(current_business_id)

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
                    margin = ft.Margin.all(20),
                ),
            ],
            expand=True,
        )

        main_content.controls = [product_area, sidebar]
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

    page_body = ft.Container(
        content=content_area,
        expand=True,
        alignment=ft.Alignment.CENTER,
    )

    main_content = ft.Column(
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

