"""Service for managing scheduled tasks."""
import asyncio
import logging
import time
from datetime import datetime, timedelta
import threading
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


class Task:
    """Class representing a scheduled task."""

    def __init__(
            self,
            func: Callable,
            interval: int,
            name: Optional[str] = None,
            args: Optional[tuple] = None,
            kwargs: Optional[dict] = None,
            immediate: bool = False,
            max_retries: int = 3,
            retry_delay: int = 5,
            on_error: Optional[Callable] = None
    ):
        """
        Initialize a scheduled task.

        Args:
            func: The function to call
            interval: The interval in seconds
            name: The name of the task
            args: Positional arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            immediate: Whether to run the task immediately
            max_retries: Maximum number of retries on failure
            retry_delay: Delay in seconds between retries
            on_error: Function to call on error
        """
        self.id = str(uuid.uuid4())
        self.func = func
        self.interval = interval
        self.name = name or func.__name__
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.immediate = immediate
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.on_error = on_error
        self.last_run = None
        self.next_run = datetime.utcnow() if immediate else datetime.utcnow() + timedelta(seconds=interval)
        self.running = False
        self.enabled = True
        self.runs = 0
        self.failures = 0
        self.last_error = None
        self.is_async = asyncio.iscoroutinefunction(func)

    def should_run(self) -> bool:
        """
        Check if the task should run.

        Returns:
            bool: True if the task should run, False otherwise
        """
        return (
                self.enabled and
                not self.running and
                datetime.utcnow() >= self.next_run
        )

    async def run(self) -> bool:
        """
        Run the task.

        Returns:
            bool: True if the task completed successfully, False otherwise
        """
        if self.running:
            return False

        self.running = True
        self.runs += 1
        self.last_run = datetime.utcnow()
        self.next_run = datetime.utcnow() + timedelta(seconds=self.interval)

        retries = 0
        success = False

        while retries <= self.max_retries and not success:
            try:
                if self.is_async:
                    await self.func(*self.args, **self.kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None, lambda: self.func(*self.args, **self.kwargs)
                    )
                success = True
            except Exception as e:
                retries += 1
                self.last_error = str(e)

                if retries <= self.max_retries:
                    logger.warning(
                        f"Task {self.name} failed (attempt {retries}/{self.max_retries}): {str(e)}"
                    )
                    await asyncio.sleep(self.retry_delay)
                else:
                    self.failures += 1
                    logger.error(f"Task {self.name} failed after {retries} attempts: {str(e)}")

                    if self.on_error:
                        try:
                            if asyncio.iscoroutinefunction(self.on_error):
                                await self.on_error(self, e)
                            else:
                                loop = asyncio.get_event_loop()
                                await loop.run_in_executor(
                                    None, lambda: self.on_error(self, e)
                                )
                        except Exception as error_e:
                            logger.error(f"Error handler for task {self.name} failed: {str(error_e)}")

        self.running = False
        return success


