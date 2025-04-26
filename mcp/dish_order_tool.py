class DishOrderTool:
    def __init__(self):
        self.orders = []

    def add_order(self, dish_name, quantity):
        order = {
            "dish_name": dish_name,
            "quantity": quantity
        }
        self.orders.append(order)

    def get_orders(self):
        return self.orders

    def clear_orders(self):
        self.orders = []
