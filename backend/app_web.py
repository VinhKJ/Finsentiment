import os
import logging
import time
import random
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize Flask extensions
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database - using SQLite for simplicity
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///finsentiment.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions with app
db.init_app(app)

# Import models and create database tables
with app.app_context():
    from models import Post, Comment, SentimentData
    db.create_all()

# Import components after app is created to avoid circular imports
from reddit_fetcher import RedditFetcher
from sentiment_analyzer import SentimentAnalyzer
from stock_data_fetcher import StockDataFetcher

# Initialize components
reddit_fetcher = RedditFetcher()
sentiment_analyzer = SentimentAnalyzer()
stock_data_fetcher = StockDataFetcher()

# Routes
@app.route('/')
def index():
    # Get filter parameters
    subreddit = request.args.get('subreddit', 'wallstreetbets')
    time_period = request.args.get('time_period', 'day')
    sort_by = request.args.get('sort_by', 'hot')
    
    # Simulate loading delay (for demo purposes only)
    time.sleep(random.uniform(0.5, 1.0))
    
    # Get posts from Reddit
    posts = reddit_fetcher.get_posts(subreddit, time_period, sort_by, limit=25)
    
    # Analyze sentiment for each post
    for post in posts:
        post['sentiment'] = sentiment_analyzer.analyze_text(post['title'] + ' ' + post['selftext'])
    
    # Calculate overall sentiment for the shown posts
    overall_sentiment = {
        'positive': sum(1 for post in posts if post['sentiment']['compound'] > 0.05),
        'neutral': sum(1 for post in posts if -0.05 <= post['sentiment']['compound'] <= 0.05),
        'negative': sum(1 for post in posts if post['sentiment']['compound'] < -0.05)
    }
    
    # Get popular subreddits
    popular_subreddits = [
        'wallstreetbets', 'investing', 'stocks', 'finance', 
        'cryptocurrency', 'personalfinance', 'options', 'stockmarket',
        'fintech', 'econmonitor', 'dividends', 'ValueInvesting',
        'Bogleheads', 'passiveincome', 'EuropeFIRE', 'UKPersonalFinance',
        'CreditCards'
    ]
    
    return render_template('index.html', 
                          posts=posts, 
                          overall_sentiment=overall_sentiment,
                          popular_subreddits=popular_subreddits,
                          current_subreddit=subreddit,
                          current_time_period=time_period,
                          current_sort=sort_by)

@app.route('/post/<post_id>')
def post_detail(post_id):
    # Simulate loading delay (for demo purposes only)
    time.sleep(random.uniform(0.5, 1.2))
    
    # Get post details
    post = reddit_fetcher.get_post(post_id)
    if not post:
        flash('Post not found')
        return redirect(url_for('index'))
    
    # Analyze sentiment
    post['sentiment'] = sentiment_analyzer.analyze_text(post['title'] + ' ' + post['selftext'])
    
    # Get comments
    comments = reddit_fetcher.get_comments(post_id)
    
    # Analyze comment sentiments and track total sentiment score
    total_sentiment_compound = 0
    all_comment_text = ""
    
    for comment in comments:
        comment['sentiment'] = sentiment_analyzer.analyze_text(comment['body'])
        total_sentiment_compound += comment['sentiment']['compound']
        all_comment_text += " " + comment['body']
    
    # Calculate overall sentiment stats
    sentiment_stats = {
        'positive': sum(1 for c in comments if c['sentiment']['compound'] > 0.05),
        'neutral': sum(1 for c in comments if -0.05 <= c['sentiment']['compound'] <= 0.05),
        'negative': sum(1 for c in comments if c['sentiment']['compound'] < -0.05),
        'total': len(comments) if comments else 1  # Avoid division by zero
    }
    
    # Calculate percentages
    sentiment_percentages = {
        'positive': (sentiment_stats['positive'] / sentiment_stats['total']) * 100,
        'neutral': (sentiment_stats['neutral'] / sentiment_stats['total']) * 100,
        'negative': (sentiment_stats['negative'] / sentiment_stats['total']) * 100
    }
    
    # Extract entities (companies/stocks mentioned)
    entities = sentiment_analyzer.extract_entities(post['title'] + ' ' + post['selftext'])
    
    # Generate word cloud from comments if there are enough comments
    wordcloud_path = None
    if len(comments) > 0 and all_comment_text:
        from word_cloud_generator import generate_word_cloud
        wordcloud_path = generate_word_cloud(all_comment_text, post_id)
    
    # Get total sentiment score
    comments_sentiment_score = total_sentiment_compound
    
    # Get top upvoted comments (sort by score)
    top_comments = sorted(comments, key=lambda x: x['score'], reverse=True)[:5] if comments else []
    
    return render_template('post_detail.html', 
                          post=post, 
                          comments=comments,
                          sentiment_stats=sentiment_stats,
                          sentiment_percentages=sentiment_percentages,
                          entities=entities,
                          wordcloud_path=wordcloud_path,
                          comments_sentiment_score=comments_sentiment_score,
                          top_comments=top_comments)

