from flask import Flask, request, jsonify
from flask_cors import CORS
from reddit_fetcher import RedditFetcher
from sentiment_analyzer import SentimentAnalyzer
from stock_data_fetcher import StockDataFetcher

app = Flask(__name__)
CORS(app)

reddit_fetcher = RedditFetcher()
sentiment_analyzer = SentimentAnalyzer()
stock_data_fetcher = StockDataFetcher()

@app.route('/api/posts')
def api_posts():
    subreddit = request.args.get('subreddit', 'wallstreetbets')
    time_period = request.args.get('time_period', 'day')
    sort_by = request.args.get('sort_by', 'hot')
    posts = reddit_fetcher.get_posts(subreddit, time_period, sort_by, limit=25)
    for post in posts:
        post['sentiment'] = sentiment_analyzer.analyze_text(post['title'] + ' ' + post['selftext'])
    return jsonify(posts)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
