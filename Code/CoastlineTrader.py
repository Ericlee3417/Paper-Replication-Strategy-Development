from LocalLiquidity import LocalLiquidity
from Runner import Runner
from LimitOrders import LimitOrder


class CoastlineTrader:
    def __init__(self, original_delta, long_short, initial_capital, trade_unit):
        self.original_delta = original_delta
        self.original_unit_size = trade_unit  # This should be set based on your specific needs
        self.long_short = long_short
        self.buy_limit_order = None
        self.sell_limit_order = None
        self.initialized = False
        self.inventory = 0
        self.local_liquidity_indicator = LocalLiquidity(original_delta, original_delta * 2.525729, 50.0)
        self.disbalanced_orders = []
        self.realized_profit = 0.0
        self.position_realized_profit = 0.0
        self.runners = []
        self.initiate_runners(original_delta)
        self.target_abs_pnl = 0.005
        self.trade_history = []
        self.initial_capital = initial_capital
        self.capital = initial_capital

    def initiate_runners(self, original_delta):
        self.runners = [Runner(original_delta, original_delta, original_delta, original_delta)]
        if self.long_short == 1:
            self.runners.append(Runner(0.75 * original_delta, 1.5 * original_delta, 0.75 * original_delta, 0.75 * original_delta))
            self.runners.append(Runner(0.5 * original_delta, 2.0 * original_delta, 0.5 * original_delta, 0.5 * original_delta))
        else:
            self.runners.append(Runner(1.5 * original_delta, 0.75 * original_delta, 0.75 * original_delta, 0.75 * original_delta))
            self.runners.append(Runner(2.0 * original_delta, 0.5 * original_delta, 0.75 * original_delta, 0.75 * original_delta))

    # three kinda of runner in runners -->[a, b, c]  in the initial stage

    def run(self, price):
        self.local_liquidity_indicator.computation(price)
        events = [runner.run(price) for runner in self.runners]  # generating the signal


        if not self.initialized:
            self.initialized = True
            self.correct_thresholds_and_volumes(self.inventory)
            self.put_orders(price)
            # self.recorded_events.append(events[0])
        else:
            if self.check_buy_filled(price):
                self.make_buy_filled(price)
                self.cancel_sell_limit_order()
            elif self.check_sell_filled(price):
                self.make_sell_filled(price)
                self.cancel_buy_limit_order()

            proper_runner_index = self.find_proper_runner_index()
            # self.recorded_events.append(events[proper_runner_index])
            if events[proper_runner_index] != 0:
                # Replace all active limit orders
                self.cancel_buy_limit_order()
                self.cancel_sell_limit_order()
                self.put_orders(price)
            else:
                if self.position_crossed_target_pnl(price):
                    self.close_position(price)
                    self.put_orders(price)
                else:
                    self.correct_orders_level(self.runners[proper_runner_index].get_expected_dc_level())


    def check_buy_filled(self, price):
        if self.buy_limit_order is not None:
            if price.get_ask() < self.buy_limit_order.get_level():
                return True
        return False

    def check_sell_filled(self, price):
        if self.sell_limit_order is not None:
            if price.get_bid() > self.sell_limit_order.get_level():
                return True
        return False

    def put_orders(self, price):
        cascade_vol = self.unite_size_from_inventory * self.compute_liq_unit_coef(
            self.local_liquidity_indicator.liq)
        proper_index = self.find_proper_runner_index()
        expected_upper_ie = self.runners[proper_index].get_expected_upper_ie()
        expected_lower_ie = self.runners[proper_index].get_expected_lower_ie()
        runner_mode = self.runners[proper_index].get_mode()
        delta_up = self.runners[proper_index].get_delta_up()
        delta_down = self.runners[proper_index].get_delta_down()
        d_star_up = self.runners[proper_index].get_d_star_up()
        d_star_down = self.runners[proper_index].get_d_star_down()
        upper_ie_type = self.runners[proper_index].get_upper_ie_type()
        lower_ie_type = self.runners[proper_index].get_lower_ie_type()

        if runner_mode == -1:
            buy_dc_or_os = 2
            buy_delta = d_star_down
            sell_dc_or_os = 1
            sell_delta = delta_up
        else:
            buy_dc_or_os = 1
            buy_delta = delta_down
            sell_dc_or_os = 2
            sell_delta = d_star_up

        if self.long_short == 1:
            if not self.disbalanced_orders:
                self.sell_limit_order = None
                self.buy_limit_order = LimitOrder(1, price.clone(), expected_lower_ie, cascade_vol, lower_ie_type,
                                                  d_star_down)
                self.compute_target_relat_pnl(self.buy_limit_order)
            else:
                self.buy_limit_order = LimitOrder(1, price.clone(), expected_lower_ie, cascade_vol, buy_dc_or_os,
                                                  buy_delta)
                compensated_orders_list = self.find_compensated_orders_list(expected_upper_ie, self.original_delta,
                                                                            -1)
                if compensated_orders_list:
                    self.sell_limit_order = LimitOrder(-1, price.clone(), expected_upper_ie, 0, sell_dc_or_os,
                                                       sell_delta)
                    self.sell_limit_order.set_compensated_orders(compensated_orders_list)
                else:
                    self.sell_limit_order = None
        else:
            if not self.disbalanced_orders:
                self.buy_limit_order = None
                self.sell_limit_order = LimitOrder(-1, price.clone(), expected_upper_ie, cascade_vol, upper_ie_type,
                                                   delta_up)
                self.compute_target_relat_pnl(self.sell_limit_order)
            else:
                compensated_orders_list = self.find_compensated_orders_list(expected_lower_ie, self.original_delta,
                                                                            1)
                if compensated_orders_list:
                    self.buy_limit_order = LimitOrder(1, price.clone(), expected_lower_ie, 0, buy_dc_or_os,
                                                      buy_delta)
                    self.buy_limit_order.set_compensated_orders(compensated_orders_list)
                else:
                    self.buy_limit_order = None
                self.sell_limit_order = LimitOrder(-1, price.clone(), expected_upper_ie, cascade_vol, sell_dc_or_os,
                                                   sell_delta)

    def find_proper_runner_index(self):
        if abs(self.inventory) < 15:
            return 0
        elif 15 <= abs(self.inventory) < 30:
            return 1
        else:
            return 2

    def make_buy_filled(self, price):
        self.inventory += self.buy_limit_order.get_volume()
        self.correct_thresholds_and_volumes(self.inventory)
        buy_cost = self.buy_limit_order.get_volume()*price.get_ask()
        self.capital -= buy_cost
        self.record_trade('buy', price.time, price.get_ask(), buy_cost, self.buy_limit_order.get_volume())

        if self.long_short == 1:
            self.disbalanced_orders.append(self.buy_limit_order.clone())
        else:  # the case if the order is de-cascading
            self.position_realized_profit += self.buy_limit_order.get_relative_pnl()
            # self.capital += self.buy_limit_order.get_relative_pnl()
            self.disbalanced_orders = [order for order in self.disbalanced_orders if
                                       order not in self.buy_limit_order.compensated_orders]

        if not self.disbalanced_orders:  # inventory can become equal to 0, no position in reality
            self.close_position(price)

        self.buy_limit_order = None

    def make_sell_filled(self, price):
        self.inventory -= self.sell_limit_order.get_volume()
        self.correct_thresholds_and_volumes(self.inventory)
        sell_revenue = self.sell_limit_order.get_volume()*price.get_bid()
        self.capital += sell_revenue
        self.record_trade('sell', price.time, price.get_bid(), sell_revenue, self.sell_limit_order.get_volume())

        if self.long_short == -1:
            self.disbalanced_orders.append(self.sell_limit_order.clone())
        else:  # the case if the order is de-cascading
            self.position_realized_profit += self.sell_limit_order.get_relative_pnl()
            # self.capital += self.sell_limit_order.get_relative_pnl()
            self.disbalanced_orders = [order for order in self.disbalanced_orders if
                                       order not in self.sell_limit_order.compensated_orders]

        if not self.disbalanced_orders:  # inventory can become equal to 0, no position in reality
            self.close_position(price)

        self.sell_limit_order = None



    def correct_orders_level(self, expected_dc_level):
        if self.buy_limit_order is not None:
            self.correct_buy_limit_order(expected_dc_level)
        if self.sell_limit_order is not None:
            self.correct_sell_limit_order(expected_dc_level)

    def find_compensated_orders_list(self, level_order, delta, buy_sell):
        compensated_orders = []
        for a_disbalanced_order in self.disbalanced_orders:
            if (a_disbalanced_order.get_level() - level_order) * buy_sell >= delta * a_disbalanced_order.get_level():
                compensated_orders.append(a_disbalanced_order)
        return compensated_orders

    def correct_buy_limit_order(self, expected_dc_level):
        if self.buy_limit_order.get_dc_or_os() == 1:
            if self.long_short == 1 or len(self.disbalanced_orders) > 1:
                if expected_dc_level > self.buy_limit_order.get_level():
                    if len(self.disbalanced_orders) > 1 and self.long_short == -1:
                        compensated_orders_list = self.find_compensated_orders_list(expected_dc_level,
                                                                                    self.original_delta, 1)
                        if compensated_orders_list:
                            self.buy_limit_order.set_level(expected_dc_level)
                            self.buy_limit_order.set_compensated_orders(compensated_orders_list)
                        else:
                            self.buy_limit_order = None
                    else:
                        self.buy_limit_order.set_level(expected_dc_level)
                    return True
        return False

    def correct_sell_limit_order(self, expected_dc_level):
        if self.sell_limit_order.get_dc_or_os() == 1:
            if self.long_short == -1 or len(self.disbalanced_orders) > 1:
                if expected_dc_level < self.sell_limit_order.get_level():
                    if len(self.disbalanced_orders) > 1 and self.long_short == 1:
                        compensated_orders_list = self.find_compensated_orders_list(expected_dc_level,
                                                                                    self.original_delta, -1)
                        if compensated_orders_list:
                            self.sell_limit_order.set_level(expected_dc_level)
                            self.sell_limit_order.set_compensated_orders(compensated_orders_list)
                        else:
                            self.sell_limit_order = None
                    else:
                        self.sell_limit_order.set_level(expected_dc_level)
                    return True
        return False

    def cancel_sell_limit_order(self):
        self.sell_limit_order = None

    def cancel_buy_limit_order(self):
        self.buy_limit_order = None

    def correct_thresholds_and_volumes(self, inventory):
        if abs(inventory) < 15:
            self.unite_size_from_inventory = self.original_unit_size
        elif 15 <= abs(inventory) < 30:
            self.unite_size_from_inventory = self.original_unit_size / 2
        else:
            self.unite_size_from_inventory = self.original_unit_size / 4

    def compute_liq_unit_coef(self, liquidity):
        if 0.5 <= liquidity:
            liq_unit_coef = 1.0
        elif 0.1 <= liquidity < 0.5:
            liq_unit_coef = 0.5
        else:
            liq_unit_coef = 0.1
        return liq_unit_coef

    # def position_crossed_target_pnl(self, price):
    #     return self.get_position_total_pnl(price) >= (self.target_abs_pnl/100)*self.capital
    def position_crossed_target_pnl(self, price):
        return self.get_position_total_pnl(price) >= self.target_abs_pnl

    def get_position_total_pnl(self, price):
        return self.get_position_profit(price)

    def get_position_profit(self, price):
        return self.position_realized_profit + self.get_position_unrealized_profit(price)

    def get_position_unrealized_profit(self, price):
        if self.disbalanced_orders:
            market_price = price.get_bid() if self.long_short == 1 else price.get_ask()
            unrealized_profit = 0.0
            for a_disbalanced_order in self.disbalanced_orders:
                abs_price_move = (market_price - a_disbalanced_order.get_level()) * a_disbalanced_order.get_type()
                unrealized_profit += abs_price_move / a_disbalanced_order.get_level() * a_disbalanced_order.get_volume()
            return unrealized_profit
        return 0.0

    def close_position(self, price):
        close_amount = self.market_order_to_close_position(price)
        close_profit = self.position_realized_profit
        self.realized_profit += close_profit
        self.capital += self.position_realized_profit
        self.record_trade('close', price.time, price.get_bid() if self.long_short == 1 else price.get_ask(),
                          close_amount+close_profit, self.inventory)
        self.position_realized_profit = 0.0
        self.inventory = 0
        self.cancel_buy_limit_order()
        self.cancel_sell_limit_order()
        self.correct_thresholds_and_volumes(self.inventory)

    def market_order_to_close_position(self, price):
        market_price = price.get_bid() if self.long_short == 1 else price.get_ask()
        total_volume_value = 0
        for a_disbalanced_order in self.disbalanced_orders:
            abs_price_move = (market_price - a_disbalanced_order.get_level()) * a_disbalanced_order.get_type()
            pnl = abs_price_move / a_disbalanced_order.get_level() * a_disbalanced_order.get_volume()
            self.position_realized_profit += pnl
            if self.long_short==1:
                self.capital += a_disbalanced_order.get_level() * a_disbalanced_order.get_volume()
            else:
                self.capital -= a_disbalanced_order.get_level() * a_disbalanced_order.get_volume()
            total_volume_value += a_disbalanced_order.get_level() * a_disbalanced_order.get_volume()
        self.disbalanced_orders = []
        return total_volume_value

    def compute_target_relat_pnl(self, LimitOrder):
        # TODO: Implement the method's logic
        pass

    def get_realized_profit(self):
        return self.realized_profit

    def record_trade(self, trade_type, time, price,  amount, volume):
        trade_record = {
            'trade_type': trade_type,
            'time': time,
            'price':price,
            'amount': amount,
            'volume': volume,
            'capital_after_trade': self.capital,
            'realized_profit': self.realized_profit,
            'realized_profit(%)': self.calculate_profit_percentage()
        }
        self.trade_history.append(trade_record)

    def calculate_profit_percentage(self):
        return (self.realized_profit / self.initial_capital) * 100 if self.initial_capital else 0
