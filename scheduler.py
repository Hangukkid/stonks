"""Scheduling and timing utilities for stock data updates."""

import time
from datetime import datetime, timedelta
from typing import Optional
from logger import logger
from config import MARKET_OPEN_HOUR, MARKET_CLOSE_HOUR, UPDATE_INTERVAL_MINUTES


class UpdateScheduler:
    """Handles scheduling and timing for stock data updates."""
    
    def __init__(self):
        self.last_update = None
    
    def wait_until_next_update(self) -> None:
        """
        Wait until it's time for the next update.
        Considers market hours and update intervals.
        """
        current_time = datetime.now()
        logger.debug(f"Current time: {current_time.strftime('%H:%M:%S')}")
        
        # Check if we're outside market hours
        if self._is_outside_market_hours(current_time):
            wait_seconds = self._calculate_wait_until_market_open(current_time)
            logger.info(f"Outside market hours. Waiting {wait_seconds/3600:.1f} hours until market opens")
        else:
            # We're in market hours, wait until next update interval
            wait_seconds = self._calculate_wait_until_next_interval(current_time)
            logger.info(f"In market hours. Waiting {wait_seconds/60:.1f} minutes until next update")
        
        if wait_seconds > 0:
            logger.debug(f"Sleeping for {wait_seconds} seconds")
            time.sleep(wait_seconds)
    
    def _is_outside_market_hours(self, current_time: datetime) -> bool:
        """
        Check if current time is outside market hours.
        
        Args:
            current_time: Current datetime
            
        Returns:
            True if outside market hours
        """
        hour = current_time.hour
        return hour < MARKET_OPEN_HOUR or hour >= MARKET_CLOSE_HOUR
    
    def _calculate_wait_until_market_open(self, current_time: datetime) -> int:
        """
        Calculate seconds to wait until market opens.
        
        Args:
            current_time: Current datetime
            
        Returns:
            Seconds to wait
        """
        hour = current_time.hour
        
        if hour < MARKET_OPEN_HOUR:
            # Market opens today
            target_time = current_time.replace(
                hour=MARKET_OPEN_HOUR, 
                minute=0, 
                second=0, 
                microsecond=0
            )
        else:
            # Market opens tomorrow
            tomorrow = current_time + timedelta(days=1)
            target_time = tomorrow.replace(
                hour=MARKET_OPEN_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )
        
        wait_seconds = int((target_time - current_time).total_seconds())
        return max(0, wait_seconds)
    
    def _calculate_wait_until_next_interval(self, current_time: datetime) -> int:
        """
        Calculate seconds to wait until next update interval.
        
        Args:
            current_time: Current datetime
            
        Returns:
            Seconds to wait
        """
        # Calculate minutes since the hour started
        minutes_past_hour = current_time.minute
        
        # Find the next update interval
        next_interval = ((minutes_past_hour // UPDATE_INTERVAL_MINUTES) + 1) * UPDATE_INTERVAL_MINUTES
        
        # If we've gone past the hour, move to next hour
        if next_interval >= 60:
            next_hour = (current_time + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            target_time = next_hour
        else:
            target_time = current_time.replace(minute=next_interval, second=0, microsecond=0)
        
        wait_seconds = int((target_time - current_time).total_seconds())
        return max(0, wait_seconds)
    
    def should_update(self, force: bool = False) -> bool:
        """
        Check if an update should be performed now.
        
        Args:
            force: Force update regardless of timing
            
        Returns:
            True if update should be performed
        """
        if force:
            logger.debug("Force update requested")
            return True
        
        current_time = datetime.now()
        
        # Don't update outside market hours
        if self._is_outside_market_hours(current_time):
            logger.debug("Outside market hours, skipping update")
            return False
        
        # Check if enough time has passed since last update
        if self.last_update is None:
            logger.debug("First update, proceeding")
            return True
        
        time_since_last = current_time - self.last_update
        min_interval = timedelta(minutes=UPDATE_INTERVAL_MINUTES)
        
        if time_since_last >= min_interval:
            logger.debug(f"Sufficient time passed since last update ({time_since_last})")
            return True
        
        logger.debug(f"Not enough time since last update ({time_since_last})")
        return False
    
    def mark_update_completed(self) -> None:
        """Mark that an update has been completed."""
        self.last_update = datetime.now()
        logger.debug(f"Update completed at {self.last_update.strftime('%H:%M:%S')}")
    
    def get_next_update_time(self) -> Optional[datetime]:
        """
        Get the estimated time of the next update.
        
        Returns:
            Next update datetime or None if unknown
        """
        current_time = datetime.now()
        
        if self._is_outside_market_hours(current_time):
            # Next update is when market opens
            if current_time.hour < MARKET_OPEN_HOUR:
                return current_time.replace(
                    hour=MARKET_OPEN_HOUR, 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
            else:
                tomorrow = current_time + timedelta(days=1)
                return tomorrow.replace(
                    hour=MARKET_OPEN_HOUR,
                    minute=0,
                    second=0,
                    microsecond=0
                )
        else:
            # Next update is at next interval
            minutes_past_hour = current_time.minute
            next_interval = ((minutes_past_hour // UPDATE_INTERVAL_MINUTES) + 1) * UPDATE_INTERVAL_MINUTES
            
            if next_interval >= 60:
                next_hour = (current_time + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                return next_hour
            else:
                return current_time.replace(minute=next_interval, second=0, microsecond=0)
    
    def get_market_status(self) -> dict:
        """
        Get current market status information.
        
        Returns:
            Dictionary with market status details
        """
        current_time = datetime.now()
        is_market_open = not self._is_outside_market_hours(current_time)
        
        return {
            'current_time': current_time.strftime('%H:%M:%S'),
            'is_market_open': is_market_open,
            'market_open_hour': MARKET_OPEN_HOUR,
            'market_close_hour': MARKET_CLOSE_HOUR,
            'update_interval_minutes': UPDATE_INTERVAL_MINUTES,
            'last_update': self.last_update.strftime('%H:%M:%S') if self.last_update else None,
            'next_update': self.get_next_update_time()
        }
