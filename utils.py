"""
Utility functions for the Slskd Discord webhook.
"""
from datetime import datetime


def format_bytes(bytes_val: int) -> str:
    """Format bytes into human readable format."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024**2:
        return f"{bytes_val/1024:.1f} KB"
    elif bytes_val < 1024**3:
        return f"{bytes_val/1024**2:.1f} MB"
    else:
        return f"{bytes_val/1024**3:.1f} GB"


def format_speed(bytes_per_sec: float) -> str:
    """Format speed in bytes per second to human readable format."""
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f} B/s"
    elif bytes_per_sec < 1024**2:
        return f"{bytes_per_sec/1024:.1f} KB/s"
    elif bytes_per_sec < 1024**3:
        return f"{bytes_per_sec/1024**2:.1f} MB/s"
    else:
        return f"{bytes_per_sec/1024**3:.1f} GB/s"

def format_duration(duration_str: str) -> str:
    """Format duration string to be more human readable."""
    if not duration_str or duration_str == "Unknown":
        return "Unknown"
    
    try:
        # Parse the duration string (assuming it's in format like "00:01:23.456789")
        time_parts = duration_str.split(':')
        if len(time_parts) >= 3:
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds = float(time_parts[2])
            
            # Build human readable string
            parts = []
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            if seconds > 1:
                parts.append(f"{int(seconds)}s")
            
            return " ".join(parts) if parts else "< 1s"
        else:
            return duration_str
    except (ValueError, IndexError):
        return duration_str


def format_datetime(datetime_str: str, format_template: str = "%d/%m/%Y %H:%M") -> str:
    """Format ISO datetime string to be more human readable."""
    if not datetime_str:
        return "Unknown date"
    
    try:
        # Parse ISO datetime (handle both with and without 'Z' suffix)
        dt_str = datetime_str.replace('Z', '+00:00')
        dt = datetime.fromisoformat(dt_str)
        
        # Format as human readable string
        return dt.strftime(format_template)
    except (ValueError, AttributeError):
        return datetime_str
