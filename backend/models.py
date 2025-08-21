from database import db
from datetime import datetime

# Expose the base model for use outside of the Flask context
Base = db.Model


class Post(Base):
    id = db.Column(db.String(10), primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    selftext = db.Column(db.Text)
    url = db.Column(db.String(500))
    subreddit = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50))
    created_utc = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer, default=0)
    num_comments = db.Column(db.Integer, default=0)
    
    # Sentiment data
    sentiment_positive = db.Column(db.Float, default=0.0)
    sentiment_negative = db.Column(db.Float, default=0.0)
    sentiment_neutral = db.Column(db.Float, default=0.0)
    sentiment_compound = db.Column(db.Float, default=0.0)
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy=True)
    
    def __repr__(self):
        return f'<Post {self.id}: {self.title}>'


class Comment(Base):
    id = db.Column(db.String(10), primary_key=True)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50))
    created_utc = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer, default=0)
    
    # Parent post
    post_id = db.Column(db.String(10), db.ForeignKey('post.id'), nullable=False)
    
    # Sentiment data
    sentiment_positive = db.Column(db.Float, default=0.0)
    sentiment_negative = db.Column(db.Float, default=0.0)
    sentiment_neutral = db.Column(db.Float, default=0.0)
    sentiment_compound = db.Column(db.Float, default=0.0)
    
    # Parent comment (for nested comments)
    parent_id = db.Column(db.String(10), db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def __repr__(self):
        return f'<Comment {self.id}>'


class SentimentData(Base):
    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(100), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    
    # Sentiment counts
    positive_count = db.Column(db.Integer, default=0)
    negative_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    
    # Aggregated sentiment values
    sentiment_avg = db.Column(db.Float, default=0.0)
    sentiment_stddev = db.Column(db.Float, default=0.0)
    
    # Metadata
    post_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    
    __table_args__ = (
        db.UniqueConstraint('entity', 'date', name='unique_entity_date'),
    )
    
    def __repr__(self):
        return f'<SentimentData {self.entity} on {self.date}>'


class Stock(Base):
    symbol = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    sector = db.Column(db.String(100))
    sentiment = db.Column(db.Float)

    def __repr__(self):
        return f'<Stock {self.symbol}>'
