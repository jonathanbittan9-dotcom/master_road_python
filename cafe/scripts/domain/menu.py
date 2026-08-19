class Order:
    def __init__(self, menu: list) -> None:
        self.menu = menu

    def price_per_size(self) -> dict:
        return {
            "small": 6,
            "medium": 9,
            "large": 13,
        }

    def __str__(self) -> str:
        return str(self.price_per_size())


def main():
    order = Order(menu=["small", "medium", "large"])


if __name__ == "__main__":
    main()
