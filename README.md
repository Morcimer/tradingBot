# EMA-Momentum Bot

This is a Python project for building an EMA-Momentum trading bot with a FastAPI interface.

## Features

- **EMA 20/50 Crossover Strategy**: Golden Cross (BUY) and Death Cross (SELL) signals
- **FastAPI Web Interface**: RESTful API for bot control and monitoring
- **Real-time Data**: Historical price data from Yahoo Finance (yfinance)
- **Automated Scheduling**: Daily analysis at configurable times
- **Trade History**: Complete signal logging and statistics
- **Docker Support**: Containerized deployment ready

## Installation

### From PyPI (when published)

```bash
pip install trading-bot-ema
```

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/Morcimer/tradingBot.git
   cd tradingBot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Bot

```bash
python src/main.py
```

The bot will start a FastAPI server on `http://localhost:8000`

### API Documentation

Access the interactive API docs at: `http://localhost:8000/docs`

#### Key Endpoints:

- `GET /` - Root endpoint
- `GET /status` - Get bot status
- `GET /config` - Get current configuration
- `GET /signals` - Get recent trade signals
- `POST /start` - Start the bot
- `POST /stop` - Stop the bot
- `POST /analyze` - Run analysis immediately

### Using Docker

```bash
docker build -t trading-bot .
docker run -p 8000:8000 trading-bot
```

Or with Podman:

```bash
podman build -t trading-bot .
podman run -p 8000:8000 trading-bot
```

## Configuration

Edit `src/main.py` to customize:

- **Symbol**: Default is `BTC-USD`, change `bot = EMATradingBot(symbol="BTC-USD")`
- **EMA Periods**: Default 20/50, change `ema_short=20, ema_long=50`
- **Schedule**: Modify the `schedule.every().day.at("09:00")` line

## Strategy Details

### EMA-Momentum Strategy

The bot monitors two Exponential Moving Averages:
- **EMA Short**: 20-day period (more responsive)
- **EMA Long**: 50-day period (trend indicator)

#### Buy Signal (Golden Cross)
When EMA-20 crosses above EMA-50, indicating potential uptrend

#### Sell Signal (Death Cross)
When EMA-20 crosses below EMA-50, indicating potential downtrend

#### No Signal (Hold)
No crossover detected

## Description

The bot calculates Exponential Moving Average (EMA) and Momentum indicators for trading signals. It uses real-time market data from Yahoo Finance and provides a modern API interface for control and monitoring.

## Requirements

- Python 3.9+
- pandas
- numpy
- yfinance
- ta-lib
- fastapi
- uvicorn
- schedule

## License

MIT License - see LICENSE file for details

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
