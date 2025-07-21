"""
File processing utilities
"""
import os
from typing import Optional


def read_file_content(file_path: str) -> str:
    """
    Read file content with proper encoding handling.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file cannot be decoded
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Try different encodings
    encodings = ['utf-8', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, read as binary and replace invalid characters
    with open(file_path, 'rb') as file:
        content = file.read()
        return content.decode('utf-8', errors='replace')


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    
    This is a rough estimation based on character count.
    More sophisticated tokenization could be implemented later.
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def is_text_file(file_path: str) -> bool:
    """
    Check if a file is likely to be a text file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file appears to be text, False otherwise
    """
    # Common text file extensions
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json',
        '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.log',
        '.sql', '.sh', '.bat', '.ps1', '.java', '.c', '.cpp', '.h',
        '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
        '.scala', '.clj', '.hs', '.ml', '.fs', '.r', '.m', '.pl',
        '.tcl', '.lua', '.vim', '.emacs', '.gitignore', '.dockerignore'
    }
    
    _, ext = os.path.splitext(file_path.lower())
    if ext in text_extensions:
        return True
    
    # Check if filename suggests text file
    basename = os.path.basename(file_path.lower())
    text_filenames = {
        'readme', 'license', 'changelog', 'authors', 'contributors',
        'makefile', 'dockerfile', 'vagrantfile', 'gemfile', 'requirements'
    }
    
    if basename in text_filenames:
        return True
    
    # Try to read first few bytes to detect binary files
    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(1024)
            if b'\x00' in chunk:  # Null bytes suggest binary file
                return False
        return True
    except:
        return False