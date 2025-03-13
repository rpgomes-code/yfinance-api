"""Service for tracking API usage metrics."""
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Callable, Dict, List, Optional, Set, Tuple
import threading
import asyncio
from dataclasses import dataclass, field

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EndpointMetrics:
    """Data class for storing endpoint metrics."""
    name: str
    path: str
    calls: int = 0
    errors: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    last_called: Optional[datetime] = None

    @property
    def avg_response_time(self) -> float:
        """Calculate the average response time."""
        if self.calls == 0:
            return 0.0
        return self.total_response_time / self.calls


@dataclass
class ServiceMetrics:
    """Data class for storing service metrics."""
    name: str
    calls: int = 0
    errors: int = 0
    total_time: float = 0.0


@dataclass
class APIMetrics:
    """Data class for storing overall API metrics."""
    start_time: datetime = field(default_factory=datetime.utcnow)
    total_requests: int = 0
    endpoint_metrics: Dict[str, EndpointMetrics] = field(default_factory=dict)
    service_metrics: Dict[str, ServiceMetrics] = field(default_factory=dict)
    active_endpoints: Set[str] = field(default_factory=set)

    @property
    def uptime_seconds(self) -> float:
        """Calculate the API uptime in seconds."""
        return (datetime.utcnow() - self.start_time).total_seconds()

    @property
    def uptime_formatted(self) -> str:
        """Format the API uptime as a string."""
        seconds = self.uptime_seconds
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"


