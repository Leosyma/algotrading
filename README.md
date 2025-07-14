# 🤖 Algotrading Bot for MetaTrader 5

This project implements a fully functional algorithmic trading bot integrated with MetaTrader 5 (MT5). It combines real-time data acquisition, automated strategy execution using Bollinger Bands and volume filters, and backtesting capabilities to analyze performance over historical data. The architecture supports both live trading and strategy evaluation to optimize results.

---

## 📌 Project Structure

### 1. `main.py`
- Entry point for the trading system.
- Provides a command-line interface to start and stop the trading strategy.

### 2. `rsi_model.py`
- Implements the main trading logic using Bollinger Bands.
- Strategy logic:
  - **Buy**: When price falls below the lower Bollinger Band and volume is above average.
  - **Sell**: When price rises above the upper Bollinger Band.
- Uses threading and real-time data from MetaTrader via a custom `BotMT` class.
- Includes logging of entries, exits, and trade signals in the console.

### 3. `bot_mt.py`
- Defines the `BotMT` class responsible for:
  - Connecting to the MetaTrader platform.
  - Fetching OHLC data.
  - Sending market orders.
  - Checking open positions and orders.

### 4. `backtesting.py`
- Loads historical data from MT5.
- Simulates trades using the same Bollinger Band strategy.
- Visualizes trades using Plotly candlestick charts.
- Calculates cumulative returns and performs performance analysis.
- Includes parameter tuning for different combinations of rolling window sizes and band widths.

### 5. Strategy Parameters
- `roll_window`: Window size for calculating rolling mean and standard deviation.
- `boll_size`: Multiplier for standard deviation to determine band width.
- `symbol`: Asset to trade (e.g., `PETR4`, `WDO$D`).
- `bet_size`: Position size in each trade.

---

## 📈 Features

- 🔁 **Real-Time Strategy Execution**
- 📊 **Interactive Backtesting Visualization**
- 🧠 **Rule-Based Trading Logic**
- ⚙️ **Parameter Tuning and Optimization**
- 🔄 **Multi-threaded Execution**

---

## ✅ Requirements

- Python 3.8+
- MetaTrader5
- pandas, numpy, plotly
- A valid MT5 demo or live account
- `credentials.json` with login details for MetaTrader5

---



