from CoastlineTrader import CoastlineTrader


class AlphaEngine:
    def __init__(self, initial_capital, trade_unit):
        self.long_coastline_traders = []
        self.short_coastline_traders = []
        self.initial_capital = initial_capital
        self.trade_unit = trade_unit
        self.aggregate_profit = 0.0
        self.initiate_traders()

    def run(self, price):
        for trader in self.long_coastline_traders:
            trader.run(price)
            # print(f"capital {trader.capital}")
            # print(f"realized profit {trader.realized_profit}\n")
            # print(f"trade history {trader.trade_history}\n")
        for trader in self.short_coastline_traders:
            trader.run(price)
            # print(f"capital {trader.capital}")
            # print(f"realized profit {trader.realized_profit}\n")
            # print(trader.get_position_total_pnl(price))

    def initiate_traders(self):
        self.long_coastline_traders = [
            CoastlineTrader(0.00005, 1, self.initial_capital, self.trade_unit),
            # CoastlineTrader(0.00025, 1, self.initial_capital, self.trade_unit),
            # CoastlineTrader(0.0005, 1, self.initial_capital, self.trade_unit),
            # CoastlineTrader(0.0025, 1, self.initial_capital, self.trade_unit)
        ]
        self.short_coastline_traders = [
            CoastlineTrader(0.00005, -1, self.initial_capital, self.trade_unit),
            # CoastlineTrader(0.00025, -1, self.initial_capital, self.trade_unit),
            # CoastlineTrader(0.0005, -1, self.initial_capital, self.trade_unit),
            # CoastlineTrader(0.0025, -1, self.initial_capital, self.trade_unit)
        ]

    def finalize(self, price):
        for trader in self.long_coastline_traders:
            trader.close_position(price)
        for trader in self.short_coastline_traders:
            trader.close_position(price)

    def calculate_profit(self):
        final_profit = {}
        final_lowest_cap_level = {}
        total_profit_percentage = 0
        pure_pnl_amount = 0
        for index, trader in enumerate(self.long_coastline_traders):
            histories = trader.trade_history
            final_capital = trader.capital
            low = 0
            for history in histories:
                if history["capital_after_trade"] < low:
                    low = history["capital_after_trade"]
            pure_pnl_amount += (final_capital - self.initial_capital)
            profit_percent = (final_capital - self.initial_capital) * 100 / self.initial_capital
            final_profit[f"trader_long_{index}"] = profit_percent
            total_profit_percentage += profit_percent
            final_lowest_cap_level[f"trader_long_{index}"] = low
        for index, trader in enumerate(self.short_coastline_traders):
            histories = trader.trade_history
            final_capital = trader.capital
            low = 0
            for history in histories:
                if history["capital_after_trade"] < low:
                    low = history["capital_after_trade"]
            pure_pnl_amount += (final_capital - self.initial_capital)
            profit_percent = (final_capital - self.initial_capital) * 100 / self.initial_capital
            final_profit[f"trader_short_{index}"] = profit_percent
            total_profit_percentage += profit_percent
            final_lowest_cap_level[f"trader_short_{index}"] = low
        return final_profit, final_lowest_cap_level, total_profit_percentage/(len(self.long_coastline_traders)+len(self.short_coastline_traders)), pure_pnl_amount
