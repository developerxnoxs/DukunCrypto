#!/usr/bin/env python3
"""
MetaTrader5 Auto-Trading Module
Modul untuk eksekusi order otomatis berdasarkan sinyal analisa teknikal
Mendukung: Windows (native) dan Linux/Docker (via Wine + pymt5linux)
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

try:
    import MetaTrader5 as mt5
    MT5_NATIVE = True
    logger.info("MetaTrader5 native library loaded")
except ImportError:
    MT5_NATIVE = False
    try:
        from pymt5linux import MetaTrader5
        mt5 = None
        logger.info("pymt5linux bridge library available")
    except ImportError:
        mt5 = None
        MetaTrader5 = None
        logger.warning("MetaTrader5 libraries not available")


class TradeAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


@dataclass
class TradeSignal:
    symbol: str
    action: TradeAction
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: Optional[float] = None
    confidence: float = 0.0
    reason: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TradeResult:
    success: bool
    order_id: Optional[int] = None
    message: str = ""
    executed_price: float = 0.0
    volume: float = 0.0
    symbol: str = ""
    action: str = ""


class MT5Trader:
    """
    MetaTrader5 Auto-Trading Class
    Handles connection, order execution, and position management
    """
    
    MT5_SYMBOL_MAP = {
        "BTC": "BTCUSD",
        "ETH": "ETHUSD",
        "SOL": "SOLUSD",
        "BNB": "BNBUSD",
        "XRP": "XRPUSD",
        "ADA": "ADAUSD",
        "DOGE": "DOGEUSD",
        "AVAX": "AVAXUSD",
        "MATIC": "MATICUSD",
        "LINK": "LINKUSD",
        "DOT": "DOTUSD",
        "ATOM": "ATOMUSD",
        "UNI": "UNIUSD",
        "LTC": "LTCUSD",
        "XAUUSD": "XAUUSD",
        "XAGUSD": "XAGUSD",
        "EURUSD": "EURUSD",
        "GBPUSD": "GBPUSD",
        "USDJPY": "USDJPY",
        "USDCHF": "USDCHF",
        "AUDUSD": "AUDUSD",
        "USDCAD": "USDCAD",
        "NZDUSD": "NZDUSD",
        "EURGBP": "EURGBP",
        "EURJPY": "EURJPY",
        "GBPJPY": "GBPJPY",
        "AUDJPY": "AUDJPY",
        "EURAUD": "EURAUD",
        "EURCHF": "EURCHF",
        "USOIL": "USOIL",
    }
    
    def __init__(
        self,
        login: int = None,
        password: str = None,
        server: str = None,
        mt5_path: str = None,
        linux_host: str = "localhost",
        linux_port: int = 8001,
        risk_percent: float = 1.0,
        max_positions: int = 5,
        enable_trading: bool = False
    ):
        self.login = login or int(os.environ.get("MT5_LOGIN", 0))
        self.password = password or os.environ.get("MT5_PASSWORD", "")
        self.server = server or os.environ.get("MT5_SERVER", "")
        self.mt5_path = mt5_path or os.environ.get("MT5_PATH", "")
        self.linux_host = linux_host
        self.linux_port = linux_port
        self.risk_percent = risk_percent
        self.max_positions = max_positions
        self.enable_trading = enable_trading
        self.connected = False
        self.mt5 = None
        
    def initialize(self) -> bool:
        """Initialize connection to MetaTrader5"""
        if not MT5_NATIVE and MetaTrader5 is None:
            logger.error("MetaTrader5 library not available")
            return False
        
        try:
            if MT5_NATIVE:
                if self.mt5_path:
                    init_result = mt5.initialize(self.mt5_path)
                else:
                    init_result = mt5.initialize()
                
                if not init_result:
                    logger.error(f"MT5 initialize() failed, error code: {mt5.last_error()}")
                    return False
                
                if self.login and self.password and self.server:
                    authorized = mt5.login(
                        login=self.login,
                        password=self.password,
                        server=self.server
                    )
                    if not authorized:
                        logger.error(f"MT5 login failed, error code: {mt5.last_error()}")
                        mt5.shutdown()
                        return False
                
                self.mt5 = mt5
                self.connected = True
                logger.info("MT5 initialized successfully (native)")
                return True
            else:
                self.mt5 = MetaTrader5(host=self.linux_host, port=self.linux_port)
                self.connected = True
                logger.info(f"MT5 initialized via bridge ({self.linux_host}:{self.linux_port})")
                return True
                
        except Exception as e:
            logger.error(f"MT5 initialization error: {e}")
            return False
    
    def shutdown(self):
        """Shutdown MT5 connection"""
        if MT5_NATIVE and self.connected:
            mt5.shutdown()
        self.connected = False
        logger.info("MT5 connection closed")
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account information"""
        if not self.connected:
            return None
        
        try:
            info = self.mt5.account_info()
            if info is None:
                return None
            
            return {
                "login": info.login,
                "balance": info.balance,
                "equity": info.equity,
                "margin": info.margin,
                "margin_free": info.margin_free,
                "margin_level": info.margin_level,
                "profit": info.profit,
                "leverage": info.leverage,
                "currency": info.currency,
                "server": info.server,
                "trade_mode": info.trade_mode,
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol information and current price"""
        if not self.connected:
            return None
        
        mt5_symbol = self.MT5_SYMBOL_MAP.get(symbol, symbol)
        
        try:
            info = self.mt5.symbol_info(mt5_symbol)
            if info is None:
                logger.warning(f"Symbol {mt5_symbol} not found")
                return None
            
            tick = self.mt5.symbol_info_tick(mt5_symbol)
            
            return {
                "symbol": mt5_symbol,
                "bid": tick.bid if tick else 0,
                "ask": tick.ask if tick else 0,
                "spread": info.spread,
                "digits": info.digits,
                "trade_contract_size": info.trade_contract_size,
                "volume_min": info.volume_min,
                "volume_max": info.volume_max,
                "volume_step": info.volume_step,
                "trade_mode": info.trade_mode,
            }
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    def get_positions(self, symbol: str = None) -> list:
        """Get open positions"""
        if not self.connected:
            return []
        
        try:
            if symbol:
                mt5_symbol = self.MT5_SYMBOL_MAP.get(symbol, symbol)
                positions = self.mt5.positions_get(symbol=mt5_symbol)
            else:
                positions = self.mt5.positions_get()
            
            if positions is None:
                return []
            
            return [
                {
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": "BUY" if pos.type == 0 else "SELL",
                    "volume": pos.volume,
                    "price_open": pos.price_open,
                    "price_current": pos.price_current,
                    "sl": pos.sl,
                    "tp": pos.tp,
                    "profit": pos.profit,
                    "time": datetime.fromtimestamp(pos.time),
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def calculate_lot_size(
        self,
        symbol: str,
        stop_loss_pips: float,
        risk_percent: float = None
    ) -> float:
        """Calculate lot size based on risk management"""
        if not self.connected:
            return 0.01
        
        risk = risk_percent or self.risk_percent
        
        try:
            account = self.get_account_info()
            symbol_info = self.get_symbol_info(symbol)
            
            if not account or not symbol_info:
                return symbol_info["volume_min"] if symbol_info else 0.01
            
            risk_amount = account["balance"] * (risk / 100)
            
            pip_value = symbol_info["trade_contract_size"] / (10 ** symbol_info["digits"])
            
            if stop_loss_pips > 0:
                lot_size = risk_amount / (stop_loss_pips * pip_value)
            else:
                lot_size = symbol_info["volume_min"]
            
            lot_size = max(symbol_info["volume_min"], lot_size)
            lot_size = min(symbol_info["volume_max"], lot_size)
            
            step = symbol_info["volume_step"]
            lot_size = round(lot_size / step) * step
            
            return round(lot_size, 2)
            
        except Exception as e:
            logger.error(f"Error calculating lot size: {e}")
            return 0.01
    
    def execute_trade(
        self,
        signal: TradeSignal,
        volume: float = None,
        deviation: int = 20,
        magic: int = 234000,
        comment: str = "AI Trading Bot"
    ) -> TradeResult:
        """Execute a trade based on signal"""
        if not self.connected:
            return TradeResult(
                success=False,
                message="Not connected to MT5"
            )
        
        if not self.enable_trading:
            return TradeResult(
                success=False,
                message="Trading is disabled. Set enable_trading=True to execute trades."
            )
        
        if signal.action == TradeAction.HOLD:
            return TradeResult(
                success=False,
                message="Signal is HOLD, no trade executed"
            )
        
        positions = self.get_positions()
        if len(positions) >= self.max_positions:
            return TradeResult(
                success=False,
                message=f"Max positions ({self.max_positions}) reached"
            )
        
        mt5_symbol = self.MT5_SYMBOL_MAP.get(signal.symbol, signal.symbol)
        symbol_info = self.get_symbol_info(signal.symbol)
        
        if not symbol_info:
            return TradeResult(
                success=False,
                message=f"Symbol {signal.symbol} not available"
            )
        
        if volume is None:
            sl_pips = abs(signal.entry_price - signal.stop_loss) * (10 ** symbol_info["digits"])
            volume = self.calculate_lot_size(signal.symbol, sl_pips)
        
        if signal.action == TradeAction.BUY:
            order_type = self.mt5.ORDER_TYPE_BUY if MT5_NATIVE else 0
            price = symbol_info["ask"]
        else:
            order_type = self.mt5.ORDER_TYPE_SELL if MT5_NATIVE else 1
            price = symbol_info["bid"]
        
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL if MT5_NATIVE else 1,
            "symbol": mt5_symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": signal.stop_loss,
            "tp": signal.take_profit_1,
            "deviation": deviation,
            "magic": magic,
            "comment": comment,
            "type_time": self.mt5.ORDER_TIME_GTC if MT5_NATIVE else 0,
            "type_filling": self.mt5.ORDER_FILLING_IOC if MT5_NATIVE else 1,
        }
        
        try:
            logger.info(f"Executing {signal.action.value} order for {mt5_symbol}")
            logger.info(f"Volume: {volume}, Price: {price}, SL: {signal.stop_loss}, TP: {signal.take_profit_1}")
            
            result = self.mt5.order_send(request)
            
            if result is None:
                error = self.mt5.last_error() if MT5_NATIVE else "Unknown error"
                return TradeResult(
                    success=False,
                    message=f"Order failed: {error}"
                )
            
            if result.retcode != 10009:
                return TradeResult(
                    success=False,
                    message=f"Order failed with code {result.retcode}: {result.comment}"
                )
            
            logger.info(f"Order executed successfully: #{result.order}")
            
            return TradeResult(
                success=True,
                order_id=result.order,
                message=f"Order #{result.order} executed successfully",
                executed_price=result.price,
                volume=result.volume,
                symbol=mt5_symbol,
                action=signal.action.value
            )
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return TradeResult(
                success=False,
                message=f"Trade execution error: {str(e)}"
            )
    
    def close_position(
        self,
        ticket: int,
        volume: float = None,
        deviation: int = 20,
        magic: int = 234000
    ) -> TradeResult:
        """Close an open position"""
        if not self.connected:
            return TradeResult(success=False, message="Not connected to MT5")
        
        if not self.enable_trading:
            return TradeResult(
                success=False,
                message="Trading is disabled"
            )
        
        try:
            positions = self.mt5.positions_get(ticket=ticket)
            if not positions:
                return TradeResult(
                    success=False,
                    message=f"Position #{ticket} not found"
                )
            
            position = positions[0]
            
            if volume is None:
                volume = position.volume
            
            if position.type == 0:
                order_type = self.mt5.ORDER_TYPE_SELL if MT5_NATIVE else 1
                price = self.mt5.symbol_info_tick(position.symbol).bid
            else:
                order_type = self.mt5.ORDER_TYPE_BUY if MT5_NATIVE else 0
                price = self.mt5.symbol_info_tick(position.symbol).ask
            
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL if MT5_NATIVE else 1,
                "symbol": position.symbol,
                "volume": volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": deviation,
                "magic": magic,
                "comment": "Close by AI Bot",
                "type_time": self.mt5.ORDER_TIME_GTC if MT5_NATIVE else 0,
                "type_filling": self.mt5.ORDER_FILLING_IOC if MT5_NATIVE else 1,
            }
            
            result = self.mt5.order_send(request)
            
            if result is None or result.retcode != 10009:
                return TradeResult(
                    success=False,
                    message=f"Close failed: {result.comment if result else 'Unknown error'}"
                )
            
            return TradeResult(
                success=True,
                order_id=result.order,
                message=f"Position #{ticket} closed successfully",
                executed_price=result.price,
                volume=volume,
                symbol=position.symbol,
                action="CLOSE"
            )
            
        except Exception as e:
            logger.error(f"Close position error: {e}")
            return TradeResult(success=False, message=str(e))
    
    def modify_position(
        self,
        ticket: int,
        stop_loss: float = None,
        take_profit: float = None
    ) -> TradeResult:
        """Modify stop loss and take profit of an open position"""
        if not self.connected:
            return TradeResult(success=False, message="Not connected to MT5")
        
        try:
            positions = self.mt5.positions_get(ticket=ticket)
            if not positions:
                return TradeResult(success=False, message=f"Position #{ticket} not found")
            
            position = positions[0]
            
            request = {
                "action": self.mt5.TRADE_ACTION_SLTP if MT5_NATIVE else 6,
                "symbol": position.symbol,
                "position": ticket,
                "sl": stop_loss if stop_loss else position.sl,
                "tp": take_profit if take_profit else position.tp,
            }
            
            result = self.mt5.order_send(request)
            
            if result is None or result.retcode != 10009:
                return TradeResult(
                    success=False,
                    message=f"Modify failed: {result.comment if result else 'Unknown error'}"
                )
            
            return TradeResult(
                success=True,
                order_id=ticket,
                message=f"Position #{ticket} modified successfully",
                symbol=position.symbol,
                action="MODIFY"
            )
            
        except Exception as e:
            logger.error(f"Modify position error: {e}")
            return TradeResult(success=False, message=str(e))


def parse_analysis_signal(analysis_text: str, symbol: str, current_price: float) -> Optional[TradeSignal]:
    """
    Parse AI analysis text to extract trading signal
    Returns TradeSignal object or None if parsing fails
    """
    import re
    
    signal_text = analysis_text.upper()
    
    action = TradeAction.HOLD
    if "BELI" in signal_text or "BUY" in signal_text or "BULLISH" in signal_text:
        action = TradeAction.BUY
    elif "JUAL" in signal_text or "SELL" in signal_text or "BEARISH" in signal_text:
        action = TradeAction.SELL
    
    entry_price = current_price
    stop_loss = 0.0
    take_profit_1 = 0.0
    take_profit_2 = 0.0
    confidence = 50.0
    
    entry_patterns = [
        r"ENTRY[:\s]+\$?([\d,\.]+)",
        r"HARGA MASUK[:\s]+\$?([\d,\.]+)",
        r"MASUK[:\s]+\$?([\d,\.]+)",
        r"BUY AT[:\s]+\$?([\d,\.]+)",
        r"SELL AT[:\s]+\$?([\d,\.]+)",
    ]
    
    sl_patterns = [
        r"STOP LOSS[:\s]+\$?([\d,\.]+)",
        r"SL[:\s]+\$?([\d,\.]+)",
        r"STOPLOSS[:\s]+\$?([\d,\.]+)",
    ]
    
    tp_patterns = [
        r"TARGET PROFIT 1[:\s]+\$?([\d,\.]+)",
        r"TP1[:\s]+\$?([\d,\.]+)",
        r"TAKE PROFIT 1[:\s]+\$?([\d,\.]+)",
        r"TARGET 1[:\s]+\$?([\d,\.]+)",
    ]
    
    tp2_patterns = [
        r"TARGET PROFIT 2[:\s]+\$?([\d,\.]+)",
        r"TP2[:\s]+\$?([\d,\.]+)",
        r"TAKE PROFIT 2[:\s]+\$?([\d,\.]+)",
        r"TARGET 2[:\s]+\$?([\d,\.]+)",
    ]
    
    confidence_patterns = [
        r"CONFIDENCE[:\s]+(\d+)%?",
        r"KEPERCAYAAN[:\s]+(\d+)%?",
        r"PROBABILITY[:\s]+(\d+)%?",
    ]
    
    def extract_value(patterns: list, text: str) -> float:
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", "")
                try:
                    return float(value)
                except ValueError:
                    continue
        return 0.0
    
    entry_price = extract_value(entry_patterns, analysis_text) or current_price
    stop_loss = extract_value(sl_patterns, analysis_text)
    take_profit_1 = extract_value(tp_patterns, analysis_text)
    take_profit_2 = extract_value(tp2_patterns, analysis_text)
    confidence = extract_value(confidence_patterns, analysis_text) or 50.0
    
    if stop_loss == 0.0:
        if action == TradeAction.BUY:
            stop_loss = entry_price * 0.98
        elif action == TradeAction.SELL:
            stop_loss = entry_price * 1.02
    
    if take_profit_1 == 0.0:
        if action == TradeAction.BUY:
            take_profit_1 = entry_price * 1.03
        elif action == TradeAction.SELL:
            take_profit_1 = entry_price * 0.97
    
    return TradeSignal(
        symbol=symbol,
        action=action,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit_1=take_profit_1,
        take_profit_2=take_profit_2 if take_profit_2 > 0 else None,
        confidence=confidence,
        reason=analysis_text[:500]
    )


class AutoTrader:
    """
    Auto-Trading Manager
    Manages automated trading based on analysis signals
    """
    
    def __init__(
        self,
        trader: MT5Trader,
        min_confidence: float = 60.0,
        auto_execute: bool = False,
        notify_callback=None
    ):
        self.trader = trader
        self.min_confidence = min_confidence
        self.auto_execute = auto_execute
        self.notify_callback = notify_callback
        self.pending_signals: list[TradeSignal] = []
        self.executed_trades: list[TradeResult] = []
    
    async def process_signal(
        self,
        analysis_text: str,
        symbol: str,
        current_price: float
    ) -> Tuple[TradeSignal, Optional[TradeResult]]:
        """Process an analysis result and optionally execute trade"""
        
        signal = parse_analysis_signal(analysis_text, symbol, current_price)
        
        if signal is None:
            return None, None
        
        result = None
        
        if signal.action != TradeAction.HOLD and signal.confidence >= self.min_confidence:
            if self.auto_execute and self.trader.enable_trading:
                result = self.trader.execute_trade(signal)
                self.executed_trades.append(result)
                
                if self.notify_callback:
                    await self.notify_callback(signal, result)
            else:
                self.pending_signals.append(signal)
                if self.notify_callback:
                    await self.notify_callback(signal, None)
        
        return signal, result
    
    def get_pending_signals(self) -> list[TradeSignal]:
        """Get list of pending (unexecuted) signals"""
        return self.pending_signals.copy()
    
    def clear_pending_signals(self):
        """Clear pending signals"""
        self.pending_signals.clear()
    
    def get_trade_history(self) -> list[TradeResult]:
        """Get executed trade history"""
        return self.executed_trades.copy()
    
    def execute_pending_signal(self, index: int = 0) -> Optional[TradeResult]:
        """Execute a pending signal by index"""
        if not self.pending_signals or index >= len(self.pending_signals):
            return None
        
        signal = self.pending_signals.pop(index)
        result = self.trader.execute_trade(signal)
        self.executed_trades.append(result)
        return result
