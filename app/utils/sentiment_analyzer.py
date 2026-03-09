from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Tuple
import re

class SentimentAnalyzer:
    """
    Sentiment analysis service using TextBlob and VADER
    """

    def __init__(self):
        self.textblob = TextBlob
        self.vader = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of text using multiple methods

        Returns:
            {
                'polarity': float (-1 to 1),
                'subjectivity': float (0 to 1),
                'emotion': str,
                'confidence': float (0 to 1),
                'vader_scores': dict
            }
        """
        # TextBlob analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # VADER analysis
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores['compound']

        # Determine emotion
        emotion = self._classify_emotion(polarity, subjectivity, vader_compound)

        # Calculate confidence
        confidence = self._calculate_confidence(vader_scores, abs(polarity))

        return {
            'polarity': round(polarity, 3),
            'subjectivity': round(subjectivity, 3),
            'emotion': emotion,
            'confidence': round(confidence, 3),
            'vader_scores': {
                'compound': round(vader_scores['compound'], 3),
                'pos': round(vader_scores['pos'], 3),
                'neu': round(vader_scores['neu'], 3),
                'neg': round(vader_scores['neg'], 3),
            }
        }

    def _classify_emotion(self, polarity: float, subjectivity: float,
                         vader_compound: float) -> str:
        """
        Classify emotion based on polarity and subjectivity
        """
        # Combine scores for better classification
        combined_score = (polarity + (vader_compound / 2)) / 2

        if combined_score > 0.5:
            return 'positive'
        elif combined_score < -0.5:
            return 'negative'
        elif combined_score < -0.1:
            if subjectivity > 0.7:
                return 'anxious'
            return 'negative'
        elif combined_score > 0.1:
            if subjectivity < 0.3:
                return 'confident'
            return 'positive'
        else:
            return 'neutral'

    def _calculate_confidence(self, vader_scores: dict, polarity_strength: float) -> float:
        """
        Calculate confidence score based on VADER intensity
        """
        # Get the maximum intensity score
        max_intensity = max(
            vader_scores['pos'],
            vader_scores['neg'],
            vader_scores['neu']
        )

        # Confidence is based on how clear the sentiment is
        confidence = (max_intensity + polarity_strength) / 2
        return min(confidence, 1.0)

    def batch_analyze(self, texts: list) -> list:
        """Analyze multiple texts"""
        return [self.analyze(text) for text in texts]

    def get_emotion_keywords(self, emotion: str) -> list:
        """Get keywords associated with emotion"""
        emotion_keywords = {
            'positive': ['happy', 'glad', 'joyful', 'great', 'excellent', 'wonderful',
                        'amazing', 'fantastic', 'love', 'awesome'],
            'negative': ['sad', 'unhappy', 'depressed', 'terrible', 'awful', 'horrible',
                        'hate', 'bad', 'worse', 'worst'],
            'neutral': ['okay', 'normal', 'fine', 'moderate', 'average'],
            'anxious': ['worried', 'anxious', 'stressed', 'nervous', 'afraid'],
            'confident': ['confident', 'sure', 'certain', 'strong', 'powerful'],
            'mixed': ['but', 'however', 'although', 'while']
        }
        return emotion_keywords.get(emotion, [])

# Create singleton instance
sentiment_analyzer = SentimentAnalyzer()
