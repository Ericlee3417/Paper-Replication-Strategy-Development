from AlphaEngine import AlphaEngine
from Price import Price
import pandas as pd
import matplotlib.pyplot as plt



class AlphaEnginePublic():
    def __init__(self, initial_capital, trade_unit):
        self.alpha_engine = AlphaEngine(initial_capital= initial_capital, trade_unit=trade_unit)

    def run(self, price_feed):
        for i, price in enumerate(price_feed):
            # print(f"{i} price {price.mid} ")
            self.alpha_engine.run(price)
        self.alpha_engine.finalize(price_feed[-1])
        return self.alpha_engine.calculate_profit()


if __name__ == "__main__":
    df = pd.read_csv("/Users/ericlee/Downloads/trading_model/Alpha_Engine/Data/NZD_JPY_5min_2006_2015.csv")
    df['time'] = pd.to_datetime(df['time'])

    grouped_df = df.groupby(df['time'].dt.date)
    profit_history = []
    lowest_cap_history = []
    avg_profit_history = []
    pure_pnl_history = []
    agg_pure_pnl_history = []
    dates =[]
    daily_capital_record = []
    prices_line = []
    agg_pure_pnl = 0
    for date, daily_data in grouped_df:
        dates.append(date)
        price_feed = [Price(row['bid_c'], row['ask_c'], row['time']) for index, row in daily_data.iterrows()]
        daily_prices = [price.get_mid() for price in price_feed]
        avg_mid_price = sum(daily_prices) / len(daily_prices)
        prices_line.append(avg_mid_price)
        trade_unit = 10
        daily_capital = price_feed[0].mid * 5 * trade_unit
        daily_capital_record.append(daily_capital)

        alpha_engine_public = AlphaEnginePublic(daily_capital, trade_unit)
        final_profit, final_lowest_cap_level, avg_profit_percentage, pure_pnl_amount = alpha_engine_public.run(price_feed)

        pure_pnl_history.append(pure_pnl_amount)
        agg_pure_pnl += pure_pnl_amount
        agg_pure_pnl_history.append(agg_pure_pnl)
        profit_history.append(final_profit)
        lowest_cap_history.append(final_lowest_cap_level)
        avg_profit_history.append(avg_profit_percentage)

    # long_trader = []
    # short_trader = []
    # for record in profit_history:
    #     long_trader.append(record["trader_long_0"])
    #     short_trader.append(record['trader_short_0'])
    # plt.plot(dates, long_trader, label='long_trade', linewidth=1)
    # plt.plot(dates, short_trader, label='long_trade', linewidth=1)
    print(f"average daily enter capital: {sum(daily_capital_record)*2 / len(daily_capital_record)}")
    fig, axs = plt.subplots(4, 1, figsize=(16, 8))
    axs[0].plot(dates, prices_line, label='price_line', linewidth=1)
    axs[0].grid()
    axs[0].legend()
    axs[1].plot(dates, avg_profit_history, label='avg_all_trader_daily_PnL(%)', linewidth=1)
    axs[1].grid()
    axs[1].legend()
    axs[2].plot(dates, pure_pnl_history, label='daily_PnL_amount', linewidth=1)
    axs[2].grid()
    axs[2].legend()
    axs[3].plot(dates, agg_pure_pnl_history, label='aggregate_PnL_amount', linewidth=1)
    axs[3].grid()
    axs[3].legend()
    # plt.savefig('NZD_JPY_5min_trade_track_plot_percent.png', format='png', dpi=300)
    plt.show()


