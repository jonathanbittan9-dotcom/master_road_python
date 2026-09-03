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
    def __set_name(self , positive:int) -> None:
        self.positive = "_" + positive
    
    def __set__(self , instance ,value) -> None:
        if not isinstance(value , int):
            raise ValueError f"{value} is not an int."
        setattr(instance ,self.positive , value=)
    
    def __get__(self, instance , owner) -> None:
        if instance is None:
            return self
        getattr(instance , self.positive)

        




class Product:
    price = PositiveNumber()
    stock = PositiveNumber()

P = Product()

P.price 
    def __init__(self, name, price, stock):
        self.name = name
        # Initialize price and stock here
        pass


# --- Test your code ---
if __name__ == "__main__":
    item = Product("Widget", 9.99, 100)
    print(f"Created: {item.name} | Price: ${item.price} | Stock: {item.stock}")

    item.price = 12.50
    print(f"Updated price: ${item.price}")

    # These should raise ValueError:
    # item.price = -5
    # item.stock = "many"
