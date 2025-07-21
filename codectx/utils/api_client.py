"""
API client for AI summarization service
"""
import time
from typing import Optional

import requests

from .file_processor import read_file_content, estimate_tokens
from .config import get_api_key, get_api_url, SUMMARIZE_SYSTEM_PROMPT, DEFAULT_MODEL, TOKEN_THRESHOLD


class APIError(Exception):
    """Exception raised for API-related errors."""
    pass


def summarize_file(file_path: str, mock_mode: bool = False, copy_mode: bool = False) -> str:
    """
    Summarize a file using AI or return raw content based on configuration.
    
    Args:
        file_path: Path to the file to process
        mock_mode: If True, return mock summary without API call
        copy_mode: If True, return raw content without summarization
        
    Returns:
        Formatted summary or raw content
        
    Raises:
        APIError: If API call fails
        FileNotFoundError: If file doesn't exist
    """
    try:
        content = read_file_content(file_path)
    except Exception as e:
        return f"## File: {file_path} (ERROR)\nCould not read file: {e}"
    
    token_count = estimate_tokens(content)

    if copy_mode:
        return f"## File: {file_path} (RAW CONTENT)\n{content}"

    if token_count >= TOKEN_THRESHOLD:
        if mock_mode:
            time.sleep(1)  # Simulate API delay
            return f"""## File: {file_path} (MOCKED SUMMARY)
- **Role**: This is a mocked summary of the file.
- **Classes**: None
- **Global Functions**: None
- **Dependencies**: None"""

        return _call_api(file_path, content)
    else:
        return f"## File: {file_path} (RAW CONTENT)\n{content}"


def _call_api(file_path: str, content: str) -> str:
    """
    Make API call to summarize file content.
    
    Args:
        file_path: Path to the file being summarized
        content: File content to summarize
        
    Returns:
        AI-generated summary
        
    Raises:
        APIError: If API call fails
    """
    api_key = get_api_key()
    if not api_key:
        return f"""## File: {file_path} (ERROR)
Error: No API key provided. Set the CODECTX_API_KEY environment variable."""

    api_url = get_api_url()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SUMMARIZE_SYSTEM_PROMPT
            },
            {
                "role": "user", 
                "content": f"Here is the content of {file_path}. Can you provide a concise and informative summary of this file?\n---\n{content}\n---"
            }
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            choices = response.json().get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "No content available.")
            else:
                return f"## File: {file_path} (ERROR)\nNo summary available from API."
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            return f"## File: {file_path} (ERROR)\n{error_msg}"
            
    except requests.exceptions.Timeout:
        return f"## File: {file_path} (ERROR)\nAPI request timed out."
    except requests.exceptions.RequestException as e:
        return f"## File: {file_path} (ERROR)\nAPI request failed: {e}"
    except Exception as e:
        return f"## File: {file_path} (ERROR)\nUnexpected error: {e}"