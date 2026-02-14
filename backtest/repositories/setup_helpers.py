"""Helper functions for setting up example brokers, assets, and trading rules."""

from decimal import Decimal
from backtest.models import (
    Asset,
    AssetType,
    Broker,
    TradingPair,
    TradingRules,
    LeverageType,
    FeeType,
    FeeTiming,
    Fee,
)
from backtest.repositories import BacktestContext


def setup_example_assets(ctx: BacktestContext) -> dict:
    """
    Setup example assets (currencies, crypto, stocks).
    
    Args:
        ctx: BacktestContext to populate
        
    Returns:
        Dictionary of asset ticker -> Asset object
    """
    assets = {
        # Currencies
        "USD": Asset(
            ticker="USD",
            name="US Dollar",
            asset_type=AssetType.CURRENCY,
            min_unit=Decimal("0.01")
        ),
        "EUR": Asset(
            ticker="EUR",
            name="Euro",
            asset_type=AssetType.CURRENCY,
            min_unit=Decimal("0.01")
        ),
        "BRL": Asset(
            ticker="BRL",
            name="Brazilian Real",
            asset_type=AssetType.CURRENCY,
            min_unit=Decimal("0.01")
        ),
        # Cryptocurrencies
        "BTC": Asset(
            ticker="BTC",
            name="Bitcoin",
            asset_type=AssetType.CRYPTO,
            min_unit=Decimal("0.00000001")
        ),
        "ETH": Asset(
            ticker="ETH",
            name="Ethereum",
            asset_type=AssetType.CRYPTO,
            min_unit=Decimal("0.000001")
        ),
        # Stocks
        "AAPL": Asset(
            ticker="AAPL",
            name="Apple Inc",
            asset_type=AssetType.STOCK,
            min_unit=Decimal("1")
        ),
        "MSFT": Asset(
            ticker="MSFT",
            name="Microsoft Corporation",
            asset_type=AssetType.STOCK,
            min_unit=Decimal("1")
        ),
    }
    
    for asset in assets.values():
        ctx.assets.save(asset)
    
    return assets


def setup_example_brokers(ctx: BacktestContext) -> dict:
    """
    Setup example brokers (Binance, XP, ActivTrades).
    
    Args:
        ctx: BacktestContext to populate
        
    Returns:
        Dictionary of broker code -> Broker object
    """
    brokers = {
        "BINANCE": Broker(
            name="Binance",
            code="BINANCE",
            land="GLOBAL",
            description="Leading crypto exchange"
        ),
        "XP": Broker(
            name="XP Investimentos",
            code="XP",
            land="BR",
            description="Brazilian brokerage firm"
        ),
        "ACTIVTRADES": Broker(
            name="ActivTrades",
            code="ACTIVTRADES",
            land="UK",
            description="Forex and CFD broker"
        ),
    }
    
    for broker in brokers.values():
        ctx.brokers.save(broker)
    
    return brokers


def setup_example_trading_pairs(
    ctx: BacktestContext,
    assets: dict
) -> dict:
    """
    Setup example trading pairs.
    
    Args:
        ctx: BacktestContext to populate
        assets: Dictionary of assets
        
    Returns:
        Dictionary of pair_code -> TradingPair object
    """
    pairs = {
        "BTCUSD": TradingPair(
            base_asset=assets["BTC"],
            quote_asset=assets["USD"],
            contract_size=Decimal("1"),
            min_unit=Decimal("0.001")
        ),
        "ETHUSD": TradingPair(
            base_asset=assets["ETH"],
            quote_asset=assets["USD"],
            contract_size=Decimal("1"),
            min_unit=Decimal("0.01")
        ),
        "AAPLUSD": TradingPair(
            base_asset=assets["AAPL"],
            quote_asset=assets["USD"],
            contract_size=Decimal("1"),
            min_unit=Decimal("1")
        ),
    }
    
    for pair in pairs.values():
        ctx.trading_pairs.save(pair)
    
    return pairs