class MetricsService:
    """
    Service for tracking API usage metrics.

    This service provides methods for tracking endpoint usage,
    service calls, and other metrics.
    """

    _instance = None
    _metrics = None
    _lock = threading.RLock()

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(MetricsService, cls).__new__(cls)
            cls._metrics = APIMetrics()
        return cls._instance

    @classmethod
    def record_request(cls) -> None:
        """
        Record a new API request.

        This method increments the total request counter.
        """
        with cls._lock:
            cls._metrics.total_requests += 1

    @classmethod
    def record_endpoint_call(
            cls,
            endpoint_name: str,
            path: str,
            response_time: float,
            error: bool = False
    ) -> None:
        """
        Record a call to an endpoint.

        Args:
            endpoint_name: Name of the endpoint
            path: HTTP path of the endpoint
            response_time: Response time in seconds
            error: Whether the call resulted in an error
        """
        with cls._lock:
            if endpoint_name not in cls._metrics.endpoint_metrics:
                cls._metrics.endpoint_metrics[endpoint_name] = EndpointMetrics(
                    name=endpoint_name,
                    path=path
                )

            metrics = cls._metrics.endpoint_metrics[endpoint_name]
            metrics.calls += 1
            metrics.total_response_time += response_time
            metrics.min_response_time = min(metrics.min_response_time, response_time)
            metrics.max_response_time = max(metrics.max_response_time, response_time)
            metrics.last_called = datetime.utcnow()

            if error:
                metrics.errors += 1

    @classmethod
    def record_service_call(
            cls,
            service_name: str,
            duration: float,
            error: bool = False
    ) -> None:
        """
        Record a call to a service.

        Args:
            service_name: Name of the service
            duration: Duration of the call in seconds
            error: Whether the call resulted in an error
        """
        with cls._lock:
            if service_name not in cls._metrics.service_metrics:
                cls._metrics.service_metrics[service_name] = ServiceMetrics(name=service_name)

            metrics = cls._metrics.service_metrics[service_name]
            metrics.calls += 1
            metrics.total_time += duration

            if error:
                metrics.errors += 1

    @classmethod
    def set_endpoint_active(cls, endpoint_name: str) -> None:
        """
        Mark an endpoint as active.

        Args:
            endpoint_name: Name of the endpoint
        """
        with cls._lock:
            cls._metrics.active_endpoints.add(endpoint_name)

    @classmethod
    def set_endpoint_inactive(cls, endpoint_name: str) -> None:
        """
        Mark an endpoint as inactive.

        Args:
            endpoint_name: Name of the endpoint
        """
        with cls._lock:
            cls._metrics.active_endpoints.discard(endpoint_name)

    @classmethod
    def get_summary(cls) -> Dict:
        """
        Get a summary of API metrics.

        Returns:
            Dict: A dictionary containing a summary of API metrics
        """
        with cls._lock:
            # Calculate overall API metrics
            total_calls = sum(m.calls for m in cls._metrics.endpoint_metrics.values())
            total_errors = sum(m.errors for m in cls._metrics.endpoint_metrics.values())
            error_rate = (total_errors / total_calls) * 100 if total_calls > 0 else 0

            # Get the top 5 endpoints by calls
            top_endpoints = sorted(
                cls._metrics.endpoint_metrics.values(),
                key=lambda m: m.calls,
                reverse=True
            )[:5]

            # Get the top 5 slowest endpoints by average response time
            slowest_endpoints = sorted(
                [m for m in cls._metrics.endpoint_metrics.values() if m.calls > 0],
                key=lambda m: m.avg_response_time,
                reverse=True
            )[:5]

            return {
                "api": {
                    "start_time": cls._metrics.start_time.isoformat(),
                    "uptime": cls._metrics.uptime_formatted,
                    "total_requests": cls._metrics.total_requests,
                    "active_endpoints": len(cls._metrics.active_endpoints),
                    "total_endpoints": len(cls._metrics.endpoint_metrics),
                    "total_services": len(cls._metrics.service_metrics),
                },
                "endpoints": {
                    "total_calls": total_calls,
                    "total_errors": total_errors,
                    "error_rate": f"{error_rate:.2f}%",
                    "top_endpoints": [
                        {
                            "name": e.name,
                            "path": e.path,
                            "calls": e.calls,
                            "errors": e.errors,
                            "avg_response_time": f"{e.avg_response_time:.6f}s",
                        }
                        for e in top_endpoints
                    ],
                    "slowest_endpoints": [
                        {
                            "name": e.name,
                            "path": e.path,
                            "avg_response_time": f"{e.avg_response_time:.6f}s",
                            "max_response_time": f"{e.max_response_time:.6f}s",
                            "calls": e.calls,
                        }
                        for e in slowest_endpoints
                    ],
                },
                "services": {
                    "metrics": [
                        {
                            "name": s.name,
                            "calls": s.calls,
                            "errors": s.errors,
                            "avg_time": f"{s.total_time / s.calls if s.calls > 0 else 0:.6f}s",
                            "error_rate": f"{(s.errors / s.calls) * 100 if s.calls > 0 else 0:.2f}%",
                        }
                        for s in cls._metrics.service_metrics.values()
                    ]
                }
            }

    @classmethod
    def get_endpoint_metrics(cls, endpoint_name: str) -> Optional[Dict]:
        """
        Get metrics for a specific endpoint.

        Args:
            endpoint_name: Name of the endpoint

        Returns:
            Optional[Dict]: Metrics for the endpoint, or None if not found
        """
        with cls._lock:
            if endpoint_name not in cls._metrics.endpoint_metrics:
                return None

            metrics = cls._metrics.endpoint_metrics[endpoint_name]
            return {
                "name": metrics.name,
                "path": metrics.path,
                "calls": metrics.calls,
                "errors": metrics.errors,
                "error_rate": f"{(metrics.errors / metrics.calls) * 100 if metrics.calls > 0 else 0:.2f}%",
                "avg_response_time": f"{metrics.avg_response_time:.6f}s",
                "min_response_time": f"{metrics.min_response_time if metrics.min_response_time != float('inf') else 0:.6f}s",
                "max_response_time": f"{metrics.max_response_time:.6f}s",
                "last_called": metrics.last_called.isoformat() if metrics.last_called else None,
                "active": metrics.name in cls._metrics.active_endpoints,
            }

    @classmethod
    def get_all_endpoint_metrics(cls) -> List[Dict]:
        """
        Get metrics for all endpoints.

        Returns:
            List[Dict]: List of endpoint metrics
        """
        with cls._lock:
            return [
                {
                    "name": metrics.name,
                    "path": metrics.path,
                    "calls": metrics.calls,
                    "errors": metrics.errors,
                    "error_rate": f"{(metrics.errors / metrics.calls) * 100 if metrics.calls > 0 else 0:.2f}%",
                    "avg_response_time": f"{metrics.avg_response_time:.6f}s",
                    "active": metrics.name in cls._metrics.active_endpoints,
                }
                for metrics in cls._metrics.endpoint_metrics.values()
            ]

    @classmethod
    def reset(cls) -> None:
        """Reset all metrics."""
        with cls._lock:
            cls._metrics = APIMetrics()

    @classmethod
    def track_endpoint_performance(cls) -> Callable:
        """
        Create a decorator for tracking endpoint performance.

        Returns:
            Callable: A decorator function
        """

        def decorator(func: Callable) -> Callable:
            endpoint_name = func.__name__

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Record the request
                cls.record_request()

                # Mark the endpoint as active
                cls.set_endpoint_active(endpoint_name)

                # Get the path from the request object
                path = "unknown"
                for arg in args:
                    if hasattr(arg, "url") and hasattr(arg.url, "path"):
                        path = arg.url.path
                        break

                # Measure response time
                start_time = time.time()
                error = False

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    error = True
                    raise
                finally:
                    response_time = time.time() - start_time
                    cls.record_endpoint_call(endpoint_name, path, response_time, error)
                    cls.set_endpoint_inactive(endpoint_name)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Record the request
                cls.record_request()

                # Mark the endpoint as active
                cls.set_endpoint_active(endpoint_name)

                # Get the path from the request object
                path = "unknown"
                for arg in args:
                    if hasattr(arg, "url") and hasattr(arg.url, "path"):
                        path = arg.url.path
                        break

                # Measure response time
                start_time = time.time()
                error = False

                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception:
                    error = True
                    raise
                finally:
                    response_time = time.time() - start_time
                    cls.record_endpoint_call(endpoint_name, path, response_time, error)
                    cls.set_endpoint_inactive(endpoint_name)

            # Return the appropriate wrapper based on whether the function is async
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator

    @classmethod
    def track_service_performance(cls, service_name: str) -> Callable:
        """
        Create a decorator for tracking service performance.

        Args:
            service_name: Name of the service

        Returns:
            Callable: A decorator function
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Measure duration
                start_time = time.time()
                error = False

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    error = True
                    raise
                finally:
                    duration = time.time() - start_time
                    cls.record_service_call(service_name, duration, error)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Measure duration
                start_time = time.time()
                error = False

                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception:
                    error = True
                    raise
                finally:
                    duration = time.time() - start_time
                    cls.record_service_call(service_name, duration, error)

            # Return the appropriate wrapper based on whether the function is async
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator