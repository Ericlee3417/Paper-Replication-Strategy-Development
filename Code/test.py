from AlphaEngine import AlphaEngine
from Price import Price
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def mean_reverting_simulation(x0, kappa, theta, sigma, T, dt, n_simulations, spread):
    n_steps = int(T / dt)
    t = np.linspace(0, T, n_steps)
    X = np.zeros((n_steps, n_simulations))
    bid = np.zeros((n_steps, n_simulations))
    ask = np.zeros((n_steps, n_simulations))
    X[0] = x0
    bid[0]=x0 - spread / 2
    ask[0]= x0 + spread / 2
    for t in range(1, n_steps):
        dW = np.random.normal(scale=np.sqrt(dt), size=n_simulations)
        X[t] = X[t - 1] + kappa * (theta - X[t - 1]) * dt + sigma * dW
        bid[t] = X[t] - spread / 2  # subtract half the spread from the simulated price
        ask[t] = X[t] + spread / 2  # add half the spread to the simulated price
    return X, bid, ask


def geometric_random_walk_with_spread(S0, mu, sigma, T, dt, n_simulations, spread):
    n_steps = int(T / dt)
    S = np.zeros((n_steps, n_simulations))
    bid = np.zeros((n_steps, n_simulations))
    ask = np.zeros((n_steps, n_simulations))
    S[0] = S0
    bid[0] = S0 - spread / 2
    ask[0] = S0 + spread / 2


    for t in range(1, n_steps):
        Z = np.random.standard_normal(n_simulations)
        S[t] = S[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z)
        bid[t] = S[t] - spread / 2  # subtract half the spread from the simulated price
        ask[t] = S[t] + spread / 2  # add half the spread to the simulated price

    return S, bid, ask


class AlphaEnginePublic():
    def __init__(self, initial_capital, trade_unit):
        self.alpha_engine = AlphaEngine(initial_capital= initial_capital, trade_unit=trade_unit)

    def run(self, price_feed):
        for i, price in enumerate(price_feed):
            # print(f"{i} price {price.mid} ")
            self.alpha_engine.run(price)
            # print(price.time)
            # print("-----")
        self.alpha_engine.finalize(price)


if __name__ == "__main__":
    x0 = 1.00  # Initial value of the process
    mu = 0.08
    kappa = 0.5  # Rate of mean reversion
    theta = 1.00  # Long-term mean
    sigma = 2.5  # Volatility
    T = 1  # Time horizon in years
    dt = 1 / 1000 # Step size in years (daily steps)
    n_simulations = 10  # Number of Monte Carlo simulations
    spread = x0 * 0.001

    simulations, bid_price, ask_price = mean_reverting_simulation(x0, kappa, theta, sigma, T, dt, n_simulations, spread)
    # simulations, bid_price, ask_price = geometric_random_walk_with_spread(x0, mu, sigma, T, dt, n_simulations, spread )
    average_simulation = np.mean(simulations, axis=1)
    bid_prices = np.mean(bid_price, axis=1)
    ask_prices = np.mean(ask_price, axis=1)

    plt.plot(average_simulation, 'b-', linewidth=1, label='Average Simulation')
    plt.title('Monte Carlo Simulations')
    plt.xlabel('Time Steps')
    plt.ylabel('Process Value')
    plt.legend()
    plt.savefig(f'price_line.png', format='png', dpi=300)
    plt.close()

    price_feed = []
    for i, value in enumerate(bid_prices):
        price = Price(bid=value, ask=ask_prices[i], time=i)
        price_feed.append(price)
    trade_unit = 10
    initial_capital = price_feed[0].mid*15*trade_unit
    alpha_engine_public = AlphaEnginePublic(initial_capital, trade_unit)
    alpha_engine_public.run(price_feed)
    # alpha_engine_public.alpha_engine.long_coastline_traders[0].close_position(price_feed[-1])
    histories = alpha_engine_public.alpha_engine.long_coastline_traders[0].trade_history
    final_capital = alpha_engine_public.alpha_engine.long_coastline_traders[0].capital
    for history in histories:
        print(history)
    print(f"final profit :{(final_capital-initial_capital)*100/initial_capital}%")