def setup_binance_rules(
    ctx: BacktestContext,
    broker: Broker,
    pairs: dict
) -> list:
    """
    Setup trading rules for Binance (crypto with leverage).
    
    Args:
        ctx: BacktestContext to populate
        broker: Binance broker object
        pairs: Dictionary of trading pairs
        
    Returns:
        List of TradingRules objects
    """
    rules_list = []
    
    # BTC/USD on Binance - 10x leverage, 0.1% fee
    btc_fee = Fee(
        fee_type=FeeType.PERCENT_OF_NOTIONAL,
        fee_timing=FeeTiming.ON_FILL,
        amount=Decimal("0.001")
    )
    btc_rules = TradingRules(
        broker_id=broker.id,
        pair_code="BTCUSD",
        leverage_type=LeverageType.MARGIN_MULTIPLIER,
        leverage_value=Decimal("10"),
        brokerage_fee=btc_fee,
        min_volume=Decimal("0.001"),
        min_notional_amount=Decimal("10"),
        allows_long=True,
        allows_short=True
    )
    ctx.trading_rules.save(btc_rules)
    rules_list.append(btc_rules)
    
    # ETH/USD on Binance - 5x leverage, 0.1% fee
    eth_fee = Fee(
        fee_type=FeeType.PERCENT_OF_NOTIONAL,
        fee_timing=FeeTiming.ON_FILL,
        amount=Decimal("0.001")
    )
    eth_rules = TradingRules(
        broker_id=broker.id,
        pair_code="ETHUSD",
        leverage_type=LeverageType.MARGIN_MULTIPLIER,
        leverage_value=Decimal("5"),
        brokerage_fee=eth_fee,
        min_volume=Decimal("0.01"),
        min_notional_amount=Decimal("10"),
        allows_long=True,
        allows_short=True
    )
    ctx.trading_rules.save(eth_rules)
    rules_list.append(eth_rules)
    
    return rules_list


def setup_xp_rules(
    ctx: BacktestContext,
    broker: Broker,
    pairs: dict
) -> list:
    """
    Setup trading rules for XP (Brazilian stocks, no leverage).
    
    Args:
        ctx: BacktestContext to populate
        broker: XP broker object
        pairs: Dictionary of trading pairs
        
    Returns:
        List of TradingRules objects
    """
    rules_list = []
    
    # AAPL on XP - no leverage, flat fee
    aapl_fee = Fee(
        fee_type=FeeType.FLAT_PER_TRADE,
        fee_timing=FeeTiming.ON_FILL,
        amount=Decimal("2.50")
    )
    custody_fee = Fee(
        fee_type=FeeType.PERCENT_OF_NOTIONAL,
        fee_timing=FeeTiming.ON_OVERNIGHT_FILLED,
        amount=Decimal("0.0001")  # 0.01% per day
    )
    aapl_rules = TradingRules(
        broker_id=broker.id,
        pair_code="AAPLUSD",
        leverage_type=LeverageType.NO_LEVERAGE,
        leverage_value=Decimal("1"),
        brokerage_fee=aapl_fee,
        custody_fee=custody_fee,
        min_volume=Decimal("1"),
        min_notional_amount=Decimal("1"),
        allows_long=True,
        allows_short=False
    )
    ctx.trading_rules.save(aapl_rules)
    rules_list.append(aapl_rules)
    
    return rules_list


def setup_example_configuration(ctx: BacktestContext) -> dict:
    """
    Setup a complete example configuration.
    
    Args:
        ctx: BacktestContext to populate
        
    Returns:
        Dictionary with all created entities
    """
    assets = setup_example_assets(ctx)
    brokers = setup_example_brokers(ctx)
    pairs = setup_example_trading_pairs(ctx, assets)
    
    binance_rules = setup_binance_rules(ctx, brokers["BINANCE"], pairs)
    xp_rules = setup_xp_rules(ctx, brokers["XP"], pairs)
    
    return {
        "assets": assets,
        "brokers": brokers,
        "pairs": pairs,
        "rules": binance_rules + xp_rules,
    }
