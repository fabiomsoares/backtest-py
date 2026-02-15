"""Tests for Portfolio class."""

import pytest
from datetime import datetime
from backtest.core.portfolio import Portfolio
from backtest.core.order import Order, OrderType, OrderSide


def test_portfolio_initialization():
    """Test Portfolio initialization."""
    portfolio = Portfolio(initial_capital=100000)
    
    assert portfolio.initial_capital == 100000
    assert portfolio.cash == 100000
    assert len(portfolio.positions) == 0
    assert portfolio.total_value == 100000


def test_portfolio_execute_buy_order():
    """Test executing a buy order."""
    portfolio = Portfolio(initial_capital=100000)
    order = Order(
        symbol="AAPL",
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=100,
    )
    
    success = portfolio.execute_order(order, fill_price=150.0)
    
    assert success
    assert order.is_filled
    assert "AAPL" in portfolio.positions
    assert portfolio.positions["AAPL"].quantity == 100
    assert portfolio.cash < 100000  # Cash reduced


def test_portfolio_execute_sell_order():
    """Test executing a sell order."""
    portfolio = Portfolio(initial_capital=100000)
    
    # First buy
    buy_order = Order(
        symbol="AAPL",
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=100,
    )
    portfolio.execute_order(buy_order, fill_price=150.0)
    
    # Then sell
    sell_order = Order(
        symbol="AAPL",
        order_type=OrderType.MARKET,
        side=OrderSide.SELL,
        quantity=50,
    )
    success = portfolio.execute_order(sell_order, fill_price=155.0)
    
    assert success
    assert portfolio.positions["AAPL"].quantity == 50


def test_portfolio_insufficient_cash():
    """Test handling insufficient cash."""
    portfolio = Portfolio(initial_capital=1000)
    order = Order(
        symbol="AAPL",
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=100,
    )
    
    success = portfolio.execute_order(order, fill_price=150.0)
    
    assert not success
    assert order.status.value == "rejected"


def test_portfolio_total_value():
    """Test calculating total portfolio value."""
    portfolio = Portfolio(initial_capital=100000)
    
    # Buy some shares
    order = Order(
        symbol="AAPL",
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=100,
    )
    portfolio.execute_order(order, fill_price=150.0)
    
    # Update prices
    portfolio.update_prices({"AAPL": 160.0})
    
    total_value = portfolio.total_value
    assert total_value > portfolio.initial_capital  # Should have gained value


def test_portfolio_transaction_history():
    """Test transaction history tracking."""
    portfolio = Portfolio(initial_capital=100000)
    
    order = Order(
        symbol="AAPL",
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=100,
    )
    portfolio.execute_order(order, fill_price=150.0)
    
    assert len(portfolio.transaction_history) == 1
    txn = portfolio.transaction_history[0]
    assert txn['symbol'] == "AAPL"
    assert txn['side'] == "BUY"
    assert txn['quantity'] == 100
