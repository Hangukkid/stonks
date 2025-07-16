#!/usr/bin/env python3
"""
Test script for the refactored stock data fetcher.
This script tests individual components without running the full application.
"""

import sys
from logger import logger
from stock_fetcher import StockDataFetcher
from sheets_client import SheetsClient
from scheduler import UpdateScheduler


def test_stock_fetcher():
    """Test the stock data fetching functionality."""
    logger.info("Testing StockDataFetcher...")
    
    fetcher = StockDataFetcher()
    
    # Test single ticker
    test_tickers = ['AAPL', 'GOOGL', 'INVALID_TICKER']
    
    for ticker in test_tickers:
        price = fetcher.get_ticker_price(ticker)
        if price:
            logger.info(f"✓ {ticker}: ${price:.2f}")
        else:
            logger.warning(f"✗ {ticker}: Failed to fetch price")
    
    # Test multiple tickers
    logger.info("Testing multiple ticker fetch...")
    prices = fetcher.get_multiple_prices(['AAPL', 'MSFT'])
    logger.info(f"Multiple prices result: {prices}")
    
    # Test exchange rate
    cad_rate = fetcher.get_exchange_rate()
    if cad_rate:
        logger.info(f"✓ CAD/USD rate: {cad_rate:.4f}")
    else:
        logger.warning("✗ Failed to fetch CAD exchange rate")


def test_sheets_client():
    """Test the Google Sheets client (requires valid credentials)."""
    logger.info("Testing SheetsClient...")
    
    try:
        client = SheetsClient()
        
        # Test getting sheet info
        info = client.get_sheet_info()
        if info:
            logger.info(f"✓ Connected to sheet: {info.get('title', 'Unknown')}")
            logger.info(f"  - Rows: {info.get('row_count', 'Unknown')}")
            logger.info(f"  - Columns: {info.get('col_count', 'Unknown')}")
        else:
            logger.warning("✗ Failed to get sheet info")
        
        # Test getting tickers (read-only operation)
        tickers = client.get_tickers()
        if tickers:
            logger.info(f"✓ Found {len(tickers)} tickers: {tickers[:5]}...")
        else:
            logger.warning("✗ No tickers found or failed to read")
            
    except Exception as e:
        logger.error(f"✗ SheetsClient test failed: {e}")
        logger.info("This is expected if credentials.json is not set up")


def test_scheduler():
    """Test the update scheduler."""
    logger.info("Testing UpdateScheduler...")
    
    scheduler = UpdateScheduler()
    
    # Test market status
    status = scheduler.get_market_status()
    logger.info(f"✓ Market status: {status}")
    
    # Test update timing
    should_update = scheduler.should_update(force=True)
    logger.info(f"✓ Force update check: {should_update}")
    
    next_update = scheduler.get_next_update_time()
    if next_update:
        logger.info(f"✓ Next update scheduled for: {next_update.strftime('%H:%M:%S')}")


def main():
    """Run all tests."""
    logger.info("=" * 50)
    logger.info("Running refactored stock fetcher tests")
    logger.info("=" * 50)
    
    try:
        # Test individual components
        test_stock_fetcher()
        logger.info("-" * 30)
        
        test_scheduler()
        logger.info("-" * 30)
        
        test_sheets_client()
        logger.info("-" * 30)
        
        logger.info("✓ All tests completed")
        
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
