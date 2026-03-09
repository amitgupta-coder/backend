import json
import random
from typing import List, Optional, Dict
from pathlib import Path
from app.models.schemas import Quote, QuoteCategory

class QuoteService:
    """
    Service for managing quotes and recommendations
    """

    def __init__(self, db_path: str = "app/data/quotes_db.json"):
        self.db_path = Path(db_path)
        self.quotes: Dict[str, List[dict]] = {}
        self.load_quotes()

    def load_quotes(self):
        """Load quotes from JSON database"""
        try:
            if self.db_path.exists():
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.quotes = json.load(f)
            else:
                self.quotes = self._get_default_quotes()
                self.save_quotes()
        except Exception as e:
            print(f"Error loading quotes: {e}")
            self.quotes = self._get_default_quotes()

    def get_quotes(self, category: Optional[str] = None) -> List[Quote]:
        """Get quotes, optionally filtered by category"""
        quotes = []
        categories = [category] if category and category in self.quotes else self.quotes.keys()

        for cat in categories:
            for quote_data in self.quotes.get(cat, []):
                quote = Quote(
                    id=f"{cat}_{len(quotes)}",
                    text=quote_data.get('text', ''),
                    author=quote_data.get('author', 'Unknown'),
                    category=cat,
                    sentiment=cat
                )
                quotes.append(quote)

        return quotes

    def get_random_quote(self, category: Optional[str] = None) -> Optional[Quote]:
        """Get a random quote"""
        quotes = self.get_quotes(category)
        if quotes:
            return random.choice(quotes)
        return None

    def recommend_quote(self, sentiment: str, category: Optional[str] = None) -> Optional[Quote]:
        """
        Recommend quote based on sentiment

        sentiment: 'positive', 'negative', 'neutral'
        """
        # Map sentiment to quote categories
        sentiment_to_categories = {
            'positive': [QuoteCategory.MOTIVATION, QuoteCategory.INSPIRATION,
                        QuoteCategory.SUCCESS],
            'negative': [QuoteCategory.MOTIVATION, QuoteCategory.INSPIRATION,
                        QuoteCategory.LOVE],
            'neutral': [QuoteCategory.INSPIRATION, QuoteCategory.SUCCESS],
            'anxious': [QuoteCategory.MOTIVATION, QuoteCategory.LOVE],
            'confident': [QuoteCategory.SUCCESS, QuoteCategory.HUMOR],
            'mixed': list(QuoteCategory)
        }

        # Get target categories
        target_categories = sentiment_to_categories.get(sentiment, list(QuoteCategory))

        # Filter by user preference if specified
        if category:
            target_categories = [cat for cat in target_categories if str(cat) == category]

        if not target_categories:
            target_categories = sentiment_to_categories.get(sentiment, list(QuoteCategory))

        # Get quotes from target categories
        all_quotes = []
        for cat in target_categories:
            all_quotes.extend(self.get_quotes(str(cat)))

        if all_quotes:
            quote = random.choice(all_quotes)
            # Add relevance score based on sentiment match
            quote.relevance_score = self._calculate_relevance(quote.category, sentiment)
            return quote

        return self.get_random_quote()

    def _calculate_relevance(self, category: str, sentiment: str) -> float:
        """Calculate relevance score (0-1)"""
        relevance_map = {
            ('motivation', 'negative'): 0.95,
            ('motivation', 'anxious'): 0.9,
            ('inspiration', 'neutral'): 0.85,
            ('success', 'confident'): 0.9,
            ('love', 'negative'): 0.8,
            ('humor', 'negative'): 0.85,
        }
        return relevance_map.get((category, sentiment), 0.7)

    def search_quotes(self, keyword: str) -> List[Quote]:
        """Search quotes by keyword"""
        keyword = keyword.lower()
        matching_quotes = []

        for category, quotes in self.quotes.items():
            for quote_data in quotes:
                text = quote_data.get('text', '').lower()
                author = quote_data.get('author', '').lower()

                if keyword in text or keyword in author:
                    matching_quotes.append(Quote(
                        id=f"{category}_{len(matching_quotes)}",
                        text=quote_data.get('text', ''),
                        author=quote_data.get('author', 'Unknown'),
                        category=category
                    ))

        return matching_quotes

    def add_quote(self, text: str, author: str, category: str):
        """Add a new quote"""
        if category not in self.quotes:
            self.quotes[category] = []

        self.quotes[category].append({
            'text': text,
            'author': author
        })
        self.save_quotes()

    def save_quotes(self):
        """Save quotes to JSON file"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.quotes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving quotes: {e}")

    @staticmethod
    def _get_default_quotes() -> Dict:
        """Get default quotes"""
        return {
            "motivation": [
                {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
                {"text": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
                {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
                {"text": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"},
                {"text": "The only impossible journey is the one you never begin.", "author": "Tony Robbins"},
            ],
            "inspiration": [
                {"text": "Everything you want is on the other side of fear.", "author": "George Addair"},
                {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
                {"text": "The only limit to our realization of tomorrow is our doubts of today.", "author": "Franklin D. Roosevelt"},
                {"text": "Great things never come from comfort zones.", "author": "Unknown"},
                {"text": "Push yourself, because no one else is going to do it for you.", "author": "Unknown"},
            ],
            "success": [
                {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
                {"text": "I find that the harder I work, the more luck I seem to have.", "author": "Thomas Jefferson"},
                {"text": "The way to get started is to quit talking and begin doing.", "author": "Walt Disney"},
                {"text": "Don't be afraid to give up the good to go for the great.", "author": "John D. Rockefeller"},
            ],
            "love": [
                {"text": "The best and most beautiful things in this world cannot be seen or even heard, but must be felt with the heart.", "author": "Helen Keller"},
                {"text": "Love is not about how much you say 'I love you', but how much you can prove it's true.", "author": "Unknown"},
                {"text": "Love all, trust a few, do wrong to none.", "author": "William Shakespeare"},
                {"text": "To love oneself is the beginning of a lifelong romance.", "author": "Oscar Wilde"},
            ],
            "humor": [
                {"text": "Why fit in when you were born to stand out?", "author": "Dr. Seuss"},
                {"text": "I'm not lazy, I'm just on energy-saving mode.", "author": "Unknown"},
                {"text": "People say nothing is impossible, but I do nothing every day.", "author": "Unknown"},
                {"text": "If you can't laugh at yourself, life's going to seem a lot longer than it is.", "author": "Taylor Swift"},
            ]
        }

# Create singleton instance
quote_service = QuoteService()
