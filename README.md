# Paper-Replication-Strategy-Development

# Alpha Engine Trading Strategy

## Overview

This repository contains the implementation and analysis of the **Alpha Engine Trading Strategy**, which is designed for trading in the highly liquid and dynamic forex market. The project replicates and enhances the strategy detailed in the paper "The Alpha Engine: Designing an Automated Trading Algorithm" by Anton Golub, James B. Glattfelder, and Richard B. Olsen.

## Objectives

- **Replication**: Accurately replicate the original Alpha Engine strategy to ensure fidelity to its components and logic.
- **Implementation**: Deploy the strategy in live forex trading using real-time data.
- **Parameter Optimization**: Adjust the strategy’s parameters for optimal performance under varying market conditions.
- **Performance Monitoring**: Continuously monitor and analyze the strategy’s performance in terms of capital changes, profitability, and risk metrics.
- **Advanced Analysis**: Conduct thorough analysis, including hypothesis testing and overfitting assessments, to validate the strategy’s robustness.

## Key Components

- **Intrinsic Time and Directional Changes**: The strategy uses an endogenous time scale to dissect price curves into directional changes and overshoots, identifying key market events.
- **Scaling Laws**: Adjusts trading behavior based on analytical relationships between price movements.
- **Coastline Trading Agents**: Agents trade based on intrinsic events, adjusting position sizes using a probability indicator to mitigate risk.
- **Asymmetric Thresholds**: Introduces asymmetric thresholds for directional changes and overshoots to navigate trending markets and reduce inventory build-up.
- **Fractional Position Changes**: Allows adaptive management of exposure and risk in response to market volatility.

## Methodology

1. **Data Collection**: Historical and real-time forex data for major currency pairs is gathered using OANDA’s API.
2. **Model Replication**: The Alpha Engine model is implemented in a Python-based trading platform.
3. **Parameter Optimization**: Techniques such as grid search are used to fine-tune parameters.
4. **Live Deployment**: The optimized strategy is deployed in a live trading environment.
5. **Performance Evaluation**: Metrics such as Sharpe Ratio, maximum drawdown, and total return are used to evaluate the strategy’s performance.

## Data Description

- **15-minute Price Data (December 14-16, 2008)**: Used for detailed event identification.
- **5-minute Price Data (January 1, 2008 - January 1, 2024)**: Covers several years of market activity for multiple currency pairs.
- **Monte Carlo Simulations**: Used to estimate the number of directional changes under various price line trends.

## Hypothesis Testing

1. **Accuracy of Intrinsic Event Detection**: The strategy's ability to detect small price movements is validated using simulated data.
2. **Effectiveness of Probability Indicator "L"**: The strategy's adjustments in timing and position size are evaluated using historical and simulated price data.

## Constraints and Benchmarks

- **Constraints**: Includes data availability, varying market conditions, technical infrastructure, risk management, parameter sensitivity, and execution costs.
- **Benchmarks**: Performance metrics like Sharpe Ratio, maximum drawdown, and cumulative return are compared against market indices such as the S&P 500.

## Results and Expected Outcomes

- **Enhanced Understanding**: Insights into the effectiveness of the Alpha Engine strategy.
- **Optimized Performance**: Improved risk-adjusted returns through parameter optimization.
- **Robust Validation**: Rigorous testing to ensure robustness and adaptability.
- **Scalable Model**: A trading model applicable to various currency pairs and market conditions.
