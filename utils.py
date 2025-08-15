"""
Utility functions for the Slskd Discord webhook.
"""


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