class SchedulerService:
    """
    Service for managing scheduled tasks.

    This service provides methods for scheduling and managing tasks.
    """

    _instance = None
    _tasks = {}
    _running = False
    _lock = threading.RLock()
    _task_runner = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(SchedulerService, cls).__new__(cls)
        return cls._instance

    @classmethod
    async def start(cls) -> None:
        """Start the scheduler."""
        with cls._lock:
            if cls._running:
                logger.warning("Scheduler is already running")
                return

            cls._running = True

        logger.info("Starting scheduler")
        cls._task_runner = asyncio.create_task(cls._run())

    @classmethod
    async def stop(cls) -> None:
        """Stop the scheduler."""
        with cls._lock:
            if not cls._running:
                logger.warning("Scheduler is not running")
                return

            cls._running = False

            if cls._task_runner:
                cls._task_runner.cancel()
                try:
                    await cls._task_runner
                except asyncio.CancelledError:
                    pass
                cls._task_runner = None

        logger.info("Scheduler stopped")

    @classmethod
    async def _run(cls) -> None:
        """Run the scheduler loop."""
        while cls._running:
            tasks_to_run = []

            # Find tasks that should run
            with cls._lock:
                for task_id, task in cls._tasks.items():
                    if task.should_run():
                        tasks_to_run.append(task)

            # Run tasks
            for task in tasks_to_run:
                try:
                    await task.run()
                except Exception as e:
                    logger.error(f"Error running task {task.name}: {str(e)}")

            # Sleep for a short time
            await asyncio.sleep(1)

    @classmethod
    def schedule(
            cls,
            func: Callable,
            interval: int,
            name: Optional[str] = None,
            args: Optional[tuple] = None,
            kwargs: Optional[dict] = None,
            immediate: bool = False,
            max_retries: int = 3,
            retry_delay: int = 5,
            on_error: Optional[Callable] = None
    ) -> str:
        """
        Schedule a task.

        Args:
            func: The function to call
            interval: The interval in seconds
            name: The name of the task
            args: Positional arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            immediate: Whether to run the task immediately
            max_retries: Maximum number of retries on failure
            retry_delay: Delay in seconds between retries
            on_error: Function to call on error

        Returns:
            str: The task ID
        """
        with cls._lock:
            task = Task(
                func=func,
                interval=interval,
                name=name,
                args=args,
                kwargs=kwargs,
                immediate=immediate,
                max_retries=max_retries,
                retry_delay=retry_delay,
                on_error=on_error
            )
            cls._tasks[task.id] = task
            logger.info(f"Scheduled task {task.name} with ID {task.id}")
            return task.id

    @classmethod
    def schedule_decorator(
            cls,
            interval: int,
            name: Optional[str] = None,
            immediate: bool = False,
            max_retries: int = 3,
            retry_delay: int = 5,
            on_error: Optional[Callable] = None
    ) -> Callable:
        """
        Create a decorator for scheduling tasks.

        Args:
            interval: The interval in seconds
            name: The name of the task
            immediate: Whether to run the task immediately
            max_retries: Maximum number of retries on failure
            retry_delay: Delay in seconds between retries
            on_error: Function to call on error

        Returns:
            Callable: A decorator function
        """

        def decorator(func: Callable) -> Callable:
            task_id = cls.schedule(
                func=func,
                interval=interval,
                name=name or func.__name__,
                immediate=immediate,
                max_retries=max_retries,
                retry_delay=retry_delay,
                on_error=on_error
            )

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            # Store the task ID on the function
            wrapper.task_id = task_id

            return wrapper

        return decorator

    @classmethod
    def unschedule(cls, task_id: str) -> bool:
        """
        Unschedule a task.

        Args:
            task_id: The task ID

        Returns:
            bool: True if the task was unscheduled, False otherwise
        """
        with cls._lock:
            if task_id not in cls._tasks:
                logger.warning(f"Task with ID {task_id} not found")
                return False

            task = cls._tasks.pop(task_id)
            logger.info(f"Unscheduled task {task.name} with ID {task_id}")
            return True

    @classmethod
    def get_task(cls, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: The task ID

        Returns:
            Optional[Task]: The task, or None if not found
        """
        with cls._lock:
            return cls._tasks.get(task_id)

    @classmethod
    def get_all_tasks(cls) -> Dict[str, Task]:
        """
        Get all tasks.

        Returns:
            Dict[str, Task]: Dictionary of tasks
        """
        with cls._lock:
            return cls._tasks.copy()

    @classmethod
    def enable_task(cls, task_id: str) -> bool:
        """
        Enable a task.

        Args:
            task_id: The task ID

        Returns:
            bool: True if the task was enabled, False otherwise
        """
        with cls._lock:
            task = cls._tasks.get(task_id)
            if not task:
                logger.warning(f"Task with ID {task_id} not found")
                return False

            task.enabled = True
            logger.info(f"Enabled task {task.name} with ID {task_id}")
            return True

    @classmethod
    def disable_task(cls, task_id: str) -> bool:
        """
        Disable a task.

        Args:
            task_id: The task ID

        Returns:
            bool: True if the task was disabled, False otherwise
        """
        with cls._lock:
            task = cls._tasks.get(task_id)
            if not task:
                logger.warning(f"Task with ID {task_id} not found")
                return False

            task.enabled = False
            logger.info(f"Disabled task {task.name} with ID {task_id}")
            return True

    @classmethod
    def get_task_status(cls, task_id: str) -> Optional[Dict]:
        """
        Get the status of a task.

        Args:
            task_id: The task ID

        Returns:
            Optional[Dict]: Status of the task, or None if not found
        """
        with cls._lock:
            task = cls._tasks.get(task_id)
            if not task:
                return None

            return {
                "id": task.id,
                "name": task.name,
                "enabled": task.enabled,
                "running": task.running,
                "runs": task.runs,
                "failures": task.failures,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "last_error": task.last_error,
                "interval": task.interval,
                "max_retries": task.max_retries,
                "retry_delay": task.retry_delay,
            }

    @classmethod
    def get_all_task_statuses(cls) -> List[Dict]:
        """
        Get the status of all tasks.

        Returns:
            List[Dict]: List of task statuses
        """
        with cls._lock:
            return [
                {
                    "id": task.id,
                    "name": task.name,
                    "enabled": task.enabled,
                    "running": task.running,
                    "runs": task.runs,
                    "failures": task.failures,
                    "last_run": task.last_run.isoformat() if task.last_run else None,
                    "next_run": task.next_run.isoformat() if task.next_run else None,
                    "interval": task.interval,
                }
                for task in cls._tasks.values()
            ]