@app.route('/trends')
def trend_analysis():
    # Get parameters
    entity = request.args.get('entity', 'market')
    time_range = request.args.get('time_range', '7days')
    
    # Simulate loading delay (for demo purposes only)
    time.sleep(random.uniform(0.7, 1.5))
    
    # Get time range in days
    days = 7
    if time_range == '1day':
        days = 1
    elif time_range == '7days':
        days = 7
    elif time_range == '30days':
        days = 30
    elif time_range == '90days':
        days = 90
    
    # Get sentiment data over time
    sentiment_data = reddit_fetcher.get_historical_sentiment(entity, days)
    
    # Process data for chart
    dates = [data['date'] for data in sentiment_data]
    positive_vals = [data['positive'] for data in sentiment_data]
    negative_vals = [data['negative'] for data in sentiment_data]
    neutral_vals = [data['neutral'] for data in sentiment_data]
    
    # Get popular entities
    popular_entities = [
        'market', 'SPY', 'AAPL', 'TSLA', 'MSFT', 'AMZN', 
        'GME', 'AMC', 'BTC', 'ETH', 'NVDA', 'GOOG', 'META',
        'PLTR', 'AMD', 'COIN', 'JPM', 'BAC', 'GS', 'MS',
        'BBBY', 'NOK', 'inflation', 'recession', 'QQQ', 'VIX'
    ]
    
    return render_template('trend_analysis.html',
                          entity=entity,
                          time_range=time_range,
                          dates=dates,
                          positive_vals=positive_vals,
                          negative_vals=negative_vals,
                          neutral_vals=neutral_vals,
                          popular_entities=popular_entities)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
    
    # Simulate loading delay (for demo purposes only)
    time.sleep(random.uniform(0.5, 1.3))
    
    # Search posts
    results = reddit_fetcher.search_posts(query, limit=25)
    
    # Analyze sentiment for results
    for post in results:
        post['sentiment'] = sentiment_analyzer.analyze_text(post['title'] + ' ' + post['selftext'])
    
    return render_template('search_results.html', 
                          query=query, 
                          results=results)

@app.route('/stock/<symbol>')
def stock_detail(symbol):
    """
    Page showing stock price data and correlation with sentiment
    """
    # Simulate loading delay (for demo purposes only)
    time.sleep(random.uniform(0.8, 1.8))
    
    # Get time range parameter (default to 30 days)
    time_range = request.args.get('time_range', '30days')
    
    # Convert time range to days for API calls
    days = 30
    if time_range == '7days':
        days = 7
    elif time_range == '30days':
        days = 30
    elif time_range == '90days':
        days = 90
    
    # Get stock data
    stock_prices = stock_data_fetcher.get_daily_prices(symbol, days)
    
    # Get company overview
    company_info = stock_data_fetcher.get_stock_overview(symbol)
    
    # Get sentiment data for the same time period
    sentiment_data = reddit_fetcher.get_historical_sentiment(symbol, days)
    
    # Format sentiment data for correlation calculation
    formatted_sentiment = []
    for data in sentiment_data:
        formatted_sentiment.append({
            'date': data['date'],
            'sentiment_score': data['sentiment_avg'] if 'sentiment_avg' in data else 0
        })
    
    # Calculate correlation between stock price and sentiment
    correlation = stock_data_fetcher.calculate_correlation(symbol, formatted_sentiment, days)
    
    # Get data for charts
    chart_dates = [price['date'] for price in stock_prices]
    chart_prices = [price['close'] for price in stock_prices]
    chart_sentiment = []
    
    # Create a dictionary to map dates to sentiment values
    sentiment_by_date = {item['date']: item.get('sentiment_avg', 0) for item in sentiment_data}
    
    # Add sentiment values aligned with price dates
    for date in chart_dates:
        chart_sentiment.append(sentiment_by_date.get(date, 0))
    
    # Get recent related posts mentioning this stock
    related_posts = reddit_fetcher.search_posts(symbol, limit=5)
    
    # Analyze sentiment for related posts
    for post in related_posts:
        post['sentiment'] = sentiment_analyzer.analyze_text(post['title'] + ' ' + post['selftext'])
    
    return render_template('stock_detail.html',
                          symbol=symbol,
                          time_range=time_range,
                          stock_prices=stock_prices,
                          company_info=company_info,
                          correlation=correlation,
                          chart_dates=chart_dates,
                          chart_prices=chart_prices,
                          chart_sentiment=chart_sentiment,
                          related_posts=related_posts)

@app.route('/stocks')
def stock_list():
    """
    Page listing popular stocks with sentiment and price information
    """
    # Simulate loading delay (for demo purposes only)
    time.sleep(random.uniform(1.0, 2.0))
    
    # Get popular stock symbols
    popular_stocks = [
        'AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA', 
        'META', 'NVDA', 'SPY', 'QQQ', 'AMD', 
        'GME', 'AMC', 'PLTR', 'INTC', 'COIN', 
        'JPM', 'BAC', 'GS', 'MS', 'BBBY', 'NOK',
        'VTI', 'VOO', 'JEPI', 'SCHD', 'VYM', 'VIG'
    ]
    
    stocks = []
    
    # Get basic data for each stock
    for symbol in popular_stocks:
        # Get company overview
        company_info = stock_data_fetcher.get_stock_overview(symbol)
        
        # Get latest price
        price_data = stock_data_fetcher.get_daily_prices(symbol, days=1)
        latest_price = price_data[0]['close'] if price_data else None
        
        # Get sentiment data
        sentiment_data = reddit_fetcher.get_historical_sentiment(symbol, days=7)
        avg_sentiment = 0
        if sentiment_data:
            # Calculate average sentiment over the past week
            sentiments = [data.get('sentiment_avg', 0) for data in sentiment_data]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Mention count in the past week
        mention_count = sum(data.get('post_count', 0) + data.get('comment_count', 0) 
                            for data in sentiment_data)
        
        # Add to stocks list
        stocks.append({
            'symbol': symbol,
            'name': company_info.get('name', f'{symbol} Inc.'),
            'price': latest_price,
            'sector': company_info.get('sector', 'Technology'),
            'sentiment': avg_sentiment,
            'mentions': mention_count
        })
    
    return render_template('stock_list.html', stocks=stocks)

@app.route('/about')
def about():
    return render_template('about.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {e}")
    return render_template('500.html'), 500
