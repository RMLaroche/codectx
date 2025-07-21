"""
Utility functions
"""
from datetime import datetime


def get_timestamp() -> str:
    """
    Get current timestamp formatted for console output.
    
    Returns:
        Formatted timestamp string with Rich markup
    """
    return f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"