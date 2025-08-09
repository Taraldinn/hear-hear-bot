"""
Timer utilities for debate timing
Author: Tasdid Tahsin
Email: tasdidtahsin@gmail.com
"""

import asyncio
import time
from datetime import datetime, timedelta

class TimerManager:
    """Manages debate timers and timing functions"""
    
    def __init__(self):
        self.active_timers = {}  # Format: {user_id_channel_id: status}
        self.timer_tasks = {}    # Store asyncio tasks for cleanup
    
    def create_timer_key(self, user_id, channel_id):
        """Create a unique timer key"""
        return f"{user_id}_{channel_id}"
    
    def is_timer_active(self, user_id, channel_id):
        """Check if a timer is active for user in channel"""
        key = self.create_timer_key(user_id, channel_id)
        return key in self.active_timers
    
    def start_timer(self, user_id, channel_id):
        """Start a timer for user in channel"""
        key = self.create_timer_key(user_id, channel_id)
        self.active_timers[key] = {
            'start_time': time.time(),
            'user_id': user_id,
            'channel_id': channel_id,
            'active': True
        }
    
    def stop_timer(self, user_id, channel_id):
        """Stop a timer and return elapsed time"""
        key = self.create_timer_key(user_id, channel_id)
        if key in self.active_timers:
            timer_data = self.active_timers[key]
            elapsed = time.time() - timer_data['start_time']
            del self.active_timers[key]
            
            # Clean up any associated tasks
            if key in self.timer_tasks:
                self.timer_tasks[key].cancel()
                del self.timer_tasks[key]
            
            return elapsed
        return None
    
    def get_elapsed_time(self, user_id, channel_id):
        """Get elapsed time for active timer"""
        key = self.create_timer_key(user_id, channel_id)
        if key in self.active_timers:
            return time.time() - self.active_timers[key]['start_time']
        return None
    
    def format_time(self, seconds):
        """Format seconds into MM:SS format"""
        if seconds is None:
            return "00:00"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_time_string(self, seconds):
        """Get formatted time string with additional info"""
        if seconds is None:
            return "No active timer"
        
        formatted_time = self.format_time(seconds)
        
        # Add warnings for common debate time limits
        if seconds >= 420:  # 7 minutes
            return f"{formatted_time} ⚠️ (Over time!)"
        elif seconds >= 360:  # 6 minutes
            return f"{formatted_time} ⏰ (Approaching time limit)"
        else:
            return formatted_time
    
    async def auto_stop_timer(self, user_id, channel_id, duration):
        """Automatically stop timer after specified duration"""
        key = self.create_timer_key(user_id, channel_id)
        
        try:
            await asyncio.sleep(duration)
            if key in self.active_timers:
                self.stop_timer(user_id, channel_id)
        except asyncio.CancelledError:
            pass  # Timer was manually stopped
    
    def start_auto_timer(self, user_id, channel_id, duration):
        """Start a timer that automatically stops after duration"""
        self.start_timer(user_id, channel_id)
        key = self.create_timer_key(user_id, channel_id)
        
        # Create auto-stop task
        task = asyncio.create_task(self.auto_stop_timer(user_id, channel_id, duration))
        self.timer_tasks[key] = task
    
    def get_active_timers_count(self):
        """Get number of active timers"""
        return len(self.active_timers)
    
    def cleanup_timers(self):
        """Clean up all timers and tasks"""
        for task in self.timer_tasks.values():
            task.cancel()
        
        self.active_timers.clear()
        self.timer_tasks.clear()

# Global timer manager instance
timer_manager = TimerManager()
