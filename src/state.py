class AppState:
    token: str | None = None
    refresh_token: str | None = None
    user: dict | None = None

    # Cart: list of {"product_id", "name", "price", "quantity"}
    cart: list[dict] = []
    cart_business_id: str | None = None

    # Menu: persisted across route changes, cleared on logout
    menu_business_id: str | None = None
    menu_categories: list[dict] = []

    def add_to_cart(self, product: dict, business_id: str) -> None:
        """Add one unit of a product to the cart (or increment if already there)."""
        if self.cart_business_id and self.cart_business_id != business_id:
            # Different business — clear old cart first
            self.cart = []
        self.cart_business_id = business_id
        for item in self.cart:
            if item["product_id"] == product["_id"]:
                item["quantity"] += 1
                return
        self.cart.append(
            {
                "product_id": product["_id"],
                "name": product["name"],
                "price": float(product["price"]),
                "quantity": 1,
            }
        )

    def remove_from_cart(self, product_id: str) -> None:
        """Decrement quantity; remove item when it reaches 0."""
        for item in self.cart:
            if item["product_id"] == product_id:
                item["quantity"] -= 1
                if item["quantity"] <= 0:
                    self.cart.remove(item)
                return

    def get_cart_quantity(self, product_id: str) -> int:
        for item in self.cart:
            if item["product_id"] == product_id:
                return item["quantity"]
        return 0

    def cart_total(self) -> float:
        return sum(i["price"] * i["quantity"] for i in self.cart)

    def cart_item_count(self) -> int:
        return sum(i["quantity"] for i in self.cart)

    def clear_cart(self) -> None:
        self.cart = []
        self.cart_business_id = None

    def clear_menu(self) -> None:
        self.menu_business_id = None
        self.menu_categories = []


# Single shared instance imported everywhere
session = AppState()
