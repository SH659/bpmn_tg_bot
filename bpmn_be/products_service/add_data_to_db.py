from database import db, Product

if __name__ == "__main__":
    products = [
        Product(title="Apple", cost=100, description="Very tasty apple"),
        Product(title="Banana", cost=50, description="Very tasty banana"),
        Product(title="Orange", cost=70, description="Very tasty orange"),
        Product(title="Pineapple", cost=200, description="Very tasty pineapple"),
        Product(title="Strawberry", cost=150, description="Very tasty strawberry"),
        Product(title="Blueberry", cost=120, description="Very tasty blueberry"),
        Product(title="Raspberry", cost=130, description="Very tasty raspberry"),
        Product(title="Blackberry", cost=140, description="Very tasty blackberry"),
        Product(title="Cherry", cost=110, description="Very tasty cherry"),
        Product(title="Grape", cost=80, description="Very tasty grape"),
        Product(title="Watermelon", cost=90, description="Very tasty watermelon"),
        Product(title="Melon", cost=120, description="Very tasty melon"),
    ]
    with db.atomic():
        for prod in products:
            prod.save()
