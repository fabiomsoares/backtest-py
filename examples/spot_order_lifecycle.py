"""
Example demonstrating SpotOrder lifecycle.

This example shows:
1. Creating spot limit and market orders
2. Filling orders (full and partial)
3. Cancelling orders
4. Order status transitions
"""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from backtest.models.spot_order import SpotOrder
from backtest.models.orders import OrderDirection, OrderStatus
from backtest.repositories.spot_order_repository import SpotOrderRepository


def main():
    """Demonstrate spot order lifecycle."""
    
    # Setup
    broker_id = uuid4()
    agent_id = uuid4()
    account_id = uuid4()
    run_id = uuid4()
    spot_repo = SpotOrderRepository()
    
    print("=" * 70)
    print("Spot Order Lifecycle Example")
    print("=" * 70)
    
    # Create a market order to buy BTC
    print("\n" + "-" * 70)
    print("1. Create Market Order: Buy 1.5 BTC")
    print("-" * 70)
    
    market_order = SpotOrder(
        broker_id=broker_id,
        trading_pair_code="BTCUSD",
        agent_id=agent_id,
        account_id=account_id,
        backtest_run_id=run_id,
        order_number=1,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("1.5"),
        limit_price=None  # Market order
    )
    spot_repo.save(market_order)
    
    print(f"Order: {market_order}")
    print(f"  Type: {'Market' if market_order.is_market_order else 'Limit'}")
    print(f"  Status: {market_order.status.name}")
    print(f"  Direction: {market_order.direction.name}")
    print(f"  Volume: {market_order.volume} BTC")
    
    # Fill the market order
    print("\n" + "-" * 70)
    print("2. Fill Market Order at $50,000/BTC")
    print("-" * 70)
    
    filled_market = market_order.create_filled_copy(
        fill_timestamp=datetime.now(),
        fill_price=Decimal("50000"),
        fill_volume=Decimal("1.5"),
        fee_fill=Decimal("37.50")  # 0.05% fee
    )
    spot_repo.save(filled_market)
    
    print(f"Order: {filled_market}")
    print(f"  Status: {filled_market.status.name}")
    print(f"  Fill Price: ${filled_market.fill_price:,.2f}")
    print(f"  Fill Volume: {filled_market.fill_volume} BTC")
    print(f"  Fill Fee: ${filled_market.fee_fill:,.2f}")
    print(f"  Total Cost: ${filled_market.fill_price * filled_market.fill_volume:,.2f}")
    
    # Create a limit order
    print("\n" + "-" * 70)
    print("3. Create Limit Order: Buy 2.0 BTC @ $48,000")
    print("-" * 70)
    
    limit_order = SpotOrder(
        broker_id=broker_id,
        trading_pair_code="BTCUSD",
        agent_id=agent_id,
        account_id=account_id,
        backtest_run_id=run_id,
        order_number=2,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("2.0"),
        limit_price=Decimal("48000")
    )
    spot_repo.save(limit_order)
    
    print(f"Order: {limit_order}")
    print(f"  Type: {'Market' if limit_order.is_market_order else 'Limit'}")
    print(f"  Limit Price: ${limit_order.limit_price:,.2f}")
    print(f"  Volume: {limit_order.volume} BTC")
    
    # Partial fill
    print("\n" + "-" * 70)
    print("4. Partially Fill Limit Order: 1.2 BTC filled")
    print("-" * 70)
    
    partial_filled = limit_order.create_filled_copy(
        fill_timestamp=datetime.now(),
        fill_price=Decimal("48000"),
        fill_volume=Decimal("1.2"),  # Only 1.2 of 2.0 filled
        fee_fill=Decimal("28.80")
    )
    spot_repo.save(partial_filled)
    
    print(f"Order: {partial_filled}")
    print(f"  Status: {partial_filled.status.name}")
    print(f"  Original Volume: {partial_filled.volume} BTC")
    print(f"  Filled Volume: {partial_filled.fill_volume} BTC")
    print(f"  Remaining Volume: {partial_filled.remaining_volume} BTC")
    print(f"  Fill Rate: {(partial_filled.fill_volume / partial_filled.volume * 100):.1f}%")
    
    # Create another order to cancel
    print("\n" + "-" * 70)
    print("5. Create and Cancel Order: Buy 0.5 BTC @ $49,000")
    print("-" * 70)
    
    cancel_order = SpotOrder(
        broker_id=broker_id,
        trading_pair_code="BTCUSD",
        agent_id=agent_id,
        account_id=account_id,
        backtest_run_id=run_id,
        order_number=3,
        direction=OrderDirection.LONG,
        status=OrderStatus.PENDING,
        create_timestamp=datetime.now(),
        volume=Decimal("0.5"),
        limit_price=Decimal("49000")
    )
    spot_repo.save(cancel_order)
    print(f"Created: {cancel_order}")
    
    # Cancel it
    cancelled_order = cancel_order.create_cancelled_copy(
        cancel_timestamp=datetime.now(),
        cancel_volume=Decimal("0.5"),
        fee_cancel=Decimal("0")  # No cancel fee
    )
    spot_repo.save(cancelled_order)
    
    print(f"Cancelled: {cancelled_order}")
    print(f"  Status: {cancelled_order.status.name}")
    print(f"  Cancelled Volume: {cancelled_order.cancel_volume} BTC")
    
    # Summary
    print("\n" + "=" * 70)
    print("Order Summary")
    print("=" * 70)
    
    all_orders = spot_repo.get_by_account(account_id, run_id)
    
    total_btc_acquired = Decimal("0")
    total_fees = Decimal("0")
    
    for i, order in enumerate(all_orders, 1):
        print(f"\n{i}. Order #{order.order_number} - {order.direction.name} {order.trading_pair_code}")
        print(f"   Status: {order.status.name}")
        
        if order.is_filled:
            print(f"   Filled: {order.fill_volume} @ ${order.fill_price:,.2f}")
            print(f"   Fee: ${order.fee_fill:,.2f}")
            if order.direction == OrderDirection.LONG:
                total_btc_acquired += order.fill_volume or Decimal("0")
            total_fees += order.fee_fill or Decimal("0")
        elif order.is_cancelled:
            print(f"   Cancelled: {order.cancel_volume} BTC")
        else:
            print(f"   Pending: {order.volume} @ ${order.limit_price or 'MARKET':,.2f}")
    
    print("\n" + "=" * 70)
    print(f"Total BTC Acquired: {total_btc_acquired} BTC")
    print(f"Total Fees Paid: ${total_fees:,.2f}")
    print("=" * 70)
    
    # Query examples
    print("\n" + "=" * 70)
    print("Repository Query Examples")
    print("=" * 70)
    
    pending_orders = spot_repo.get_pending_orders(agent_id, run_id)
    print(f"\nPending Orders: {len(pending_orders)}")
    
    filled_orders = spot_repo.get_by_status(OrderStatus.FILLED, run_id)
    print(f"Filled Orders: {len(filled_orders)}")
    
    btc_orders = spot_repo.get_by_trading_pair("BTCUSD", run_id)
    print(f"BTCUSD Orders: {len(btc_orders)}")
    
    print("\n" + "=" * 70)
    print("Example Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
