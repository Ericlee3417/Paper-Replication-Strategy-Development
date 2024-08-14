class LimitOrder:
    def __init__(self, order_type, price_opened, level, volume, dc_or_os, delta):
        self.order_type = order_type
        self.price_opened = price_opened.clone()
        self.level = level
        self.volume = volume
        self.delta = delta
        self.dc_or_os = dc_or_os
        self.compensated_orders = []

    def clone(self):
        return LimitOrder(self.order_type, self.price_opened, self.level, self.volume, self.dc_or_os, self.delta)

    def set_level(self, level):
        self.level = level

    def get_type(self):
        return self.order_type

    def get_level(self):
        return self.level

    def get_volume(self):
        return self.volume

    def get_dc_or_os(self):
        return self.dc_or_os

    def get_delta(self):
        return self.delta

    def add_compensated_order(self, compensated_order):
        self.compensated_orders.append(compensated_order)

    def clean_compensated_list(self):
        self.compensated_orders = []

    def set_compensated_orders(self, compensated_orders):
        self.compensated_orders = compensated_orders
        self.volume = self.compute_compensated_volume()

    def compute_compensated_volume(self):
        compensated_volume = 0
        for compensated_order in self.compensated_orders:
            compensated_volume += compensated_order.get_volume()
        return compensated_volume

    def get_relative_pnl(self):
        relative_pnl = 0
        for compensated_order in self.compensated_orders:
            abs_price_move = (compensated_order.get_level() - self.level) * self.order_type
            if abs_price_move < 0:
                print("Negative price move when Sell? " + str(abs_price_move))
            relative_pnl += abs_price_move / compensated_order.get_level() * compensated_order.get_volume()
        return relative_pnl
