import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
try:  # pragma: no cover - support package and script execution
    from .reddit_fetcher import RedditFetcher
    from .stock_data_fetcher import StockDataFetcher
except ImportError:
    from reddit_fetcher import RedditFetcher
    from stock_data_fetcher import StockDataFetcher

app = Flask(__name__)
CORS(app)

# Get DATABASE_URL from environment
database_url = os.environ.get('DATABASE_URL')

# Adjust for deprecated postgres scheme
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Fallback to SQLite if no database is configured. This allows the module to
# be imported in environments where a database URL hasn't been provided (e.g.,
# generating data snapshots).
if not database_url:
    database_url = 'sqlite:///finsentiment.db'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

reddit_fetcher = RedditFetcher()
stock_data_fetcher = StockDataFetcher()

from models import Post  # noqa: E402

@app.route('/api/posts')
def api_posts():
    posts_from_db = (
        Post.query.order_by(Post.created_utc.desc()).limit(25).all()
    )
    posts_json = [
        {
            'title': post.title,
            'selftext': post.selftext,
            'url': post.url,
            'subreddit': post.subreddit,
            'author': post.author,
            'created_utc': post.created_utc.isoformat()
            if post.created_utc else None,
            'score': post.score,
            'num_comments': post.num_comments,
            'sentiment': {
                'positive': post.sentiment_positive,
                'negative': post.sentiment_negative,
                'neutral': post.sentiment_neutral,
                'compound': post.sentiment_compound,
            },
        }
        for post in posts_from_db
    ]
    return jsonify(posts_json)

@app.route('/api/stocks')
def api_stocks():
    popular_stocks = [
        'AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA',
        'META', 'NVDA', 'SPY', 'QQQ', 'AMD'
    ]
    stocks = []
    for symbol in popular_stocks:
        company_info = stock_data_fetcher.get_stock_overview(symbol)
        price_data = stock_data_fetcher.get_daily_prices(symbol, days=1)
        latest_price = price_data[0]['close'] if price_data else None
        sentiment_data = reddit_fetcher.get_historical_sentiment(symbol, days=7)
        sentiments = [d.get('sentiment_avg', 0) for d in sentiment_data]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        stocks.append({
            'symbol': symbol,
            'name': company_info.get('name', f'{symbol} Inc.'),
            'price': latest_price,
            'sector': company_info.get('sector', 'Technology'),
            'sentiment': avg_sentiment
        })
    return jsonify(stocks)

@app.route('/')
def health_check():
    return jsonify(status="ok"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
