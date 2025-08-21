import os
import logging
from datetime import datetime

import pandas as pd  # noqa: F401
import nltk  # noqa: F401
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import các Models và Fetchers
from models import Base, Post, Stock
from reddit_fetcher import RedditFetcher
from sentiment_analyzer import SentimentAnalyzer
from stock_data_fetcher import StockDataFetcher

logging.basicConfig(level=logging.INFO)

# --- PHẦN KẾT NỐI DATABASE (giống như tôi đã hướng dẫn) ---
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if not database_url:
    logging.error("Error: DATABASE_URL environment variable not set.")
    exit()

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- HÀM XỬ LÝ POSTS ---
def fetch_and_store_posts(db_session):
    logging.info("Starting to fetch and store posts...")
    reddit = RedditFetcher()
    analyzer = SentimentAnalyzer()
    posts_data = reddit.get_posts("wallstreetbets", "day", "hot", limit=50)

    for data in posts_data:
        sentiment = analyzer.analyze_text(f"{data.get('title', '')} {data.get('selftext', '')}")
        created_dt = data.get("created_utc")

        post = Post(
            id=data.get("id"), title=data.get("title"), selftext=data.get("selftext"),
            url=data.get("url"), subreddit=data.get("subreddit"), author=data.get("author"),
            created_utc=created_dt, score=data.get("score", 0), num_comments=data.get("num_comments", 0),
            sentiment_positive=sentiment.get("pos", 0.0), sentiment_negative=sentiment.get("neg", 0.0),
            sentiment_neutral=sentiment.get("neu", 0.0), sentiment_compound=sentiment.get("compound", 0.0),
        )
        db_session.merge(post)
    logging.info(f"Merged {len(posts_data)} posts.")

# --- HÀM XỬ LÝ STOCKS (MỚI) ---
def fetch_and_store_stocks(db_session):
    logging.info("Starting to fetch and store stocks...")
    stock_fetcher = StockDataFetcher()
    reddit_fetcher = RedditFetcher()
    popular_stocks = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA', 'SPY', 'QQQ', 'AMD']

    for symbol in popular_stocks:
        company_info = stock_fetcher.get_stock_overview(symbol)
        price_data = stock_fetcher.get_daily_prices(symbol, days=1)
        latest_price = price_data[0]["close"] if price_data else None
        sentiment_data = reddit_fetcher.get_historical_sentiment(symbol, days=7)
        sentiments = [d.get("sentiment_avg", 0) for d in sentiment_data]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        stock = Stock(
            symbol=symbol, name=company_info.get("name", f"{symbol} Inc."),
            price=latest_price, sector=company_info.get("sector", "Technology"),
            sentiment=avg_sentiment
        )
        db_session.merge(stock)
    logging.info(f"Merged {len(popular_stocks)} stocks.")

# --- HÀM CHẠY CHÍNH ---
def run_job():
    # Tạo bảng nếu chưa có
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    try:
        fetch_and_store_posts(db_session)
        fetch_and_store_stocks(db_session)
        db_session.commit()
        logging.info("Job finished successfully. Data committed.")
    except Exception as exc:
        logging.error("Job failed: %s", exc)
        db_session.rollback()
    finally:
        db_session.close()

if __name__ == "__main__":
    run_job()

