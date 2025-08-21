import logging
from datetime import datetime

from app import app, db
from models import Post
from reddit_fetcher import RedditFetcher
from sentiment_analyzer import SentimentAnalyzer


def fetch_and_store_posts():
    """Fetch latest posts, analyze sentiment and store in the database."""
    reddit = RedditFetcher()
    analyzer = SentimentAnalyzer()

    with app.app_context():
        db.create_all()
        posts = reddit.get_posts("wallstreetbets", "day", "hot", limit=25)
        for data in posts:
            sentiment = analyzer.analyze_text(
                f"{data.get('title', '')} {data.get('selftext', '')}"
            )

            created = data.get("created_utc")
            if isinstance(created, datetime):
                created_dt = created
            else:
                try:
                    created_dt = datetime.fromtimestamp(created)
                except Exception:  # pragma: no cover - fallback
                    created_dt = None

            post = Post(
                id=data.get("id"),
                title=data.get("title"),
                selftext=data.get("selftext"),
                url=data.get("url"),
                subreddit=data.get("subreddit"),
                author=data.get("author"),
                created_utc=created_dt,
                score=data.get("score", 0),
                num_comments=data.get("num_comments", 0),
                sentiment_positive=sentiment.get("pos", 0.0),
                sentiment_negative=sentiment.get("neg", 0.0),
                sentiment_neutral=sentiment.get("neu", 0.0),
                sentiment_compound=sentiment.get("compound", 0.0),
            )
            db.session.merge(post)

        try:
            db.session.commit()
        except Exception as exc:  # pragma: no cover - logging
            db.session.rollback()
            logging.error("Failed to commit posts: %s", exc)


if __name__ == "__main__":
    fetch_and_store_posts()

