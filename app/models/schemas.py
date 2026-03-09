from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class QuoteCategory(str, Enum):
    """Quote categories"""
    MOTIVATION = "motivation"
    INSPIRATION = "inspiration"
    SUCCESS = "success"
    LOVE = "love"
    HUMOR = "humor"

class EmotionType(str, Enum):
    """Emotion types"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"

class SentimentScore(BaseModel):
    """Sentiment analysis result"""
    polarity: float = Field(..., ge=-1, le=1, description="Polarity from -1 (negative) to 1 (positive)")
    subjectivity: float = Field(..., ge=0, le=1, description="Subjectivity from 0 (objective) to 1 (subjective)")
    emotion: EmotionType = Field(..., description="Detected emotion")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")

class Quote(BaseModel):
    """Quote model"""
    id: str
    text: str
    author: str
    category: QuoteCategory
    sentiment: Optional[str] = None
    relevance_score: Optional[float] = None

class Message(BaseModel):
    """Chat message model"""
    id: str
    role: str = Field(..., description="'user' or 'bot'")
    content: str
    timestamp: datetime
    sentiment: Optional[SentimentScore] = None
    emotion: Optional[str] = None
    intent: Optional[str] = None

class ChatRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., min_length=1, max_length=1000)
    user_id: str = "default"

class ChatResponse(BaseModel):
    """Chat response"""
    status: str = "success"
    user_sentiment: SentimentScore
    detected_intent: str
    quote: Optional[Quote] = None
    ai_response: str
    suggestions: List[str] = []
    message_id: str
    timestamp: datetime

class QuoteRecommendationRequest(BaseModel):
    """Quote recommendation request"""
    sentiment: str
    category: Optional[QuoteCategory] = None
    user_preferences: Optional[dict] = {}

class UserPreferences(BaseModel):
    """User preferences"""
    theme: str = "light"
    favorite_categories: List[QuoteCategory] = []
    notification_enabled: bool = True
    language: str = "en"

class ConversationHistory(BaseModel):
    """Conversation history"""
    id: str
    user_id: str
    messages: List[Message]
    start_time: datetime
    end_time: Optional[datetime] = None
    sentiment_trend: dict

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    status_code: int
    timestamp: datetime
    request_id: Optional[str] = None

class AIGenerationRequest(BaseModel):
    """AI generation request"""
    prompt: str = Field(..., min_length=1, max_length=2000)
    context: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500

class SentimentAnalysisRequest(BaseModel):
    """Sentiment analysis request"""
    text: str = Field(..., min_length=1, max_length=1000)
