"""
Enhanced API client for AI summarization service with retry logic and flexible configuration.
"""
import time
import logging
from typing import Optional

import requests

from .file_processor import read_file_content, estimate_tokens
from .configuration import CodectxConfig, get_config


class APIError(Exception):
    """Exception raised for API-related errors."""
    pass


def summarize_file(file_path: str, mock_mode: bool = False, copy_mode: bool = False, 
                  config: Optional[CodectxConfig] = None) -> str:
    """
    Summarize a file using AI or return raw content based on configuration.
    
    Args:
        file_path: Path to the file to process
        mock_mode: If True, return mock summary without API call
        copy_mode: If True, return raw content without summarization
        config: Configuration object (uses default if None)
        
    Returns:
        Formatted summary or raw content
        
    Raises:
        APIError: If API call fails
        FileNotFoundError: If file doesn't exist
    """
    if config is None:
        config = get_config()
    
    try:
        content = read_file_content(file_path)
    except Exception as e:
        return f"## File: {file_path} (ERROR)\nCould not read file: {e}"
    
    # Check file size limit
    file_size_mb = len(content.encode('utf-8')) / (1024 * 1024)
    if file_size_mb > config.max_file_size_mb:
        return f"## File: {file_path} (SKIPPED)\nFile size ({file_size_mb:.1f}MB) exceeds limit ({config.max_file_size_mb}MB)"
    
    token_count = estimate_tokens(content)

    if copy_mode:
        return f"## File: {file_path} (RAW CONTENT)\n{content}"

    if token_count >= config.token_threshold:
        if mock_mode:
            time.sleep(1)  # Simulate API delay
            return f"""## File: {file_path} (MOCKED SUMMARY)
- **Role**: This is a mocked summary of the file.
- **Classes**: None
- **Global Functions**: None
- **Dependencies**: None"""

        return _call_api_with_retry(file_path, content, config)
    else:
        return f"## File: {file_path} (RAW CONTENT)\n{content}"


def _call_api_with_retry(file_path: str, content: str, config: CodectxConfig) -> str:
    """
    Make API call to summarize file content with retry logic.
    
    Args:
        file_path: Path to the file being summarized
        content: File content to summarize
        config: Configuration object with retry and timeout settings
        
    Returns:
        AI-generated summary
    """
    if not config.api_key:
        return f"""## File: {file_path} (ERROR)
Error: No API key provided. Set the CODECTX_API_KEY environment variable or config file."""

    if not config.api_url:
        return f"""## File: {file_path} (ERROR)
Error: No API URL provided. Set the CODECTX_API_URL environment variable or config file."""
    
    last_error = None
    
    for attempt in range(1, config.api_retry_attempts + 1):
        try:
            if attempt > 1:
                # Exponential backoff: 2^(attempt-2) seconds (0, 2, 4, 8, ...)
                wait_time = 2 ** (attempt - 2)
                logging.info(f"Retrying API call for {file_path} (attempt {attempt}/{config.api_retry_attempts}) after {wait_time}s...")
                time.sleep(wait_time)
            
            result = _single_api_call(file_path, content, config)
            
            # If we got a successful result (not an error), return it
            if not result.startswith(f"## File: {file_path} (ERROR)"):
                if attempt > 1:
                    logging.info(f"API call succeeded for {file_path} on attempt {attempt}")
                return result
            
            # If it's an error, store it and continue to retry
            last_error = result
            
        except Exception as e:
            last_error = f"## File: {file_path} (ERROR)\nUnexpected error on attempt {attempt}: {e}"
            logging.warning(f"API call attempt {attempt} failed for {file_path}: {e}")
    
    # All attempts failed, return the last error
    logging.error(f"All {config.api_retry_attempts} API attempts failed for {file_path}")
    return last_error or f"## File: {file_path} (ERROR)\nAll {config.api_retry_attempts} API attempts failed"


def _single_api_call(file_path: str, content: str, config: CodectxConfig) -> str:
    """
    Make a single API call attempt.
    
    Args:
        file_path: Path to the file being summarized
        content: File content to summarize
        config: Configuration object
        
    Returns:
        AI-generated summary or error message
    """
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": config.llm_model,
        "messages": [
            {
                "role": "system",
                "content": config.get_system_prompt()
            },
            {
                "role": "user", 
                "content": f"Here is the content of {file_path}. Can you provide a concise and informative summary of this file?\n---\n{content}\n---"
            }
        ]
    }

    try:
        response = requests.post(
            config.api_url, 
            headers=headers, 
            json=payload, 
            timeout=config.api_timeout
        )
        
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
        return f"## File: {file_path} (ERROR)\nAPI request timed out after {config.api_timeout}s."
    except requests.exceptions.ConnectionError as e:
        return f"## File: {file_path} (ERROR)\nConnection error: {e}"
    except requests.exceptions.RequestException as e:
        return f"## File: {file_path} (ERROR)\nAPI request failed: {e}"
    except Exception as e:
        return f"## File: {file_path} (ERROR)\nUnexpected error: {e}"


# Backward compatibility functions
def get_api_key() -> Optional[str]:
    """Backward compatibility function."""
    config = get_config()
    return config.api_key


def get_api_url() -> str:
    """Backward compatibility function."""
    config = get_config()
    return config.api_url