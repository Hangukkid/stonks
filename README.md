# Stock Data Fetcher

A Python application that fetches real-time stock prices from Yahoo Finance and updates them in a Google Sheets spreadsheet. This is a refactored and optimized version of the original stock data fetcher with improved error handling, logging, modular architecture, and better scheduling.

## Features

- **Real-time stock price fetching** from Yahoo Finance using yfinance
- **Google Sheets integration** for automatic data updates
- **Intelligent scheduling** that respects market hours
- **Robust error handling** with comprehensive logging
- **Modular architecture** for easy maintenance and extension
- **Configuration management** with environment variable support
- **Graceful shutdown** with signal handling
- **Batch operations** for efficient API usage
- **Exchange rate updates** (CAD/USD by default)

## Architecture

The application has been refactored into several modules:

```
├── main.py              # Main application entry point
├── config.py            # Configuration settings
├── logger.py            # Logging configuration
├── stock_fetcher.py     # Stock data fetching logic
├── sheets_client.py     # Google Sheets client
├── scheduler.py         # Update scheduling logic
├── credentials.json     # Google Sheets API credentials
└── requirements.txt  # Updated dependencies
```

## Installation

1. **Clone the repository** or download the files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up Google Sheets API credentials**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Sheets API
   - Create service account credentials
   - Download the JSON file and save it as `credentials.json`
   - Share your Google Sheet with the service account email

## Configuration

The application can be configured through environment variables or by modifying `config.py`:

### Environment Variables

- `SPREADSHEET_ID`: Your Google Sheets spreadsheet ID
- `CREDENTIALS_FILE`: Path to your Google Sheets credentials file
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Key Configuration Options

- **Market Hours**: 9 AM to 4 PM (configurable)
- **Update Interval**: Every 10 minutes during market hours
- **Retry Logic**: 3 attempts with 5-second delays
- **Special Tickers**: Skip 'Total', 'Unused', and empty cells

## Usage

### Running the Application

**Continuous monitoring** (default):
```bash
python main.py
```

**Single update** (run once and exit):
```bash
python main.py --once
```

**Debug mode** (verbose logging):
```bash
python main.py --debug
```

### Google Sheets Setup

1. Create a Google Sheets spreadsheet
2. Put your ticker symbols in **Row 1** (starting from column B)
3. The application will update prices in **Row 3**
4. Timestamp will be updated in cell **A1**
5. CAD exchange rate will be updated in cell **A100**

Example spreadsheet layout:
```
A1: [Timestamp]    B1: AAPL    C1: GOOGL    D1: MSFT
A2: 
A3:                B3: [Price] C3: [Price]  D3: [Price]
```

## Improvements Over Original Code

### 1. **Error Handling**
- Specific exception handling instead of generic try-catch
- Detailed error logging with stack traces
- Graceful degradation when some operations fail

### 2. **Logging System**
- Structured logging with different levels
- Configurable log formatting
- Debug information for troubleshooting

### 3. **Modular Architecture**
- Separated concerns into different modules
- Easy to test individual components
- Better code organization and maintenance

### 4. **Configuration Management**
- Centralized configuration in `config.py`
- Environment variable support
- No more magic numbers in code

### 5. **Better Scheduling**
- Intelligent market hours detection
- Configurable update intervals
- Proper time calculations

### 6. **Data Validation**
- Input validation for ticker symbols
- Price validation before updating sheets
- Better handling of API response variations

### 7. **Batch Operations**
- Efficient Google Sheets batch updates
- Reduced API calls
- Better performance for large ticker lists

### 8. **Signal Handling**
- Graceful shutdown on Ctrl+C
- Proper cleanup of resources
- Signal handling for production deployments

## Monitoring and Troubleshooting

### Logs
The application provides detailed logging:
- **INFO**: General operation status
- **WARNING**: Non-critical issues (failed price fetches)
- **ERROR**: Critical failures
- **DEBUG**: Detailed troubleshooting information

### Common Issues

1. **"No tickers found"**: Check that Row 1 contains ticker symbols
2. **"Failed to update prices"**: Verify Google Sheets permissions
3. **"Failed to fetch price"**: Check ticker symbol validity
4. **Authentication errors**: Verify credentials.json file

### Market Hours
The application automatically detects market hours and will wait until market opens if run outside trading hours.

## Development

### Running Tests
```bash
# Run a single update for testing
python main.py --once --debug
```

### Adding New Features
The modular architecture makes it easy to extend:
- Add new data sources in `stock_fetcher.py`
- Implement new scheduling logic in `scheduler.py`
- Add new sheet operations in `sheets_client.py`

## Migration from Original Code

To migrate from the original `getStock.py`:

1. **Backup your original files**
2. **Install new dependencies**: `pip install -r requirements.txt`
3. **Update your configuration** in `config.py` if needed
4. **Run the new application**: `python main.py`

The new version maintains compatibility with your existing Google Sheets format.

## Performance Improvements

- **Reduced API calls** through batch operations
- **Better retry logic** with exponential backoff
- **Efficient scheduling** that respects rate limits
- **Memory optimization** with lazy loading
- **Connection reuse** for Google Sheets client

## Security Considerations

- Keep `credentials.json` secure and never commit to version control
- Use environment variables for sensitive configuration
- Regular rotation of service account keys
- Minimal required permissions for Google Sheets API

## Contributing

To contribute to this project:
1. Follow the existing code structure
2. Add appropriate logging
3. Include error handling
4. Update documentation
5. Test thoroughly before submitting

## License

This project is provided as-is for educational and personal use.
