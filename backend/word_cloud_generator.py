import os
import re
from datetime import datetime

try:
    import numpy as np
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud, STOPWORDS
    WORDCLOUD_AVAILABLE = True
except ImportError:
    # Fallback if modules are not available
    WORDCLOUD_AVAILABLE = False

def generate_word_cloud(text, post_id):
    """
    Generate a word cloud from the given text and save it as an image
    
    Args:
        text (str): Text to generate word cloud from
        post_id (str): Post ID to use in the filename
        
    Returns:
        str: Path to the generated word cloud image or None if word cloud generation fails
    """
    # Check if required modules are available
    if not WORDCLOUD_AVAILABLE:
        return None
        
    # If text is too short, don't create word cloud
    if not text or len(text.split()) < 10:
        return None
    
    try:
        # Create directory if it doesn't exist
        static_dir = os.path.join('static', 'images', 'wordclouds')
        os.makedirs(static_dir, exist_ok=True)
        
        # Create filename with timestamp to avoid caching issues
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{post_id}_{timestamp}.png"
        filepath = os.path.join(static_dir, filename)
        
        # Process text: lowercase and remove special characters
        processed_text = text.lower()
        processed_text = re.sub(r'[^\w\s]', '', processed_text)
        
        # Add financial stopwords
        stopwords = set(STOPWORDS)
        financial_stopwords = {
            'stock', 'stocks', 'market', 'markets', 'trade', 'trading', 'trader',
            'invest', 'investing', 'investment', 'investor', 'money', 'price',
            'prices', 'buy', 'sell', 'call', 'put', 'option', 'options', 'share',
            'shares', 'just', 'like', 'going', 'get', 'got', 'think', 'know',
            'really', 'make', 'made', 'one', 'now', 'would', 'could', 'should',
            'will', 'year', 'month', 'day', 'today', 'tomorrow', 'yesterday',
            'week', 'good', 'bad', 'high', 'low', 'much', 'many', 'few', 'lot',
            'big', 'small', 'http', 'https', 'com', 'www', 'amp', 'im', 'dont',
            'cant', 'wont', 'isnt', 'ive', 'thats', 'theyre', 'youre', 'theyll',
            'reddit', 'comment', 'post', 'submission', 'thread', 'retard', 'retards',
            'ape', 'apes', 'wallstreetbets', 'wsb'
        }
        
        # Add financial stopwords to STOPWORDS
        for word in financial_stopwords:
            stopwords.add(word)
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            max_words=100,
            background_color='white',
            colormap='YlGnBu',
            stopwords=stopwords,
            min_font_size=10
        ).generate(processed_text)
        
        # Save to file
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        # Return the URL path to the image
        return f"/static/images/wordclouds/{filename}"
    except Exception as e:
        print(f"Error generating word cloud: {e}")
        return None