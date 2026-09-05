# Exercise: Python Descriptors
# Based on: advanced_oop(example).py
#
# Create a descriptor class called 'PositiveNumber' that:
# 1. Uses __set_name__ to store the attribute name
# 2. Uses __set__ to validate the value is a number > 0
# 3. Uses __get__ to return the stored value
#
# Then use it in a Product class with price and stock attributes.
# Test your code at the bottom.

class PositiveNumber:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __set__(self, instance, value):
        if not isinstance(value, (int, float)):
            raise ValueError(f"{value} is not a number.")
        if value <= 0:
            raise ValueError(f"{value} must be greater than 0.")
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.name)


class Product:
    price = PositiveNumber()
    stock = PositiveNumber()
    def __init__(self, name, price, stock , ):
        self.name = name    
        self.price = price
        self.stock = stock

    

# --- Test your code ---
if __name__ == "__main__":
    item = Product("Widget", 9.99, 100)
    print(f"Created: {item.name} | Price: ${item.price} | Stock: {item.stock}")

    item.price = 12.50
    print(f"Updated price: ${item.price}")

    # These should raise ValueError:
    # item.price = -5
    # item.stock = "many"
