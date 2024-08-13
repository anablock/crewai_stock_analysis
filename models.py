from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class NamedUrl(BaseModel):
    name: str
    url: str

class NewsItem(BaseModel):
    title: str
    summary: str
    source: str
    date: datetime
    url: Optional[str] = None

class FinancialMetric(BaseModel):
    name: str
    value: float
    description: Optional[str] = None

class InsiderTrade(BaseModel):
    insider_name: str
    position: str
    transaction_type: str
    shares: int
    price: float
    date: datetime

class UpcomingEvent(BaseModel):
    event_type: str
    date: datetime
    description: Optional[str] = None

class CompanyInfo(BaseModel):
    name: str
    ticker: str
    industry: str
    description: str

class FinancialAnalysis(BaseModel):
    key_metrics: List[FinancialMetric]
    strengths: List[str]
    weaknesses: List[str]
    peer_comparison: str

class FilingsAnalysis(BaseModel):
    latest_10q_summary: str
    latest_10k_summary: str
    red_flags: List[str]
    positive_indicators: List[str]

class StockAnalysisReport(BaseModel):
    company_info: CompanyInfo
    recent_news: List[NewsItem]
    market_sentiment: str
    financial_analysis: FinancialAnalysis
    filings_analysis: FilingsAnalysis
    insider_trading: List[InsiderTrade]
    upcoming_events: List[UpcomingEvent]
    investment_recommendation: str
    analysis_date: datetime

class StockAnalysisRequest(BaseModel):
    company: str

class StockAnalysisResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[StockAnalysisReport] = None
    events: List[dict]