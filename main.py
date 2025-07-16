"""
Main application for fetching stock data and updating Google Sheets.

This is the refactored version of the original getStock.py with improved:
- Error handling and logging
- Modular architecture
- Configuration management
- Better scheduling
- Data validation
"""

import sys
import signal
from typing import Set
from logger import logger
from config import SKIP_TICKERS
from stock_fetcher import StockDataFetcher
from sheets_client import SheetsClient
from scheduler import UpdateScheduler


class StockDataApp:
    """Main application class for stock data fetching and updating."""
    
    def __init__(self):
        self.stock_fetcher = StockDataFetcher()
        self.sheets_client = SheetsClient()
        self.scheduler = UpdateScheduler()
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _filter_tickers(self, tickers: list) -> list:
        """
        Filter out tickers that should be skipped.
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Filtered list of valid tickers
        """
        valid_tickers = []
        skip_set = set(SKIP_TICKERS)
        
        for ticker in tickers:
            ticker_clean = ticker.strip()
            if ticker_clean and ticker_clean not in skip_set and ticker_clean.find("@") == -1:
                valid_tickers.append(ticker_clean)
            else:
                logger.debug(f"Skipping ticker: '{ticker}'")
        
        return valid_tickers
    
    def perform_update(self) -> bool:
        """
        Perform a single update cycle.
        
        Returns:
            True if update was successful, False otherwise
        """
        try:
            logger.info("Starting update cycle")
            
            # Get tickers from spreadsheet
            all_tickers = self.sheets_client.get_tickers()
            if not all_tickers:
                logger.warning("No tickers found in spreadsheet")
                return False
            
            # Filter valid tickers
            valid_tickers = self._filter_tickers(all_tickers)
            print(valid_tickers)
            if not valid_tickers:
                logger.warning("No valid tickers to process")
                return False
            
            logger.info(f"Processing {len(valid_tickers)} valid tickers")
            
            # Fetch stock prices
            ticker_prices = self.stock_fetcher.get_multiple_prices(valid_tickers)
            
            # Count successful fetches
            successful_prices = {k: v for k, v in ticker_prices.items() if v is not None}
            failed_tickers = [k for k, v in ticker_prices.items() if v is None]
            
            if failed_tickers:
                logger.warning(f"Failed to fetch prices for: {failed_tickers}")
            
            if not successful_prices:
                logger.error("No prices were successfully fetched")
                return False
            
            # Update prices in spreadsheet
            price_update_success = self.sheets_client.update_prices(ticker_prices)
            
            if not price_update_success:
                logger.error("Failed to update prices in spreadsheet")
                return False
            
            # Update exchange rate
            exchange_rate = self.stock_fetcher.get_exchange_rate("CAD=X")
            if exchange_rate is not None:
                self.sheets_client.update_exchange_rate(exchange_rate)
                logger.info(f"Updated CAD exchange rate: {exchange_rate}")
            else:
                logger.warning("Failed to fetch CAD exchange rate")
            
            # Update timestamp
            timestamp_success = self.sheets_client.update_timestamp()
            if not timestamp_success:
                logger.warning("Failed to update timestamp")
            
            # Mark update as completed
            self.scheduler.mark_update_completed()
            
            success_rate = len(successful_prices) / len(valid_tickers) * 100
            logger.info(f"Update cycle completed successfully ({success_rate:.1f}% success rate)")
            
            return True
            
        except Exception as e:
            logger.error(f"Update cycle failed with error: {e}", exc_info=True)
            return False
    
    def run(self):
        """Main application loop."""
        logger.info("Stock Data Application starting up")
        
        try:
            # Display sheet info
            sheet_info = self.sheets_client.get_sheet_info()
            if sheet_info:
                logger.info(f"Connected to spreadsheet: {sheet_info.get('title', 'Unknown')}")
            
            # Display market status
            market_status = self.scheduler.get_market_status()
            logger.info(f"Market status: {'Open' if market_status['is_market_open'] else 'Closed'}")
            
            # Main loop
            while self.running:
                try:
                    # Check if we should perform an update
                    if self.scheduler.should_update():
                        success = self.perform_update()
                        if not success:
                            logger.warning("Update cycle failed, will retry at next interval")
                    
                    # Wait until next update time
                    if self.running:  # Check if we're still supposed to be running
                        self.scheduler.wait_until_next_update()
                        
                except KeyboardInterrupt:
                    logger.info("Received keyboard interrupt, shutting down...")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                    # Continue running but wait a bit before retrying
                    if self.running:
                        logger.info("Waiting 60 seconds before retrying...")
                        import time
                        time.sleep(60)
        
        except Exception as e:
            logger.error(f"Fatal error in application: {e}", exc_info=True)
            return 1
        
        finally:
            logger.info("Stock Data Application shutting down")
        
        return 0
    
    def run_once(self) -> bool:
        """
        Run a single update cycle without scheduling.
        Useful for testing or manual runs.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Running single update cycle")
        return self.perform_update()


def main():
    """Entry point for the application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Stock Data Fetcher and Google Sheets Updater')
    parser.add_argument('--once', action='store_true', 
                       help='Run once and exit instead of continuous monitoring')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Adjust log level if debug is requested
    if args.debug:
        logger.setLevel('DEBUG')
        logger.info("Debug logging enabled")
    
    # Create and run the application
    app = StockDataApp()
    
    try:
        if args.once:
            # Run once and exit
            success = app.run_once()
            return 0 if success else 1
        else:
            # Run continuously
            return app.run()
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
