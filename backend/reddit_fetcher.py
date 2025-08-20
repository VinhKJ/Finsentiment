import os
import praw
import logging
import datetime
import random
import re
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from sentiment_analyzer import SentimentAnalyzer

class RedditFetcher:
    def __init__(self):
        """Initialize the Reddit API connection"""
        try:
            # Try to initialize with real Reddit API credentials
            self.reddit = praw.Reddit(
                client_id='_SyfM0uJczgcOJzgLQAB2Q',
                client_secret="2Y2oi4l3K7YKEL379Fgx5iaz_2PO6A",
                user_agent="u/GeneWinter8043"
            )
            self.use_real_api = True
            logging.info("Using real Reddit API")
        except Exception as e:
            # Fall back to simulated data if API credentials are not available
            logging.warning(f"Reddit API initialization failed: {e}. Using simulated data.")
            self.use_real_api = False
            
        # Initialize sentiment analyzer for fallback mode
        self.sentiment_analyzer = SentimentAnalyzer()
            
        # Financial subreddits
        self.financial_subreddits = [
            'wallstreetbets', 'investing', 'stocks', 'finance', 
            'cryptocurrency', 'personalfinance', 'options', 'stockmarket'
        ]
    
    def get_posts(self, subreddit='wallstreetbets', time_filter='day', sort_by='hot', limit=25):
        """
        Get posts from a subreddit
        
        Args:
            subreddit (str): Subreddit name
            time_filter (str): Time filter ('hour', 'day', 'week', 'month', 'year', 'all')
            sort_by (str): Sort method ('hot', 'new', 'top', 'controversial')
            limit (int): Number of posts to return
            
        Returns:
            list: List of posts
        """
        if self.use_real_api:
            try:
                return self._get_real_posts(subreddit, time_filter, sort_by, limit)
            except Exception as e:
                logging.error(f"Error fetching real posts: {e}")
                return self._get_simulated_posts(subreddit, limit)
        else:
            return self._get_simulated_posts(subreddit, limit)
    
    def _get_real_posts(self, subreddit, time_filter, sort_by, limit):
        """Get actual posts from Reddit API"""
        subreddit_obj = self.reddit.subreddit(subreddit)
        
        if sort_by == 'hot':
            posts = subreddit_obj.hot(limit=limit)
        elif sort_by == 'new':
            posts = subreddit_obj.new(limit=limit)
        elif sort_by == 'top':
            posts = subreddit_obj.top(time_filter=time_filter, limit=limit)
        elif sort_by == 'controversial':
            posts = subreddit_obj.controversial(time_filter=time_filter, limit=limit)
        else:
            posts = subreddit_obj.hot(limit=limit)
            
        result = []
        for post in posts:
            # Skip stickied posts
            if post.stickied:
                continue
                
            result.append({
                'id': post.id,
                'title': post.title,
                'selftext': post.selftext,
                'url': post.url,
                'subreddit': post.subreddit.display_name,
                'author': post.author.name if post.author else '[deleted]',
                'created_utc': datetime.datetime.fromtimestamp(post.created_utc),
                'score': post.score,
                'upvote_ratio': post.upvote_ratio,
                'num_comments': post.num_comments,
                'permalink': post.permalink
            })
            
        return result
    
    def _get_simulated_posts(self, subreddit, limit):
        """Generate simulated posts when API is not available"""
        posts = []
        
        # Stock tickers and terminology for realistic post titles
        tickers = ['SPY', 'AAPL', 'TSLA', 'GME', 'AMC', 'NVDA', 'MSFT', 'AMZN', 'PLTR', 'BB', 'NOK', 
                   'META', 'AMD', 'COIN', 'JPM', 'BAC', 'GS', 'MS', 'BBBY', 'QQQ', 'VTI', 'VOO', 'JEPI', 
                   'SCHD', 'VYM', 'VIG', 'INTC', 'GOOG']
        terms = ['bullish', 'bearish', 'calls', 'puts', 'tendies', 'squeeze', 'moon', 'crash', 'dump', 'rally']
        
        # Generate simulated posts
        base_date = datetime.datetime.now()
        
        for i in range(limit):
            # Select random ticker and term
            ticker = random.choice(tickers)
            term1 = random.choice(terms)
            term2 = random.choice(terms)
            
            # Generate title
            title_templates = [
                f"What's happening with {ticker}? Looking {term1}",
                f"{ticker} is about to {term1} - DD inside",
                f"Why I'm {term1} on {ticker} for the next quarter",
                f"Just YOLOed my life savings into {ticker} {term1}",
                f"The {ticker} {term1} {term2} might be starting",
                f"Technical Analysis of {ticker}: {term1} indicators",
                f"Breaking: {ticker} {term1} due to market conditions",
                f"Thoughts on {ticker} going {term1}?",
                f"{ticker} Earnings Thread - Will it {term1}?",
                f"I've been researching {ticker} and found it's {term1} - here's why"
            ]
            title = random.choice(title_templates)
            
            # Generate text content
            text_templates = [
                f"I've been watching {ticker} for months and think it's heading {term1}. The technicals look {term2}.",
                f"Based on my research, {ticker} is positioned to go {term1} in the next few weeks due to market trends.",
                f"After analyzing {ticker}'s financials, I believe it's {term1}. Their revenue growth is impressive.",
                f"The market doesn't understand {ticker}'s potential. It's clearly {term1} and undervalued.",
                f"I'm seeing a {term1} pattern for {ticker}. Who else is in on this?",
                ""  # Empty for link-only posts
            ]
            selftext = random.choice(text_templates)
            
            # Generate random date within the last week
            days_ago = random.randint(0, 6)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            post_date = base_date - datetime.timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # Generate random score and comments
            score = random.randint(5, 5000)
            upvote_ratio = random.uniform(0.5, 1.0)
            num_comments = random.randint(0, 500)
            
            # Create post object
            post = {
                'id': f'sim{i}',
                'title': title,
                'selftext': selftext,
                'url': f'https://reddit.com/r/{subreddit}/comments/sim{i}/',
                'subreddit': subreddit,
                'author': f'user{random.randint(100, 9999)}',
                'created_utc': post_date,
                'score': score,
                'upvote_ratio': upvote_ratio,
                'num_comments': num_comments,
                'permalink': f'/r/{subreddit}/comments/sim{i}/'
            }
            
            posts.append(post)
            
        return posts
    
    def get_post(self, post_id):
        """
        Get a specific post by ID
        
        Args:
            post_id (str): Reddit post ID
            
        Returns:
            dict: Post data
        """
        if self.use_real_api:
            try:
                submission = self.reddit.submission(id=post_id)
                
                post = {
                    'id': submission.id,
                    'title': submission.title,
                    'selftext': submission.selftext,
                    'url': submission.url,
                    'subreddit': submission.subreddit.display_name,
                    'author': submission.author.name if submission.author else '[deleted]',
                    'created_utc': datetime.datetime.fromtimestamp(submission.created_utc),
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'permalink': submission.permalink
                }
                
                return post
            except Exception as e:
                logging.error(f"Error fetching post {post_id}: {e}")
                return self._get_simulated_post(post_id)
        else:
            return self._get_simulated_post(post_id)
    
    def _get_simulated_post(self, post_id):
        """Generate a simulated post for a specific ID"""
        # Stock tickers and terminology for realistic post content
        tickers = ['SPY', 'AAPL', 'TSLA', 'GME', 'AMC', 'NVDA', 'MSFT', 'AMZN', 'PLTR', 'META', 'AMD', 
                  'COIN', 'JPM', 'BAC', 'GS', 'MS', 'BBBY', 'NOK', 'QQQ', 'VTI', 'VOO', 'GOOG']
        ticker = random.choice(tickers)
        
        title_templates = [
            f"Deep Dive Analysis: Why {ticker} is set for a major move",
            f"{ticker} Technical Analysis and Price Targets",
            f"Breaking down {ticker}'s financials - Bullish case",
            f"The Bull and Bear case for {ticker} in the current market",
            f"Why I'm investing 50% of my portfolio in {ticker} - DD Inside"
        ]
        
        selftext_templates = [
            f"""
# {ticker} Analysis and Investment Thesis

## Introduction
I've been researching {ticker} for the past few months and wanted to share my findings. The company is positioned for growth in the current market environment.

## Financials
- Revenue: Growing at 22% YoY
- Earnings: Beat expectations last 3 quarters
- Cash position: Strong with $4.5B
- Debt: Manageable at $1.2B

## Technical Analysis
The stock is forming a classic cup and handle pattern which is typically bullish. MACD shows a crossover indicating potential upward movement.

## Catalysts
1. New product launch in Q3
2. Expansion into emerging markets
3. Potential acquisition targets
4. Industry tailwinds

## Risks
- Competition from larger players
- Regulatory concerns
- Market volatility

## Conclusion
I'm bullish on {ticker} with a price target of $XXX by year end. This represents a 30% upside from current levels.

*Disclaimer: This is not financial advice. Do your own research.*
            """,
            f"""
# {ticker} Technical Analysis

Looking at the charts, {ticker} is showing several bullish indicators:

1. **Moving Averages**: The 50-day MA just crossed above the 200-day MA (golden cross)
2. **RSI**: Currently at 58, showing momentum but not overbought
3. **Volume**: Increasing on up days, decreasing on down days
4. **Support Levels**: Strong support at $XXX levels

The stock has been consolidating for weeks and appears ready for a breakout.

Charts and further analysis: [link]

What do you think? I'm considering loading up on calls.
            """,
            f"""
# Why {ticker} is undervalued right now

After the recent market pullback, {ticker} is trading at a significant discount to its intrinsic value. Here's why:

## Industry Analysis
The sector is growing at 15% annually while {ticker} is growing at 23%

## Competitive Advantages
- Proprietary technology
- Strong brand recognition
- Economies of scale
- High switching costs for customers

## Valuation Metrics
- P/E ratio below industry average (18 vs 24)
- PEG ratio of 0.8 indicates undervaluation
- Price to FCF of 15 is attractive

I've built a DCF model that suggests a fair value 40% higher than current price.

Position: Long shares and Jan 20XX calls
            """
        ]
        
        base_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 5))
        
        post = {
            'id': post_id,
            'title': random.choice(title_templates),
            'selftext': random.choice(selftext_templates),
            'url': f'https://reddit.com/r/wallstreetbets/comments/{post_id}/',
            'subreddit': 'wallstreetbets',
            'author': f'user{random.randint(100, 9999)}',
            'created_utc': base_date,
            'score': random.randint(100, 5000),
            'upvote_ratio': random.uniform(0.7, 0.98),
            'num_comments': random.randint(50, 500),
            'permalink': f'/r/wallstreetbets/comments/{post_id}/'
        }
        
        return post
    
    def get_comments(self, post_id, limit=50):
        """
        Get comments for a specific post
        
        Args:
            post_id (str): Reddit post ID
            limit (int): Maximum number of comments to return
            
        Returns:
            list: List of comments
        """
        if self.use_real_api:
            try:
                submission = self.reddit.submission(id=post_id)
                submission.comments.replace_more(limit=0)  # Only fetch top-level comments
                
                comments = []
                for comment in submission.comments[:limit]:
                    comments.append({
                        'id': comment.id,
                        'body': comment.body,
                        'author': comment.author.name if comment.author else '[deleted]',
                        'created_utc': datetime.datetime.fromtimestamp(comment.created_utc),
                        'score': comment.score,
                        'permalink': comment.permalink,
                        'depth': 0,
                        'parent_id': None
                    })
                
                return comments
            except Exception as e:
                logging.error(f"Error fetching comments for post {post_id}: {e}")
                return self._get_simulated_comments(post_id, limit)
        else:
            return self._get_simulated_comments(post_id, limit)
    
    def _get_simulated_comments(self, post_id, limit):
        """Generate simulated comments when API is not available"""
        comments = []
        
        # Get the simulated post to get context
        post = self._get_simulated_post(post_id)
        title = post['title']
        
        # Extract ticker from title if present
        ticker_match = re.search(r'\b([A-Z]{2,5})\b', title)
        ticker = ticker_match.group(1) if ticker_match else 'SPY'
        
        # Comment templates for realistic content
        bullish_comments = [
            f"Great analysis on {ticker}. I've been holding since $XX and plan to add more.",
            f"Thanks for the DD! {ticker} has been on my watchlist, might jump in tomorrow.",
            f"I'm bullish on {ticker} too, the technicals look solid right now.",
            f"Loaded up on {ticker} calls yesterday, hoping this pays off!",
            f"{ticker} to the moon! 🚀🚀🚀",
            f"Solid fundamentals for {ticker}, and the market doesn't seem to realize it yet.",
            f"I work in the industry and {ticker} is definitely positioned well for growth.",
            f"Been holding {ticker} for months. The patience is finally paying off.",
            f"Just bought more {ticker} on this dip. Thanks for confirming my bias!",
            f"The institutional ownership of {ticker} has been increasing. Smart money knows what's up."
        ]
        
        bearish_comments = [
            f"I don't know about {ticker}, the valuation seems stretched to me.",
            f"Have you looked at {ticker}'s debt levels? I'm staying away for now.",
            f"I'm actually bearish on {ticker}. The competition is heating up in this space.",
            f"Bought puts on {ticker} yesterday. The technical breakdown is clear.",
            f"{ticker} is overvalued by every metric. This won't end well.",
            f"The whole sector {ticker} is in looks weak. I'd be careful here.",
            f"I'm short {ticker} and sleeping well at night. The earnings will disappoint.",
            f"Not convinced on {ticker}. What about the regulatory risks?",
            f"The chart for {ticker} shows a clear head and shoulders pattern. Bearish.",
            f"I see {ticker} dropping at least 15% from here. The growth story is over."
        ]
        
        neutral_comments = [
            f"Interesting take on {ticker}. What's your price target?",
            f"What do you think about {ticker}'s upcoming earnings? That could be a catalyst.",
            f"How does {ticker} compare to its competitors in the space?",
            f"I'm on the fence about {ticker}. Need to do more research.",
            f"What's the best entry point for {ticker} in your opinion?",
            f"Has anyone looked at the option chain for {ticker}? IV seems high.",
            f"Not sure if now is the time for {ticker}, but I'm watching closely.",
            f"What's your time horizon for {ticker}? Short-term or long-term play?",
            f"Any concerns about the overall market affecting {ticker}?",
            f"I've been following {ticker} for a while. It tends to be volatile around news."
        ]
        
        # Generate random comments
        base_date = post['created_utc']
        comment_date = base_date + datetime.timedelta(minutes=random.randint(5, 120))
        
        for i in range(limit):
            # Choose comment type with tendency toward bullish
            comment_type = random.choices(
                ['bullish', 'bearish', 'neutral'], 
                weights=[0.5, 0.25, 0.25], 
                k=1
            )[0]
            
            if comment_type == 'bullish':
                body = random.choice(bullish_comments)
            elif comment_type == 'bearish':
                body = random.choice(bearish_comments)
            else:
                body = random.choice(neutral_comments)
                
            # Increment time for each comment
            comment_date += datetime.timedelta(minutes=random.randint(1, 30))
            
            # Create comment object
            comment = {
                'id': f'c{i}{post_id}',
                'body': body,
                'author': f'user{random.randint(100, 9999)}',
                'created_utc': comment_date,
                'score': random.randint(-5, 200),
                'permalink': f'/r/wallstreetbets/comments/{post_id}/comment/c{i}{post_id}',
                'depth': 0,
                'parent_id': None
            }
            
            comments.append(comment)
            
        # Sort by score (descending)
        comments.sort(key=lambda x: x['score'], reverse=True)
        
        return comments
    
    def search_posts(self, query, subreddit=None, limit=25):
        """
        Search for posts containing the query
        
        Args:
            query (str): Search query
            subreddit (str): Limit search to specific subreddit (optional)
            limit (int): Maximum number of results
            
        Returns:
            list: List of matching posts
        """
        if self.use_real_api:
            try:
                # Construct search query
                search_query = query
                if subreddit:
                    search_query = f'subreddit:{subreddit} {query}'
                
                # Perform search
                results = []
                for submission in self.reddit.subreddit('all').search(search_query, limit=limit):
                    # Skip if not from a financial subreddit (unless specific subreddit requested)
                    if not subreddit and submission.subreddit.display_name.lower() not in self.financial_subreddits:
                        continue
                        
                    results.append({
                        'id': submission.id,
                        'title': submission.title,
                        'selftext': submission.selftext,
                        'url': submission.url,
                        'subreddit': submission.subreddit.display_name,
                        'author': submission.author.name if submission.author else '[deleted]',
                        'created_utc': datetime.datetime.fromtimestamp(submission.created_utc),
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'permalink': submission.permalink
                    })
                
                return results
            except Exception as e:
                logging.error(f"Error searching posts: {e}")
                return self._get_simulated_search_results(query, limit)
        else:
            return self._get_simulated_search_results(query, limit)
    
    def _get_simulated_search_results(self, query, limit):
        """Generate simulated search results when API is not available"""
        results = []
        
        # Convert query to uppercase to match stock tickers
        query_upper = query.upper()
        
        # Check if query looks like a stock ticker
        is_ticker = len(query) <= 5 and query.isalpha() and query.isupper()
        
        # Generate different types of posts based on the query
        title_templates = []
        
        if is_ticker:
            ticker = query_upper
            title_templates = [
                f"{ticker} DD: Why it's poised for growth",
                f"Technical Analysis of {ticker} - Bullish patterns forming",
                f"Just YOLO'd into {ticker} - Here's why",
                f"Breaking: {ticker} announces earnings beat",
                f"Is {ticker} undervalued? Deep dive analysis",
                f"The Bull Case for {ticker} in this market",
                f"{ticker} - A value investor's perspective",
                f"Why I'm shorting {ticker} - Bear case",
                f"Thoughts on {ticker} after today's price action?",
                f"{ticker} Earnings Thread - Q2 2023"
            ]
        else:
            # For general search terms
            title_templates = [
                f"Analysis of {query} impact on markets",
                f"How does {query} affect your investment strategy?",
                f"Discussion: {query} and its implications for investors",
                f"{query} trends and market opportunities",
                f"Is {query} priced into the market already?",
                f"The relationship between {query} and stock performance",
                f"How I'm positioning my portfolio for {query}",
                f"{query} explained - What investors should know",
                f"Breaking down the {query} situation for traders",
                f"Weekly {query} discussion thread"
            ]
            
        # Generate results
        base_date = datetime.datetime.now()
        
        for i in range(limit):
            # Choose random subreddit
            subreddit = random.choice(self.financial_subreddits)
            
            # Choose random title
            title = random.choice(title_templates)
            
            # Generate selftext based on title
            selftext = f"This is a detailed analysis of {query} and its impact on the financial markets. " \
                      f"Based on current trends, I believe we'll see significant movement related to {query}."
                      
            # Random date within last month
            days_ago = random.randint(0, 30)
            post_date = base_date - datetime.timedelta(days=days_ago)
            
            # Create post object
            post = {
                'id': f'search{i}',
                'title': title,
                'selftext': selftext,
                'url': f'https://reddit.com/r/{subreddit}/comments/search{i}/',
                'subreddit': subreddit,
                'author': f'user{random.randint(100, 9999)}',
                'created_utc': post_date,
                'score': random.randint(5, 3000),
                'upvote_ratio': random.uniform(0.6, 0.98),
                'num_comments': random.randint(0, 300),
                'permalink': f'/r/{subreddit}/comments/search{i}/'
            }
            
            results.append(post)
            
        return results
    
    def get_historical_sentiment(self, entity, days):
        """
        Get historical sentiment data for an entity over time
        
        Args:
            entity (str): Entity to get sentiment for (ticker, 'market', etc.)
            days (int): Number of days of historical data
            
        Returns:
            list: List of daily sentiment data
        """
        if self.use_real_api:
            try:
                # For real implementation, we would query a database of historical sentiment
                # Falling back to simulated data for now
                return self._get_simulated_historical_sentiment(entity, days)
            except Exception as e:
                logging.error(f"Error fetching historical sentiment: {e}")
                return self._get_simulated_historical_sentiment(entity, days)
        else:
            return self._get_simulated_historical_sentiment(entity, days)
    
    def _get_simulated_historical_sentiment(self, entity, days):
        """Generate simulated historical sentiment data"""
        result = []
        
        # Start date
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=days)
        
        # Generate trend based on entity
        # For certain tickers, we'll create specific patterns
        if entity in ['TSLA', 'GME', 'AMC', 'AAPL', 'MSFT']:
            # More volatile stocks with higher amplitude
            amplitude = 0.4
            frequency = 0.5
            upward_trend = 0.002
        elif entity == 'market':
            # Market overall is less volatile
            amplitude = 0.2
            frequency = 0.3
            upward_trend = 0.001
        else:
            # Default pattern
            amplitude = 0.3
            frequency = 0.4
            upward_trend = 0.0015
            
        # Generate daily data
        current_date = start_date
        day_count = 0
        
        while current_date <= end_date:
            # Base sentiment with slight noise
            base_positive = 0.4 + amplitude * np.sin(frequency * day_count) + day_count * upward_trend
            base_negative = 0.3 - amplitude/2 * np.sin(frequency * day_count) - day_count * upward_trend
            
            # Add random noise
            noise = np.random.normal(0, 0.05)
            base_positive = max(0.1, min(0.8, base_positive + noise))
            
            noise = np.random.normal(0, 0.05)
            base_negative = max(0.05, min(0.7, base_negative + noise))
            
            # Calculate neutral
            base_neutral = 1.0 - base_positive - base_negative
            
            # Adjust if out of bounds
            if base_neutral < 0.05:
                # Redistribute excess
                excess = 0.05 - base_neutral
                reduction = excess / 2
                base_positive -= reduction
                base_negative -= reduction
                base_neutral = 0.05
                
            # Post volume tends to increase on weekdays
            is_weekday = current_date.weekday() < 5
            base_volume = random.randint(20, 50) if is_weekday else random.randint(5, 25)
            
            # Create data point
            data_point = {
                'date': current_date.strftime('%Y-%m-%d'),
                'positive': round(base_positive, 3),
                'negative': round(base_negative, 3),
                'neutral': round(base_neutral, 3),
                'volume': base_volume
            }
            
            result.append(data_point)
            
            # Increment
            current_date += datetime.timedelta(days=1)
            day_count += 1
            
        return result
