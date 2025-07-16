"""Stock data fetching functionality."""

import yfinance as yf
from typing import Optional, Dict, Any, List
from logger import logger
from config import MAX_RETRIES, RETRY_DELAY_SECONDS
import time


class StockDataFetcher:
    """Handles fetching stock data from Yahoo Finance."""
    
    def __init__(self):
        self.session = None
        
    def get_ticker_price(self, ticker: str) -> Optional[float]:
        """
        Get current price for a ticker symbol.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Current price or None if unable to fetch
        """
        if not ticker or ticker.strip() == '':
            logger.warning(f"Empty ticker symbol provided")
            return None
            
        ticker = ticker.strip().upper()
        logger.debug(f"Fetching price for ticker: {ticker}")
        
        for attempt in range(MAX_RETRIES):
            try:
                ticker_obj = yf.Ticker(ticker)
                info = ticker_obj.info
                
                if not info:
                    logger.warning(f"No info available for ticker {ticker}")
                    continue
                
                # Try different price fields in order of preference
                price = self._extract_price_from_info(info)
                
                if price is not None:
                    logger.debug(f"Successfully fetched price for {ticker}: ${price}")
                    return price
                    
                logger.warning(f"No valid price found for {ticker} in attempt {attempt + 1}")
                
            except Exception as e:
                logger.error(f"Error fetching data for {ticker} (attempt {attempt + 1}): {e}")
                
            if attempt < MAX_RETRIES - 1:
                logger.debug(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                time.sleep(RETRY_DELAY_SECONDS)
        
        logger.error(f"Failed to fetch price for {ticker} after {MAX_RETRIES} attempts")
        return None
    
    def _extract_price_from_info(self, info: Dict[str, Any]) -> Optional[float]:
        """
        Extract price from ticker info using multiple fallback methods.
        
        Args:
            info: Ticker info dictionary from yfinance
            
        Returns:
            Price as float or None
        """
        # Priority order for price fields
        price_fields = [
            'currentPrice',
            'regularMarketPrice', 
            'previousClose',
            'open'
        ]
        
        # Try direct price fields first
        for field in price_fields:
            if field in info and info[field] is not None:
                try:
                    price = float(info[field])
                    if price > 0:
                        return price
                except (ValueError, TypeError):
                    continue
        
        # Try bid/ask average as fallback
        if 'bid' in info and 'ask' in info:
            try:
                bid = float(info['bid']) if info['bid'] is not None else 0
                ask = float(info['ask']) if info['ask'] is not None else 0
                if bid > 0 and ask > 0:
                    return (bid + ask) / 2
            except (ValueError, TypeError):
                pass
        
        return None
    
    def get_exchange_rate(self, currency_pair: str = "CAD=X") -> Optional[float]:
        """
        Get exchange rate for currency pair.
        
        Args:
            currency_pair: Currency pair symbol (default: CAD=X)
            
        Returns:
            Exchange rate or None if unable to fetch
        """
        logger.debug(f"Fetching exchange rate for {currency_pair}")
        
        try:
            ticker_obj = yf.Ticker(currency_pair)
            info = ticker_obj.info
            
            if info and 'previousClose' in info:
                rate = float(info['previousClose'])
                logger.debug(f"Exchange rate for {currency_pair}: {rate}")
                return rate
                
        except Exception as e:
            logger.error(f"Error fetching exchange rate for {currency_pair}: {e}")
        
        logger.warning(f"Could not fetch exchange rate for {currency_pair}")
        return None
    
    def get_multiple_prices(self, tickers: List[str]) -> Dict[str, Optional[float]]:
        """
        Get prices for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dictionary mapping ticker to price (or None if failed)
        """
        logger.info(f"Fetching prices for {len(tickers)} tickers")
        results = {}
        
        for ticker in tickers:
            if ticker and ticker.strip():
                results[ticker] = self.get_ticker_price(ticker)
            else:
                results[ticker] = None
                
        successful_fetches = sum(1 for price in results.values() if price is not None)
        logger.info(f"Successfully fetched {successful_fetches}/{len(tickers)} prices")
        
        return results
