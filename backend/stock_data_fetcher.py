import os
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import json
import time
import random  # For fallback simulated data when needed

class StockDataFetcher:
    """
    Fetches stock price data from Yahoo Finance API and provides methods
    for correlating stock price movements with sentiment data
    """
    
    def __init__(self):
        """Initialize the stock data fetcher"""
        logging.info("StockDataFetcher initialized with Yahoo Finance")
    
    def get_daily_prices(self, symbol, days=30):
        """
        Get daily stock prices for a given symbol using Yahoo Finance
        
        Args:
            symbol (str): Stock ticker symbol (e.g., AAPL, MSFT)
            days (int): Number of days of historical data to return
            
        Returns:
            list: List of daily price data dictionaries
        """
        try:
            # Calculate time period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 5)  # Add buffer for weekends/holidays
            
            # Fetch data from Yahoo Finance
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date.strftime('%Y-%m-%d'), 
                                end=end_date.strftime('%Y-%m-%d'),
                                interval="1d")
            
            # If data is empty or we got an error, use simulation
            if hist.empty:
                logging.warning(f"No data found for {symbol}")
                return self._get_simulated_price_data(symbol, days)
            
            # Convert to list of dictionaries with formatted dates
            result = []
            for date, row in hist.iterrows():
                # Get date as string
                date_str = date.strftime('%Y-%m-%d')
                
                price_data = {
                    'date': date_str,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                result.append(price_data)
            
            # Sort by date (most recent first)
            result.sort(key=lambda x: x['date'], reverse=True)
            
            # Limit to requested number of days
            return result[:days]
            
        except Exception as e:
            logging.error(f"Error fetching stock data for {symbol}: {e}")
            return self._get_simulated_price_data(symbol, days)
    
    def get_intraday_prices(self, symbol, interval='60m'):
        """
        Get intraday stock prices for a given symbol using Yahoo Finance
        
        Args:
            symbol (str): Stock ticker symbol (e.g., AAPL, MSFT)
            interval (str): Time interval between data points (1m, 5m, 15m, 30m, 60m)
            
        Returns:
            list: List of intraday price data dictionaries
        """
        try:
            # Map interval format from Alpha Vantage to Yahoo Finance
            interval_map = {'1min': '1m', '5min': '5m', '15min': '15m', '30min': '30m', '60min': '60m'}
            yf_interval = interval_map.get(interval, interval)
            
            # Get data for the last 7 days (Yahoo limit for intraday)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # Fetch data from Yahoo Finance
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date.strftime('%Y-%m-%d'), 
                                end=end_date.strftime('%Y-%m-%d'),
                                interval=yf_interval)
            
            # If data is empty or we got an error, use simulation
            if hist.empty:
                logging.warning(f"No intraday data found for {symbol}")
                return self._get_simulated_intraday_data(symbol)
            
            # Convert to list of dictionaries with formatted dates
            result = []
            for date, row in hist.iterrows():
                # Get datetime as string
                datetime_str = date.strftime('%Y-%m-%d %H:%M:%S')
                
                price_data = {
                    'datetime': datetime_str,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                result.append(price_data)
            
            # Sort by datetime (most recent first)
            result.sort(key=lambda x: x['datetime'], reverse=True)
            
            # Limit to 24 most recent data points (match previous behavior)
            return result[:24]
            
        except Exception as e:
            logging.error(f"Error fetching intraday data for {symbol}: {e}")
            return self._get_simulated_intraday_data(symbol)
    
    def calculate_correlation(self, symbol, sentiment_data, days=30):
        """
        Calculate correlation between stock price movement and sentiment
        
        Args:
            symbol (str): Stock ticker symbol
            sentiment_data (list): List of sentiment data with dates
            days (int): Number of days to analyze
            
        Returns:
            dict: Correlation metrics and data for visualization
        """
        # Get stock price data
        price_data = self.get_daily_prices(symbol, days)
        
        # Prepare data for correlation analysis
        dates = []
        prices = []
        sentiment_values = []
        price_changes = []
        
        # Create lookup dictionary for sentiment data
        sentiment_by_date = {item['date']: item['sentiment_score'] for item in sentiment_data}
        
        # Process price data and align with sentiment data
        for i, day in enumerate(price_data):
            date = day['date']
            
            # Skip if we don't have sentiment data for this date
            if date not in sentiment_by_date:
                continue
                
            # Add date and sentiment data
            dates.append(date)
            sentiment_values.append(sentiment_by_date[date])
            
            # Add price
            close_price = day['close']
            prices.append(close_price)
            
            # Calculate price change (percentage) if we have previous day data
            if i < len(price_data) - 1:
                prev_close = price_data[i+1]['close']
                price_change = ((close_price - prev_close) / prev_close) * 100
            else:
                price_change = 0
                
            price_changes.append(price_change)
        
        # Calculate correlations if we have enough data
        if len(dates) > 1:
            try:
                # Use pandas for correlation calculation
                df = pd.DataFrame({
                    'date': dates,
                    'price': prices,
                    'sentiment': sentiment_values,
                    'price_change': price_changes
                })
                
                # Calculate correlation coefficients
                price_sentiment_corr = df['sentiment'].corr(df['price'])
                change_sentiment_corr = df['sentiment'].corr(df['price_change'])
                
                # Calculate potential predictive relationship
                # Shift sentiment to see if it predicts next day's price change
                df['next_day_change'] = df['price_change'].shift(-1)
                predictive_corr = df['sentiment'].corr(df['next_day_change'])
                
                correlation_data = {
                    'price_sentiment_correlation': price_sentiment_corr,
                    'change_sentiment_correlation': change_sentiment_corr,
                    'predictive_correlation': predictive_corr,
                    'dates': dates,
                    'prices': prices,
                    'sentiment_values': sentiment_values,
                    'price_changes': price_changes
                }
                
                return correlation_data
                
            except Exception as e:
                logging.error(f"Error calculating correlation: {e}")
                return self._get_default_correlation()
        else:
            logging.warning(f"Not enough data points to calculate correlation for {symbol}")
            return self._get_default_correlation()
    
    def get_stock_overview(self, symbol):
        """
        Get company overview for a given stock symbol using Yahoo Finance
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Company overview data
        """
        try:
            # Get stock info from Yahoo Finance
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Check if we got valid data
            if not info or 'symbol' not in info:
                logging.warning(f"No company overview data found for {symbol}")
                return self._get_simulated_company_overview(symbol)
            
            # Extract the most relevant fields
            overview = {
                'symbol': info.get('symbol', symbol),
                'name': info.get('shortName', info.get('longName', 'Unknown')),
                'description': info.get('longBusinessSummary', ''),
                'exchange': info.get('exchange', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'pe_ratio': info.get('trailingPE', info.get('forwardPE')),
                'market_cap': info.get('marketCap'),
                'dividend_yield': info.get('dividendYield'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'eps': info.get('trailingEps')
            }
            
            return overview
            
        except Exception as e:
            logging.error(f"Error fetching company overview for {symbol}: {e}")
            return self._get_simulated_company_overview(symbol)
    
    def _get_simulated_price_data(self, symbol, days=30):
        """Generate simulated price data when API is not available"""
        logging.warning(f"Using simulated price data for {symbol}")
        
        base_price = self._get_base_price_for_symbol(symbol)
        volatility = self._get_volatility_for_symbol(symbol)
        
        result = []
        base_date = datetime.now()
        
        # Generate price data for each day
        for day in range(days):
            date = base_date - timedelta(days=day)
            date_str = date.strftime('%Y-%m-%d')
            
            # Generate realistic price movement
            daily_change = (0.5 - random.random()) * volatility
            day_base = base_price * (1 + daily_change)
            
            # Generate OHLC values
            open_price = round(day_base * (1 + (random.random() - 0.5) * 0.01), 2)
            close_price = round(day_base * (1 + (random.random() - 0.5) * 0.01), 2)
            high_price = round(max(open_price, close_price) * (1 + random.random() * 0.01), 2)
            low_price = round(min(open_price, close_price) * (1 - random.random() * 0.01), 2)
            volume = int(random.randint(100000, 10000000))
            
            price_data = {
                'date': date_str,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            }
            
            result.append(price_data)
            
        return result
    
    def _get_simulated_intraday_data(self, symbol, intervals=24):
        """Generate simulated intraday data when API is not available"""
        logging.warning(f"Using simulated intraday data for {symbol}")
        
        base_price = self._get_base_price_for_symbol(symbol)
        volatility = self._get_volatility_for_symbol(symbol) * 0.3  # Lower volatility for intraday
        
        result = []
        base_date = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        # Generate hourly data for the trading day
        for hour in range(intervals):
            datetime_obj = base_date - timedelta(hours=hour)
            datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
            
            # Generate realistic price movement
            hourly_change = (0.5 - random.random()) * volatility
            hour_base = base_price * (1 + hourly_change)
            
            # Generate OHLC values
            open_price = round(hour_base * (1 + (random.random() - 0.5) * 0.005), 2)
            close_price = round(hour_base * (1 + (random.random() - 0.5) * 0.005), 2)
            high_price = round(max(open_price, close_price) * (1 + random.random() * 0.003), 2)
            low_price = round(min(open_price, close_price) * (1 - random.random() * 0.003), 2)
            volume = int(random.randint(10000, 1000000))
            
            price_data = {
                'datetime': datetime_str,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            }
            
            result.append(price_data)
            
        return result
    
    def _get_base_price_for_symbol(self, symbol):
        """Return a realistic base price for the given symbol"""
        # Common stock prices for popular tickers 
        symbol_prices = {
            'AAPL': 175.0,
            'MSFT': 350.0,
            'GOOG': 140.0,
            'AMZN': 125.0, 
            'TSLA': 210.0,
            'META': 425.0,
            'NVDA': 800.0,
            'SPY': 470.0,
            'QQQ': 400.0,
            'GME': 40.0,
            'AMC': 15.0,
            'PLTR': 22.0,
            'INTC': 35.0,
            'AMD': 170.0,
            'BA': 190.0,
            'DIS': 110.0,
            'NFLX': 600.0
        }
        
        return symbol_prices.get(symbol.upper(), 100.0)  # Default to $100 if symbol not found
    
    def _get_volatility_for_symbol(self, symbol):
        """Return a realistic volatility value for the given symbol"""
        # Approximate daily volatility for common tickers
        symbol_volatility = {
            'AAPL': 0.015,
            'MSFT': 0.015,
            'GOOG': 0.018,
            'AMZN': 0.02, 
            'TSLA': 0.04,
            'META': 0.025,
            'NVDA': 0.035,
            'SPY': 0.01,
            'QQQ': 0.015,
            'GME': 0.08,
            'AMC': 0.07,
            'PLTR': 0.04,
            'INTC': 0.02,
            'AMD': 0.03,
            'BA': 0.025,
            'DIS': 0.02,
            'NFLX': 0.025
        }
        
        return symbol_volatility.get(symbol.upper(), 0.02)  # Default to 2% if symbol not found
    
    def _get_default_correlation(self):
        """Return default correlation data when calculation fails"""
        return {
            'price_sentiment_correlation': 0,
            'change_sentiment_correlation': 0,
            'predictive_correlation': 0,
            'dates': [],
            'prices': [],
            'sentiment_values': [],
            'price_changes': []
        }
    
    def _get_simulated_company_overview(self, symbol):
        """Generate simulated company overview when API is not available"""
        logging.warning(f"Using simulated company overview for {symbol}")
        
        # Common company data for known tickers
        company_data = {
            'AAPL': {
                'name': 'Apple Inc.',
                'sector': 'Technology',
                'industry': 'Consumer Electronics'
            },
            'MSFT': {
                'name': 'Microsoft Corporation',
                'sector': 'Technology',
                'industry': 'Software—Infrastructure'
            },
            'GOOG': {
                'name': 'Alphabet Inc.',
                'sector': 'Technology',
                'industry': 'Internet Content & Information'
            },
            'AMZN': {
                'name': 'Amazon.com, Inc.',
                'sector': 'Consumer Cyclical',
                'industry': 'Internet Retail'
            },
            'TSLA': {
                'name': 'Tesla, Inc.',
                'sector': 'Consumer Cyclical',
                'industry': 'Auto Manufacturers'
            },
            'META': {
                'name': 'Meta Platforms, Inc.',
                'sector': 'Technology',
                'industry': 'Internet Content & Information'
            },
            'NVDA': {
                'name': 'NVIDIA Corporation',
                'sector': 'Technology',
                'industry': 'Semiconductors'
            }
        }
        
        ticker = symbol.upper()
        company = company_data.get(ticker, {
            'name': f"{ticker} Corporation",
            'sector': 'Unknown',
            'industry': 'Unknown'
        })
        
        return {
            'symbol': ticker,
            'name': company['name'],
            'description': f"{company['name']} is a leading company in the {company['industry']} industry.",
            'exchange': 'NASDAQ',
            'sector': company['sector'],
            'industry': company['industry'],
            'pe_ratio': round(random.uniform(10, 30), 2),
            'market_cap': random.randint(1000000000, 2000000000000),
            'dividend_yield': round(random.uniform(0, 2.5), 2),
            '52_week_high': self._get_base_price_for_symbol(ticker) * 1.2,
            '52_week_low': self._get_base_price_for_symbol(ticker) * 0.8,
            'eps': round(random.uniform(0.5, 10), 2)
        }

# Need to import random for simulated data
import random