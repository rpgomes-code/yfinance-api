"""Models for market-related endpoints.

This module contains model definitions for market data structures
used in the market endpoints of the API.
"""
from datetime import datetime, time
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from app.models.enums import MarketRegion


class TradingHours(BaseModel):
    """Model for market trading hours."""

    open: Optional[time] = Field(None, description="Open time")
    close: Optional[time] = Field(None, description="Close time")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            time: lambda v: v.strftime('%H:%M:%S') if v else None
        }


class MarketHours(BaseModel):
    """Model for market trading sessions."""

    regular: TradingHours = Field(..., description="Regular trading hours")
    pre: Optional[TradingHours] = Field(None, description="Pre-market trading hours")
    post: Optional[TradingHours] = Field(None, description="Post-market trading hours")


class MarketStatus(BaseModel):
    """Model for market status information."""

    market: str = Field(..., description="Market identifier")
    region: str = Field(..., description="Market region")
    exchange: Optional[str] = Field(None, description="Primary exchange")
    is_open: bool = Field(..., description="Whether the market is currently open")
    trading_hours: Optional[MarketHours] = Field(None, description="Trading hours")
    current_time: datetime = Field(..., description="Current time")
    timezone: Optional[str] = Field(None, description="Market timezone")
    holidays: Optional[List[datetime]] = Field(None, description="Upcoming market holidays")

    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class MarketOverview(BaseModel):
    """Model for market overview information."""

    market: str = Field(..., description="Market identifier")
    name: str = Field(..., description="Market name")
    is_open: bool = Field(..., description="Whether the market is currently open")
    performance: Optional[Dict[str, float]] = Field(None, description="Market performance metrics")
    indices: Optional[List[Dict[str, Union[str, float]]]] = Field(None, description="Major indices")
    active_tickers: Optional[List[Dict[str, Union[str, float]]]] = Field(None, description="Most active tickers")
    gainers: Optional[List[Dict[str, Union[str, float]]]] = Field(None, description="Top gainers")
    losers: Optional[List[Dict[str, Union[str, float]]]] = Field(None, description="Top losers")


class MarketSummary(BaseModel):
    """Model for market summary information."""

    market: str = Field(..., description="Market identifier")
    name: str = Field(..., description="Market name")
    status: MarketStatus = Field(..., description="Market status")
    overview: Optional[MarketOverview] = Field(None, description="Market overview")