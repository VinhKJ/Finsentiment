import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# --- PHẦN CẤU HÌNH DATABASE (GIỮ NGUYÊN) ---
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- IMPORT MODELS SAU KHI KHỞI TẠO db ---
from models import Post, Stock  # noqa: E402

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
    stocks_from_db = Stock.query.all()
    stocks_json = [
        {
            'symbol': stock.symbol,
            'name': stock.name,
            'price': stock.price,
            'sector': stock.sector,
            'sentiment': stock.sentiment,
        }
        for stock in stocks_from_db
    ]
    return jsonify(stocks_json)

@app.route('/')
def health_check():
    return jsonify(status="ok"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
