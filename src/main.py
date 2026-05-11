"""
EMA-Momentum Trading Bot
Simple trading bot using EMA 20/50 crossover strategy with FastAPI interface
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time

import pandas as pd
import numpy as np
import yfinance as yf
import schedule
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class TradeSignal(BaseModel):
    """Trade signal data model"""
    timestamp: str
    symbol: str
    signal: str  # BUY, SELL, HOLD
    ema_short: float
    ema_long: float
    price: float
    reason: str


class BotConfig(BaseModel):
    """Bot configuration"""
    symbol: str = "BTC-USD"
    interval: str = "1d"  # Daily data
    ema_short_period: int = 20
    ema_long_period: int = 50
    is_running: bool = False


class BotStatus(BaseModel):
    """Bot status response"""
    is_running: bool
    last_update: Optional[str]
    last_signal: Optional[TradeSignal]
    config: BotConfig
    total_trades: int


# ============================================================================
# Trading Bot Class
# ============================================================================

class EMATradingBot:
    """EMA-Momentum trading bot"""
    
    def __init__(self, symbol: str = "BTC-USD", ema_short: int = 20, ema_long: int = 50):
        self.symbol = symbol
        self.ema_short_period = ema_short
        self.ema_long_period = ema_long
        
        self.is_running = False
        self.last_signal: Optional[TradeSignal] = None
        self.last_update: Optional[str] = None
        self.trade_history: List[TradeSignal] = []
        
        logger.info(f"Bot initialized for {symbol} with EMA({ema_short}, {ema_long})")
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    def fetch_data(self, days: int = 100) -> pd.DataFrame:
        """Fetch historical price data from yfinance"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = yf.download(
                self.symbol,
                start=start_date,
                end=end_date,
                interval='1d',
                progress=False
            )
            
            if data.empty:
                logger.error(f"No data fetched for {self.symbol}")
                return pd.DataFrame()
            
            logger.info(f"Fetched {len(data)} days of data for {self.symbol}")
            return data
        
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def analyze_signal(self, data: pd.DataFrame) -> Optional[TradeSignal]:
        """
        Analyze data and generate trading signal
        
        Strategy:
        - BUY: EMA-short crosses above EMA-long (bullish)
        - SELL: EMA-short crosses below EMA-long (bearish)
        - HOLD: No clear signal
        """
        if data.empty or len(data) < self.ema_long_period + 1:
            logger.warning("Insufficient data for analysis")
            return None
        
        try:
            # Calculate EMAs
            data['EMA_SHORT'] = self.calculate_ema(data['Close'], self.ema_short_period)
            data['EMA_LONG'] = self.calculate_ema(data['Close'], self.ema_long_period)
            
            # Get latest values
            latest = data.iloc[-1]
            previous = data.iloc[-2]
            
            current_price = latest['Close']
            current_ema_short = latest['EMA_SHORT']
            current_ema_long = latest['EMA_LONG']
            prev_ema_short = previous['EMA_SHORT']
            prev_ema_long = previous['EMA_LONG']
            
            # Determine signal
            signal = "HOLD"
            reason = "No crossover detected"
            
            # BUY signal: EMA short crosses above EMA long
            if (prev_ema_short <= prev_ema_long and 
                current_ema_short > current_ema_long):
                signal = "BUY"
                reason = f"Golden Cross: EMA{self.ema_short_period} crossed above EMA{self.ema_long_period}"
            
            # SELL signal: EMA short crosses below EMA long
            elif (prev_ema_short >= prev_ema_long and 
                  current_ema_short < current_ema_long):
                signal = "SELL"
                reason = f"Death Cross: EMA{self.ema_short_period} crossed below EMA{self.ema_long_period}"
            
            # Create signal object
            trade_signal = TradeSignal(
                timestamp=latest.name.strftime('%Y-%m-%d %H:%M:%S'),
                symbol=self.symbol,
                signal=signal,
                ema_short=round(float(current_ema_short), 2),
                ema_long=round(float(current_ema_long), 2),
                price=round(float(current_price), 2),
                reason=reason
            )
            
            return trade_signal
        
        except Exception as e:
            logger.error(f"Error analyzing signal: {e}")
            return None
    
    def run_analysis(self):
        """Run a complete analysis cycle"""
        logger.info(f"Running analysis for {self.symbol}")
        
        # Fetch data
        data = self.fetch_data(days=100)
        if data.empty:
            return
        
        # Analyze and get signal
        signal = self.analyze_signal(data)
        if signal:
            self.last_signal = signal
            self.last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.trade_history.append(signal)
            
            log_msg = (
                f"Signal: {signal.signal} | Price: ${signal.price} | "
                f"EMA{self.ema_short_period}: ${signal.ema_short} | "
                f"EMA{self.ema_long_period}: ${signal.ema_long}"
            )
            
            if signal.signal != "HOLD":
                logger.info(f"🎯 {log_msg}")
                logger.info(f"   Reason: {signal.reason}")
            else:
                logger.debug(log_msg)
    
    def start(self):
        """Start the bot"""
        if self.is_running:
            logger.warning("Bot is already running")
            return
        
        self.is_running = True
        logger.info("Bot started")
        
        # Run initial analysis
        self.run_analysis()
        
        # Schedule periodic analysis (every day at 9:00 AM UTC)
        schedule.every().day.at("09:00").do(self.run_analysis)
        
        # Run scheduler in background thread
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False
        schedule.clear()
        logger.info("Bot stopped")
    
    def _run_scheduler(self):
        """Run the scheduler in a loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            "is_running": self.is_running,
            "last_update": self.last_update,
            "last_signal": self.last_signal,
            "total_trades": len([t for t in self.trade_history if t.signal != "HOLD"]),
            "history_count": len(self.trade_history)
        }


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="EMA-Momentum Trading Bot",
    description="Simple trading bot using EMA 20/50 crossover strategy",
    version="1.0.0"
)

# Initialize bot
bot = EMATradingBot(symbol="BTC-USD", ema_short=20, ema_long=50)


@app.on_event("startup")
async def startup_event():
    """Start bot on application startup"""
    bot.start()
    logger.info("FastAPI app started, bot initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop bot on application shutdown"""
    bot.stop()
    logger.info("FastAPI app shutting down, bot stopped")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "EMA-Momentum Trading Bot API",
        "docs": "/docs",
        "status": "/status"
    }


