import logging
import re
import nltk
from textblob import TextBlob

class SentimentAnalyzer:
    def __init__(self):
        """
        Initialize FinBERT-inspired financial sentiment analyzer
        Uses TextBlob as the base with specialized financial lexicons
        """
        # Load nltk data if not already available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        # Load financial lexicon
        self.finance_lexicon = self.load_finance_lexicon()
        
        # Load contextual adjustments (words that modify sentiment)
        self.sentiment_modifiers = {
            'amplifiers': {
                'very': 1.5, 'extremely': 2.0, 'incredibly': 2.0, 'definitely': 1.3,
                'absolutely': 1.7, 'completely': 1.5, 'totally': 1.5, 'really': 1.3,
                'significantly': 1.4, 'substantially': 1.4, 'strongly': 1.5, 'highly': 1.5,
                'massively': 1.7, 'undoubtedly': 1.3, 'particularly': 1.2, 'especially': 1.3,
                'notably': 1.2, 'remarkably': 1.4, 'exceptionally': 1.6
            },
            'diminishers': {
                'somewhat': 0.7, 'slightly': 0.6, 'a bit': 0.7, 'barely': 0.4,
                'marginally': 0.6, 'hardly': 0.4, 'somewhat': 0.7, 'partly': 0.8,
                'partially': 0.8, 'a little': 0.7, 'mildly': 0.8, 'moderately': 0.8
            },
            'negators': {
                'not': -1.0, "n't": -1.0, 'no': -1.0, 'never': -1.0, 'neither': -1.0,
                'nor': -1.0, 'none': -1.0, 'nothing': -1.0, 'nobody': -1.0, 'nowhere': -1.0,
                'without': -1.0, 'lack': -1.0, 'lacking': -1.0, 'lacks': -1.0
            }
        }
        
        # Common financial entities
        self.financial_entities = {
            'companies': self._load_companies(),
            'indices': ['S&P', 'S&P 500', 'Dow', 'Dow Jones', 'DJIA', 'Nasdaq', 'Russell', 'Russell 2000', 
                       'FTSE', 'Nikkei', 'SSE', 'Hang Seng', 'VIX', 'Fear Index', 'QQQ', 'SPY', 'DIA', 'IWM',
                       'SMH', 'XLF', 'XLE', 'XLV', 'XLK', 'XLI', 'XLU', 'XLP', 'XLY', 'XLRE', 'XLC', 'XBI'],
            'crypto': ['BTC', 'Bitcoin', 'ETH', 'Ethereum', 'XRP', 'Ripple', 'DOGE', 'Dogecoin', 'crypto',
                      'Binance', 'Tether', 'USDT', 'stablecoin', 'blockchain', 'NFT', 'mining', 'SOL', 'Solana',
                      'ADA', 'Cardano', 'DOT', 'Polkadot', 'SHIB', 'Shiba Inu', 'AVAX', 'Avalanche', 'MATIC', 'Polygon',
                      'LTC', 'Litecoin', 'LINK', 'Chainlink', 'UNI', 'Uniswap', 'CRO', 'Crypto.com', 'wallet',
                      'exchange', 'DeFi', 'decentralized', 'DEX', 'CEX', 'yield farming', 'staking', 'APY'],
            'etfs': ['VTI', 'VOO', 'VIG', 'VYM', 'SCHD', 'JEPI', 'JEPQ', 'SPYD', 'VEA', 'VWO', 'VXUS', 'BND',
                    'VCIT', 'VCSH', 'VTIP', 'VGSH', 'TLT', 'GOVT', 'VGLT', 'VNQ', 'VNQI', 'GLD', 'IAU', 'SLV',
                    'ARKK', 'ARKG', 'ARKW', 'ARKF', 'ARKX', 'TQQQ', 'SQQQ', 'UPRO', 'SPXU', 'SOXL', 'SOXS'],
            'investment_styles': ['value', 'growth', 'income', 'dividend', 'momentum', 'defensive', 'cyclical',
                                 'contrarian', 'bogleheads', 'FIRE', 'leanFIRE', 'fatFIRE', 'indexing', 'passive',
                                 'active', 'fundamental', 'technical', 'swing', 'day trading', 'long term', 
                                 'buy and hold', 'dollar cost averaging', 'DCA', 'lump sum', 'tax loss harvesting'],
            'terms': ['bull', 'bear', 'bullish', 'bearish', 'rally', 'correction', 'crash', 'moon', 'volatile',
                     'volatility', 'resistance', 'support', 'breakout', 'trend', 'uptrend', 'downtrend', 'pattern',
                     'reversal', 'momentum', 'oversold', 'overbought', 'consolidation', 'distribution', 'accumulation',
                     'liquidity', 'sector', 'rotation', 'inflation', 'yield', 'interest rate', 'fed', 'margin',
                     'dividend', 'earnings', 'revenue', 'guidance', 'forecast', 'outlook', 'estimate', 'consensus',
                     'recession', 'depression', 'hyperinflation', 'stagflation', 'soft landing', 'hard landing',
                     'tapering', 'QE', 'quantitative easing', 'QT', 'quantitative tightening', 'FOMC', 'CPI',
                     'PCE', 'GDP', 'unemployment', 'jobs', 'housing', 'debt ceiling', 'default', 'fiscal', 'monetary',
                     'treasury', 'yield curve', 'inversion', 'steepening', 'flattening', 'spread', 'basis points'],
            'market_makers': ['Goldman', 'MS', 'Morgan Stanley', 'JPM', 'JPMorgan', 'Citadel', 'BlackRock', 'Vanguard',
                             'Fidelity', 'Schwab', 'institutions', 'hedge funds', 'pension', 'mutual funds', 'ETFs',
                             'CBOE', 'NYSE', 'NASDAQ', 'SEC', 'FINRA', 'FED', 'Federal Reserve', 'shorts', 'smart money'],
            'options_terms': ['upgrade', 'downgrade', 'target', 'valuation', 'P/E', 'PE ratio', 'market cap', 'short interest',
                             'options', 'calls', 'puts', 'expiry', 'IV', 'implied volatility', 'delta', 'gamma', 
                             'theta', 'vega', 'hedging', 'spread', 'straddle', 'strangle', 'iron condor', 'long', 
                             'short', 'position']
        }
        
        logging.debug("Enhanced FinBERT-inspired SentimentAnalyzer initialized")
    
    def load_finance_lexicon(self):
        """Load finance-specific terms with sentiment values"""
        return {
            # Bullish terms
            'bullish': 2.0, 'bull': 1.8, 'long': 1.0, 'uptrend': 1.7, 'rally': 1.5, 
            'surge': 1.8, 'jump': 1.3, 'soar': 1.8, 'thrive': 1.6, 'boom': 1.5, 
            'breakout': 1.7, 'rebound': 1.5, 'recover': 1.4, 'outperform': 1.6,
            'outperforming': 1.6, 'upgrade': 1.7, 'beat': 1.5, 'exceeded': 1.6, 
            'growth': 1.4, 'growing': 1.3, 'profitable': 1.6, 'gains': 1.5, 
            'gain': 1.4, 'winning': 1.5, 'strong': 1.3, 'strength': 1.3, 
            'opportunity': 1.2, 'promising': 1.3, 'positive': 1.3, 'upside': 1.6,
            'buy': 1.3, 'undervalued': 1.4, 'discount': 1.2, 'bargain': 1.3,
            'momentum': 1.2, 'moon': 2.5, 'rocket': 2.0, 'diamond hands': 1.7,
            'tendies': 1.8, 'stonks': 1.5, 'hold': 0.5, 'hodl': 1.0, 'buy the dip': 1.5,
            'green': 1.2, 'oversold': 1.3, 'bottomed': 1.4, 'bottom': 1.0, 
            'accumulate': 1.2, 'accumulation': 1.1, 'squeeze': 1.0, 'rip': 1.5,
            'dividend': 1.3, 'yield': 1.2, 'compounding': 1.4, 'income': 1.2,
            'passive': 1.1, 'appreciation': 1.3, 'allocation': 0.5, 'diversification': 0.8,
            'hedge': 0.8, 'value investing': 1.2, 'bogleheads': 0.7, 'fire': 1.2, 
            'retirement': 0.9, 'etf': 0.6, 'index fund': 0.6, 'alpha': 1.3, 'leveraged': 0.8,
            
            # Bearish terms
            'bearish': -2.0, 'bear': -1.8, 'short': -1.0, 'downtrend': -1.7, 'correction': -1.2, 
            'plunge': -1.8, 'crash': -2.0, 'dump': -1.7, 'tumble': -1.6, 'tank': -2.0, 
            'collapse': -1.9, 'sell off': -1.5, 'selloff': -1.5, 'drop': -1.4, 'falling': -1.4, 
            'slump': -1.6, 'underperform': -1.6, 'underperforming': -1.6, 'downgrade': -1.7,
            'miss': -1.5, 'missed': -1.5, 'disappointing': -1.6, 'disappointed': -1.5, 
            'losses': -1.5, 'losing': -1.4, 'loss': -1.5, 'weak': -1.3, 'weakness': -1.3,
            'risk': -1.1, 'risky': -1.2, 'negative': -1.3, 'downside': -1.6, 'sell': -0.5,
            'overvalued': -1.4, 'expensive': -1.2, 'bubble': -1.5, 'drilling': -1.4,
            'bagholding': -1.5, 'bagholder': -1.5, 'paper hands': -1.0, 'rekt': -1.7,
            'red': -1.2, 'overbought': -1.3, 'topped': -1.4, 'top': -0.8, 
            'distribution': -1.1, 'resistance': -0.8, 'drill': -1.3, 'bust': -1.5,
            'bankruptcy': -1.9, 'insolvent': -1.8, 'default': -1.7, 'hyperinflation': -1.6,
            'recession': -1.5, 'depression': -1.8, 'stagflation': -1.6, 'deflation': -1.4,
            'margin call': -1.6, 'leverage': -0.7, 'debt': -0.9, 'liquidation': -1.5,
            
            # Neutral/context-dependent terms with slight bias
            'volatile': -0.3, 'volatility': -0.3, 'uncertainty': -0.4, 'stabilize': 0.4,
            'consolidate': 0.2, 'consolidation': 0.1, 'sideways': 0.0, 'flat': 0.0,
            'cautious': -0.3, 'careful': -0.3, 'patience': 0.2, 'wait': 0.0, 'holding': 0.3,
            'steady': 0.2, 'yolo': 0.2, 'fomo': -0.2, 'rotation': 0.1, 'mixed': 0.0,
            'swing': 0.1, 'trade': 0.0, 'volume': 0.0, 'liquidity': 0.1, 'range': 0.0,
            'support': 0.8, 'hedged': 0.3, 'hedging': 0.0, 'hedge': 0.1, 'protection': 0.2,
            'invest': 0.3, 'investing': 0.3, 'investment': 0.2, 'portfolio': 0.1, 
            'diversify': 0.4, 'asset': 0.0, 'allocation': 0.2, 'rebalance': 0.1,
            'passive': 0.2, 'active': 0.1, 'cash': 0.0, 'bonds': 0.1, 'equities': 0.1,
            'stocks': 0.1, 'mutual fund': 0.1, 'etf': 0.1, 'index': 0.1, 'market': 0.0,
            'capital': 0.0, 'expense ratio': -0.1, 'fee': -0.2, 'commission': -0.2,
            'tax': -0.2, 'taxable': -0.1, 'roth': 0.2, 'ira': 0.1, '401k': 0.1, 
            'vanguard': 0.1, 'fidelity': 0.1, 'schwab': 0.1, 'bogle': 0.2
        }
    
    def _load_companies(self):
        """Load list of popular companies/tickers"""
        # List of popular tickers and company names
        return [
            'AAPL', 'Apple', 'MSFT', 'Microsoft', 'GOOG', 'Google', 'Alphabet',
            'AMZN', 'Amazon', 'META', 'Meta', 'Facebook', 'TSLA', 'Tesla', 'NVDA', 'Nvidia',
            'JPM', 'JP Morgan', 'BAC', 'Bank of America', 'WMT', 'Walmart', 'DIS', 'Disney',
            'NFLX', 'Netflix', 'INTC', 'Intel', 'AMD', 'GME', 'GameStop', 'AMC',
            'PLTR', 'Palantir', 'NIO', 'BABA', 'Alibaba', 'UBER', 'LYFT', 'SNAP', 'Snapchat',
            'TWTR', 'Twitter', 'PFE', 'Pfizer', 'MRNA', 'Moderna', 'JNJ', 'Johnson & Johnson',
            'COIN', 'Coinbase', 'GS', 'Goldman Sachs', 'MS', 'Morgan Stanley', 'BBBY', 'Bed Bath & Beyond',
            'NOK', 'Nokia', 'VTI', 'Vanguard', 'VOO', 'JEPI', 'SCHD', 'Schwab', 'VYM', 'VIG',
            'SPY', 'QQQ', 'Invesco', 'PYPL', 'PayPal', 'SHOP', 'Shopify', 'SQ', 'Block', 'Square',
            'RBLX', 'Roblox', 'U', 'Unity', 'NET', 'Cloudflare', 'CRWD', 'CrowdStrike', 'DDOG', 'Datadog',
            'SNOW', 'Snowflake', 'ROKU', 'Roku', 'ZM', 'Zoom', 'ADBE', 'Adobe', 'CRM', 'Salesforce'
        ]
    
    def analyze_text(self, text):
        """
        Analyze text for sentiment using TextBlob with finance-specific adjustments
        Enhanced to mimic FinBERT behavior with specialized financial lexicon
        
        Returns:
            dict: Dictionary with sentiment scores (compound, pos, neg, neu)
        """
        if not text:
            return {
                'compound': 0,
                'pos': 0,
                'neg': 0,
                'neu': 1.0,
                'sentiment': 'neutral'
            }
        
        # Pre-process the text
        # Convert to lowercase for better matching
        text_lower = text.lower()
        
        # Get base sentiment from TextBlob
        blob = TextBlob(text)
        
        # Base polarity ranges from -1 to 1
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Apply financial lexicon adjustments
        adjustment = 0
        matched_terms = []
        
        # Apply lexicon using a window-based approach for multi-word terms
        words = text_lower.split()
        # Check for single word matches
        for word in words:
            if word in self.finance_lexicon:
                adjustment += self.finance_lexicon[word] / 2.5
                matched_terms.append(word)
        
        # Check for multi-word phrases (up to 3 words)
        for i in range(len(words)):
            # 2-word phrases
            if i < len(words) - 1:
                phrase = words[i] + ' ' + words[i+1]
                if phrase in self.finance_lexicon:
                    adjustment += self.finance_lexicon[phrase] / 2.5
                    matched_terms.append(phrase)
            
            # 3-word phrases
            if i < len(words) - 2:
                phrase = words[i] + ' ' + words[i+1] + ' ' + words[i+2]
                if phrase in self.finance_lexicon:
                    adjustment += self.finance_lexicon[phrase] / 2.5
                    matched_terms.append(phrase)
        
        # Apply contextual modifiers
        # First pass: identify modifier regions (negators change polarity of phrases)
        negation_regions = []
        for i, word in enumerate(words):
            if word in self.sentiment_modifiers['negators']:
                # Mark the next 3 words as being in a negation region
                negation_regions.extend(range(i+1, min(i+4, len(words))))
        
        # Second pass: apply amplifiers and diminishers
        amplifier_effect = 0
        for i, word in enumerate(words):
            if word in self.sentiment_modifiers['amplifiers']:
                # Amplifier increases the effect of the next term
                next_idx = i + 1
                while next_idx < len(words) and words[next_idx] not in matched_terms:
                    next_idx += 1
                if next_idx < len(words) and words[next_idx] in matched_terms:
                    amplifier_effect += self.sentiment_modifiers['amplifiers'][word] - 1.0
            
            elif word in self.sentiment_modifiers['diminishers']:
                # Diminisher decreases the effect of the next term
                next_idx = i + 1
                while next_idx < len(words) and words[next_idx] not in matched_terms:
                    next_idx += 1
                if next_idx < len(words) and words[next_idx] in matched_terms:
                    amplifier_effect += self.sentiment_modifiers['diminishers'][word] - 1.0
        
        # Apply negation effect
        negation_effect = 0
        for i, word in enumerate(words):
            if i in negation_regions and word in matched_terms:
                # Reverse the polarity of this term
                if word in self.finance_lexicon:
                    negation_effect -= 2 * (self.finance_lexicon[word] / 2.5)
        
        # Combine all effects
        adjustment += negation_effect
        
        # Apply amplifier/diminisher effect to the overall adjustment
        if amplifier_effect != 0 and adjustment != 0:
            adjustment = adjustment * (1 + amplifier_effect)
        
        # Adjust polarity with financial terms (limiting to -1 to 1 range)
        adjusted_polarity = max(min(polarity + adjustment, 1.0), -1.0)
        
        # Convert to VADER-like format for compatibility
        # Compound score is the adjusted polarity in -1 to 1 range
        compound = adjusted_polarity
        
        # For compatibility, generate positive/negative/neutral components
        if compound > 0:
            pos = (compound + subjectivity) / 2
            neg = 0
            neu = 1 - pos
        elif compound < 0:
            neg = (abs(compound) + subjectivity) / 2
            pos = 0
            neu = 1 - neg
        else:
            pos = 0
            neg = 0
            neu = 1.0
        
        # Ensure proportions make sense
        pos = max(0, min(pos, 1.0))
        neg = max(0, min(neg, 1.0))
        neu = max(0, min(neu, 1.0))
        
        # Normalize if needed
        total = pos + neg + neu
        if total > 0:
            pos = pos / total
            neg = neg / total
            neu = neu / total
        
        # Add subtle increases to FinBERT-specificity
        # FinBERT typically has stronger reactions to financial terms
        if len(matched_terms) > 0:
            # Boost the confidence/intensity of the sentiment
            if compound > 0:
                pos = min(pos * 1.2, 1.0)
                neu = max(1.0 - pos, 0.0)
            elif compound < 0:
                neg = min(neg * 1.2, 1.0)
                neu = max(1.0 - neg, 0.0)
        
        # Determine sentiment category with more nuanced thresholds
        if compound >= 0.15:  # More strict threshold for positive
            sentiment = 'positive'
        elif compound <= -0.15:  # More strict threshold for negative
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'compound': compound,
            'pos': pos,
            'neg': neg,
            'neu': neu,
            'sentiment': sentiment,
            'subjectivity': subjectivity,
            'matched_terms': matched_terms  # Include matched financial terms for transparency
        }
    
    def extract_entities(self, text):
        """
        Extract financial entities from text using improved pattern matching
        
        Returns:
            dict: Dictionary with categorized entities and their sentiment impact
        """
        if not text:
            return {
                'tickers': [],
                'companies': [],
                'indices': [],
                'crypto': [],
                'terms': [],
                'key_phrases': []
            }
        
        # For proper pattern matching
        text_upper = text.upper()
        text_lower = text.lower()
        
        # Find tickers using improved regex pattern
        # Common ticker formats: $AAPL, TSLA, AAPL.B (Class B shares)
        # Also finds common index tickers like ^GSPC (S&P 500), ^DJI (Dow Jones)
        ticker_pattern = r'\$?([A-Z]{1,5})(?:\.[A-Z])?|\^([A-Z]{1,5})'
        potential_tickers = set(re.findall(ticker_pattern, text))
        # Flatten and clean the results
        potential_tickers = {t[0] if t[0] else t[1] for t in potential_tickers if t[0] or t[1]}
        
        # Find key phrases related to trading, markets, and finance
        key_phrase_patterns = [
            r'\b(buy|sell|hold|long|short)\s+(?:on|the)?\s*([A-Z]{1,5})\b',
            r'\b([A-Z]{1,5})\s+(?:is|looks?|seems?|appears?)\s+(bullish|bearish)\b',
            r'\b(earnings|revenue|guidance|forecast|dividend|split)\s+(?:for|from)?\s*([A-Z]{1,5})\b',
            r'\bI\s+(?:am|\'m)\s+(bullish|bearish)\s+on\s+([A-Z]{1,5})\b',
            r'\b(calls|puts|options|leaps)\s+(?:on|for)?\s*([A-Z]{1,5})\b'
        ]
        
        key_phrases = []
        for pattern in key_phrase_patterns:
            matches = re.findall(pattern, text)
            key_phrases.extend([f"{m[0]} {m[1]}" for m in matches if len(m) >= 2])
        
        # Results dictionary with sentiment context
        results = {
            'tickers': [],
            'companies': [],
            'indices': [],
            'crypto': [],
            'etfs': [],
            'investment_styles': [],
            'terms': [],
            'market_makers': [],
            'options_terms': [],
            'key_phrases': key_phrases,
            'sentiment_context': {}  # Will store entity-specific sentiment
        }
        
        # Add potential tickers
        results['tickers'] = list(potential_tickers)
        
        # Find known companies
        for company in self.financial_entities['companies']:
            company_pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(company_pattern, text, re.IGNORECASE):
                results['companies'].append(company)
        
        # Find known indices
        for index in self.financial_entities['indices']:
            index_pattern = r'\b' + re.escape(index) + r'\b'
            if re.search(index_pattern, text, re.IGNORECASE):
                results['indices'].append(index)
        
        # Find crypto terms
        for crypto in self.financial_entities['crypto']:
            crypto_pattern = r'\b' + re.escape(crypto) + r'\b'
            if re.search(crypto_pattern, text, re.IGNORECASE):
                results['crypto'].append(crypto)
        
        # Find ETFs
        for etf in self.financial_entities['etfs']:
            etf_pattern = r'\b' + re.escape(etf) + r'\b'
            if re.search(etf_pattern, text, re.IGNORECASE):
                results['etfs'].append(etf)
        
        # Find investment styles
        for style in self.financial_entities['investment_styles']:
            style_pattern = r'\b' + re.escape(style) + r'\b'
            if re.search(style_pattern, text, re.IGNORECASE):
                results['investment_styles'].append(style)
        
        # Find financial terms
        for term in self.financial_entities['terms']:
            term_pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(term_pattern, text, re.IGNORECASE):
                results['terms'].append(term)
        
        # Find market makers
        for maker in self.financial_entities['market_makers']:
            maker_pattern = r'\b' + re.escape(maker) + r'\b'
            if re.search(maker_pattern, text, re.IGNORECASE):
                results['market_makers'].append(maker)
        
        # Find options terms
        for option in self.financial_entities['options_terms']:
            option_pattern = r'\b' + re.escape(option) + r'\b'
            if re.search(option_pattern, text, re.IGNORECASE):
                results['options_terms'].append(option)
        
        return results
    
    def get_sentiment_color(self, compound_score):
        """
        Return a color based on the sentiment score with enhanced gradation
        
        Args:
            compound_score (float): Sentiment polarity score (-1 to 1)
            
        Returns:
            str: Hex color code
        """
        if compound_score > 0:
            # Green gradation (darker green for stronger positive)
            intensity = int(min(255, 120 + (compound_score * 135)))
            return f'#{0:02x}{intensity:02x}{0:02x}'
        elif compound_score < 0:
            # Red gradation (darker red for stronger negative)
            intensity = int(min(255, 120 + (abs(compound_score) * 135)))
            return f'#{intensity:02x}{0:02x}{0:02x}'
        else:
            # Neutral gray
            return '#888888'
    
    def explain_sentiment(self, sentiment_data):
        """
        Generate a human-readable explanation of sentiment analysis results
        
        Args:
            sentiment_data (dict): The result from analyze_text()
            
        Returns:
            str: Explanation of sentiment analysis
        """
        compound = sentiment_data.get('compound', 0)
        matched_terms = sentiment_data.get('matched_terms', [])
        
        if not matched_terms:
            return "No notable financial sentiment detected."
        
        # Create explanation based on sentiment strength
        if compound >= 0.6:
            sentiment_desc = "strongly positive"
        elif compound >= 0.15:
            sentiment_desc = "positive"
        elif compound <= -0.6:
            sentiment_desc = "strongly negative"
        elif compound <= -0.15:
            sentiment_desc = "negative"
        else:
            sentiment_desc = "neutral"
        
        # Create explanation
        explanation = f"The overall financial sentiment is {sentiment_desc} "
        explanation += f"(score: {compound:.2f}). "
        
        if matched_terms:
            # Limit to top 5 terms for readability
            top_terms = matched_terms[:5]
            explanation += "Key financial terms detected: " + ", ".join(top_terms)
            if len(matched_terms) > 5:
                explanation += f" and {len(matched_terms) - 5} more."
            else:
                explanation += "."
        
        return explanation