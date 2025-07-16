"""Google Sheets client for stock data updates."""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional, Tuple, Any
from logger import logger
from config import SCOPES, CREDENTIALS_FILE, SPREADSHEET_ID, TICKER_ROW, PRICE_ROW
from datetime import datetime


class SheetsClient:
    """Handles Google Sheets operations."""
    
    def __init__(self, spreadsheet_id: str = SPREADSHEET_ID, credentials_file: str = CREDENTIALS_FILE):
        self.spreadsheet_id = spreadsheet_id
        self.credentials_file = credentials_file
        self._client = None
        self._spreadsheet = None
        self._worksheet = None
    
    @property
    def client(self):
        """Lazy initialization of Google Sheets client."""
        if self._client is None:
            try:
                logger.debug("Initializing Google Sheets client")
                creds = Credentials.from_service_account_file(
                    self.credentials_file, 
                    scopes=SCOPES
                )
                self._client = gspread.authorize(creds)
                logger.info("Google Sheets client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google Sheets client: {e}")
                raise
        return self._client
    
    @property
    def spreadsheet(self):
        """Lazy initialization of spreadsheet."""
        if self._spreadsheet is None:
            try:
                logger.debug(f"Opening spreadsheet: {self.spreadsheet_id}")
                self._spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                logger.info("Spreadsheet opened successfully")
            except Exception as e:
                logger.error(f"Failed to open spreadsheet: {e}")
                raise
        return self._spreadsheet
    
    @property
    def worksheet(self):
        """Lazy initialization of first worksheet."""
        if self._worksheet is None:
            try:
                logger.debug("Getting first worksheet")
                self._worksheet = self.spreadsheet.sheet1
                logger.info("Worksheet accessed successfully")
            except Exception as e:
                logger.error(f"Failed to access worksheet: {e}")
                raise
        return self._worksheet
    
    def get_tickers(self, row: int = TICKER_ROW) -> List[str]:
        """
        Get ticker symbols from the specified row.
        
        Args:
            row: Row number to read tickers from
            
        Returns:
            List of ticker symbols
        """
        try:
            logger.debug(f"Reading tickers from row {row}")
            tickers = self.worksheet.row_values(row)
            # Remove empty strings and clean up
            cleaned_tickers = [ticker.strip() for ticker in tickers if ticker.strip()]
            logger.info(f"Found {len(cleaned_tickers)} tickers")
            return cleaned_tickers
        except Exception as e:
            logger.error(f"Failed to get tickers from row {row}: {e}")
            return []
    
    def update_prices(self, ticker_prices: Dict[str, Optional[float]], 
                     ticker_row: int = TICKER_ROW, price_row: int = PRICE_ROW) -> bool:
        """
        Update prices in the spreadsheet.
        
        Args:
            ticker_prices: Dictionary mapping ticker to price
            ticker_row: Row containing ticker symbols
            price_row: Row to update with prices
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Updating prices for {len(ticker_prices)} tickers")
            
            # Get current tickers from the sheet
            tickers = self.get_tickers(ticker_row)
            
            # Build list of updates
            updates = []
            updated_count = 0
            
            for col_index, ticker in enumerate(tickers, start=1):
                if ticker in ticker_prices and ticker_prices[ticker] is not None:
                    # Convert to 1-based indexing for gspread
                    cell_address = f"{self._get_column_letter(col_index)}{price_row}"
                    updates.append({
                        'range': cell_address,
                        'values': [[ticker_prices[ticker]]]
                    })
                    updated_count += 1
                    logger.debug(f"Prepared update for {ticker}: ${ticker_prices[ticker]} at {cell_address}")
            
            if updates:
                # Batch update for efficiency
                self.worksheet.batch_update(updates)
                logger.info(f"Successfully updated {updated_count} prices")
                return True
            else:
                logger.warning("No valid prices to update")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update prices: {e}")
            return False
    
    def update_cell(self, row: int, col: int, value: Any) -> bool:
        """
        Update a single cell.
        
        Args:
            row: Row number (1-based)
            col: Column number (1-based)  
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Updating cell ({row}, {col}) with value: {value}")
            self.worksheet.update_cell(row, col, value)
            logger.debug(f"Successfully updated cell ({row}, {col})")
            return True
        except Exception as e:
            logger.error(f"Failed to update cell ({row}, {col}): {e}")
            return False
    
    def update_timestamp(self, cell: Tuple[int, int] = None) -> bool:
        """
        Update timestamp in the specified cell.
        
        Args:
            cell: Tuple of (row, col), defaults to config value
            
        Returns:
            True if successful, False otherwise
        """
        from config import TIMESTAMP_CELL
        cell = cell or TIMESTAMP_CELL
        
        timestamp = datetime.now().strftime("%I:%M%p @ %Y-%m-%d")
        logger.debug(f"Updating timestamp: {timestamp}")
        
        return self.update_cell(cell[0], cell[1], timestamp)
    
    def update_exchange_rate(self, rate: float, cell: Tuple[int, int] = None) -> bool:
        """
        Update exchange rate in the specified cell.
        
        Args:
            rate: Exchange rate value
            cell: Tuple of (row, col), defaults to config value
            
        Returns:
            True if successful, False otherwise
        """
        from config import CAD_EXCHANGE_CELL
        cell = cell or CAD_EXCHANGE_CELL
        
        logger.debug(f"Updating exchange rate: {rate}")
        return self.update_cell(cell[0], cell[1], rate)
    
    def _get_column_letter(self, col_num: int) -> str:
        """
        Convert column number to letter (A, B, C, ..., AA, AB, etc.).
        
        Args:
            col_num: Column number (1-based)
            
        Returns:
            Column letter string
        """
        string = ""
        while col_num > 0:
            col_num, remainder = divmod(col_num - 1, 26)
            string = chr(65 + remainder) + string
        return string
    
    def get_sheet_info(self) -> Dict[str, Any]:
        """
        Get basic information about the spreadsheet.
        
        Returns:
            Dictionary with sheet information
        """
        try:
            return {
                'title': self.spreadsheet.title,
                'sheet_count': len(self.spreadsheet.worksheets()),
                'current_sheet': self.worksheet.title,
                'row_count': self.worksheet.row_count,
                'col_count': self.worksheet.col_count
            }
        except Exception as e:
            logger.error(f"Failed to get sheet info: {e}")
            return {}