@app.get("/status", response_model=BotStatus)
async def get_status():
    """Get bot status"""
    status = bot.get_status()
    return BotStatus(
        is_running=status["is_running"],
        last_update=status["last_update"],
        last_signal=status["last_signal"],
        config=BotConfig(),
        total_trades=status["total_trades"]
    )


@app.post("/start")
async def start_bot():
    """Start the bot"""
    if bot.is_running:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    bot.start()
    return {"message": "Bot started", "status": bot.get_status()}


@app.post("/stop")
async def stop_bot():
    """Stop the bot"""
    if not bot.is_running:
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    bot.stop()
    return {"message": "Bot stopped", "status": bot.get_status()}


@app.post("/analyze")
async def run_analysis():
    """Run analysis immediately"""
    bot.run_analysis()
    return {
        "message": "Analysis completed",
        "last_signal": bot.last_signal,
        "last_update": bot.last_update
    }


@app.get("/signals")
async def get_signals(limit: int = 10):
    """Get recent trade signals"""
    signals = bot.trade_history[-limit:]
    return {
        "total_signals": len(bot.trade_history),
        "recent_signals": signals,
        "buy_signals": len([s for s in bot.trade_history if s.signal == "BUY"]),
        "sell_signals": len([s for s in bot.trade_history if s.signal == "SELL"])
    }


@app.get("/config")
async def get_config():
    """Get current bot configuration"""
    return {
        "symbol": bot.symbol,
        "ema_short": bot.ema_short_period,
        "ema_long": bot.ema_long_period,
        "is_running": bot.is_running
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting EMA-Momentum Trading Bot")
    
    # Run FastAPI with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
