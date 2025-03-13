"""Service for interacting with the yfinance library."""
import yfinance as yf
from typing import Any, Dict, List, Optional, Union
import logging
from functools import lru_cache

from app.core.config import settings
from app.core.exceptions import TickerNotFoundError, YFinanceError

logger = logging.getLogger(__name__)


class YFinanceService:
    """
    Service class to handle all interactions with the yfinance library.
    This centralizes yfinance usage and allows for easier mocking in tests.
    """

    @staticmethod
    def get_ticker(ticker: str) -> yf.Ticker:
        """
        Get a yfinance Ticker object.

        Args:
            ticker: The ticker symbol

        Returns:
            yf.Ticker: A yfinance Ticker object

        Raises:
            TickerNotFoundError: If the ticker cannot be found
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            # Try to access a basic property to validate the ticker exists
            _ = ticker_obj.info
            return ticker_obj
        except Exception as e:
            logger.error(f"Error initializing ticker {ticker}: {str(e)}")
            if "not found" in str(e).lower():
                raise TickerNotFoundError(ticker)
            raise YFinanceError(f"Error initializing ticker {ticker}: {str(e)}")

    @staticmethod
    def get_market(market: str) -> yf.Market:
        """
        Get a yfinance Market object.

        Args:
            market: The market identifier (e.g., 'US', 'DE')

        Returns:
            yf.Market: A yfinance Market object

        Raises:
            YFinanceError: If the market cannot be initialized
        """
        try:
            return yf.Market(market)
        except Exception as e:
            logger.error(f"Error initializing market {market}: {str(e)}")
            raise YFinanceError(f"Error initializing market {market}: {str(e)}")

    @staticmethod
    def get_search(query: str) -> yf.Search:
        """
        Get a yfinance Search object.

        Args:
            query: The search query

        Returns:
            yf.Search: A yfinance Search object

        Raises:
            YFinanceError: If the search cannot be initialized
        """
        try:
            return yf.Search(query)
        except Exception as e:
            logger.error(f"Error initializing search for {query}: {str(e)}")
            raise YFinanceError(f"Error initializing search for {query}: {str(e)}")

    @staticmethod
    def get_sector(sector: str) -> yf.Sector:
        """
        Get a yfinance Sector object.

        Args:
            sector: The sector identifier

        Returns:
            yf.Sector: A yfinance Sector object

        Raises:
            YFinanceError: If the sector cannot be initialized
        """
        try:
            return yf.Sector(sector)
        except Exception as e:
            logger.error(f"Error initializing sector {sector}: {str(e)}")
            raise YFinanceError(f"Error initializing sector {sector}: {str(e)}")

    @staticmethod
    def get_industry(industry: str) -> yf.Industry:
        """
        Get a yfinance Industry object.

        Args:
            industry: The industry identifier

        Returns:
            yf.Industry: A yfinance Industry object

        Raises:
            YFinanceError: If the industry cannot be initialized
        """
        try:
            return yf.Industry(industry)
        except Exception as e:
            logger.error(f"Error initializing industry {industry}: {str(e)}")
            raise YFinanceError(f"Error initializing industry {industry}: {str(e)}")

    @classmethod
    def get_ticker_data(cls, ticker: str, attribute: str) -> Any:
        """
        Get data for a specific ticker and attribute.

        Args:
            ticker: The ticker symbol
            attribute: The yfinance Ticker attribute to access

        Returns:
            Any: The data from the specified attribute

        Raises:
            TickerNotFoundError: If the ticker cannot be found
            YFinanceError: If there is an error accessing the attribute
        """
        try:
            ticker_obj = cls.get_ticker(ticker)
            result = getattr(ticker_obj, attribute)

            # Check for empty or None results
            if result is None:
                logger.warning(f"Attribute {attribute} for ticker {ticker} returned None")
                return None

            if hasattr(result, "empty") and result.empty:
                logger.warning(f"Attribute {attribute} for ticker {ticker} returned empty DataFrame")
                return []

            return result

        except AttributeError as e:
            logger.error(f"Attribute {attribute} not found for ticker {ticker}: {str(e)}")
            raise YFinanceError(f"Attribute {attribute} not found for ticker {ticker}")

        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            logger.error(f"Error getting {attribute} for ticker {ticker}: {str(e)}")
            raise YFinanceError(f"Error getting {attribute} for ticker {ticker}: {str(e)}")

    @classmethod
    def get_market_data(cls, market: str, attribute: str) -> Any:
        """
        Get data for a specific market and attribute.

        Args:
            market: The market identifier
            attribute: The yfinance Market attribute to access

        Returns:
            Any: The data from the specified attribute

        Raises:
            YFinanceError: If there is an error accessing the attribute
        """
        try:
            market_obj = cls.get_market(market)
            return getattr(market_obj, attribute)
        except Exception as e:
            logger.error(f"Error getting {attribute} for market {market}: {str(e)}")
            raise YFinanceError(f"Error getting {attribute} for market {market}: {str(e)}")

    @classmethod
    def get_search_data(cls, query: str, attribute: str) -> Any:
        """
        Get data for a specific search query and attribute.

        Args:
            query: The search query
            attribute: The yfinance Search attribute to access

        Returns:
            Any: The data from the specified attribute

        Raises:
            YFinanceError: If there is an error accessing the attribute
        """
        try:
            search_obj = cls.get_search(query)
            return getattr(search_obj, attribute)
        except Exception as e:
            logger.error(f"Error getting {attribute} for search query {query}: {str(e)}")
            raise YFinanceError(f"Error getting {attribute} for search query {query}: {str(e)}")

    @classmethod
    def get_sector_data(cls, sector: str, attribute: str) -> Any:
        """
        Get data for a specific sector and attribute.

        Args:
            sector: The sector identifier
            attribute: The yfinance Sector attribute to access

        Returns:
            Any: The data from the specified attribute

        Raises:
            YFinanceError: If there is an error accessing the attribute
        """
        try:
            sector_obj = cls.get_sector(sector)
            return getattr(sector_obj, attribute)
        except Exception as e:
            logger.error(f"Error getting {attribute} for sector {sector}: {str(e)}")
            raise YFinanceError(f"Error getting {attribute} for sector {sector}: {str(e)}")

    @classmethod
    def get_industry_data(cls, industry: str, attribute: str) -> Any:
        """
        Get data for a specific industry and attribute.

        Args:
            industry: The industry identifier
            attribute: The yfinance Industry attribute to access

        Returns:
            Any: The data from the specified attribute

        Raises:
            YFinanceError: If there is an error accessing the attribute
        """
        try:
            industry_obj = cls.get_industry(industry)
            return getattr(industry_obj, attribute)
        except Exception as e:
            logger.error(f"Error getting {attribute} for industry {industry}: {str(e)}")
            raise YFinanceError(f"Error getting {attribute} for industry {industry}: {str(e)}")

    @classmethod
    @lru_cache(maxsize=100)
    def get_ticker_history(
            cls,
            ticker: str,
            period: str = "1mo",
            interval: str = "1d",
            **kwargs
    ) -> Any:
        """
        Get historical data for a ticker.

        This method is cached to improve performance for repeated requests.

        Args:
            ticker: The ticker symbol
            period: Time period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            **kwargs: Additional arguments to pass to yfinance.Ticker.history()

        Returns:
            pd.DataFrame: Historical data for the ticker

        Raises:
            TickerNotFoundError: If the ticker cannot be found
            YFinanceError: If there is an error retrieving the history
        """
        try:
            ticker_obj = cls.get_ticker(ticker)
            history = ticker_obj.history(period=period, interval=interval, **kwargs)

            if history.empty:
                logger.warning(f"No historical data found for ticker {ticker}")
                return []

            return history

        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            logger.error(f"Error getting history for ticker {ticker}: {str(e)}")
            raise YFinanceError(f"Error getting history for ticker {ticker}: {str(e)}")