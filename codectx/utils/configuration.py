"""
Enhanced configuration system for codectx with multiple sources support.

Supports configuration from:
1. Environment variables (backward compatibility) 
2. Configuration files (.codectx.yml, .codectx.json, .codectx.toml)
3. CLI arguments (highest priority)
4. Default values (fallback)
"""
import os
import json
import yaml
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from pathlib import Path

# Try to import TOML support (optional)
try:
    import tomllib
    HAS_TOML = True
except ImportError:
    try:
        import tomli as tomllib
        HAS_TOML = True
    except ImportError:
        HAS_TOML = False


@dataclass
class CodectxConfig:
    """
    Comprehensive configuration for codectx with validation and type safety.
    """
    
    # Core API Configuration
    api_key: Optional[str] = None
    api_url: str = ""
    api_retry_attempts: int = 3
    api_timeout: float = 30.0
    
    # LLM Configuration (extensible for future providers)
    llm_provider: str = "mistral"  # future: "claude", "openai", "local", etc.
    llm_model: str = "codestral-latest"
    custom_system_prompt: Optional[str] = None
    
    # File Processing Configuration
    token_threshold: int = 200
    max_file_size_mb: float = 10.0
    file_extensions: List[str] = field(default_factory=lambda: [
        '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json',
        '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.log',
        '.sql', '.sh', '.bat', '.ps1', '.java', '.c', '.cpp', '.h',
        '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt'
    ])
    encoding_priority: List[str] = field(default_factory=lambda: ['utf-8', 'latin1', 'cp1252'])
    
    # Processing Behavior Configuration
    concurrent_requests: int = 5
    default_mode: str = "update"  # "update", "scan-all", "mock", "copy"
    cache_enabled: bool = False
    cache_ttl_hours: int = 24
    
    # Output Configuration
    output_filename: str = "codectx.md"
    output_format: str = "markdown"  # future: "json", "html"
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    
    # UI/Display Configuration
    log_level: str = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"
    show_progress: bool = True
    color_output: bool = True
    
    # Advanced Configuration
    ignore_patterns: List[str] = field(default_factory=lambda: [
        '__pycache__/*', '*.pyc', '.git/*', 'node_modules/*',
        '.vscode/*', '.idea/*', 'dist/*', 'build/*'
    ])
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values and raise errors for invalid ones."""
        if self.api_retry_attempts < 1:
            raise ValueError("api_retry_attempts must be at least 1")
        
        if self.api_timeout <= 0:
            raise ValueError("api_timeout must be positive")
            
        if self.token_threshold < 0:
            raise ValueError("token_threshold must be non-negative")
            
        if self.concurrent_requests < 1:
            raise ValueError("concurrent_requests must be at least 1")
        
        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")
            
        valid_modes = {"update", "scan-all", "mock", "copy", "interactive"}
        if self.default_mode not in valid_modes:
            raise ValueError(f"default_mode must be one of: {valid_modes}")
            
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"log_level must be one of: {valid_log_levels}")
            
        valid_formats = {"markdown", "json", "html"}
        if self.output_format not in valid_formats:
            raise ValueError(f"output_format must be one of: {valid_formats}")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt, using custom if provided, otherwise default."""
        if self.custom_system_prompt:
            return self.custom_system_prompt
        return DEFAULT_SYSTEM_PROMPT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            field.name: getattr(self, field.name) 
            for field in self.__dataclass_fields__.values()
        }


# Default system prompt (moved from old config)
DEFAULT_SYSTEM_PROMPT = """
You are an assistant that analyzes a source code file and produces a structured summary. Your goal is to help a developer understand the purpose of this file without including the raw code.

Follow these rules strictly:
- Summarize the overall purpose of the file in one sentence.
- List all classes with:
    - Their role in the file.
    - Their methods (name, parameters, parameter types) with a short description.
- List global functions similarly.
- Mention important internal dependencies (imports from the same project).
- DO NOT include any raw code or implementation details.
- Keep the summary concise but informative (max 300 tokens).
- Use the following Markdown format:

## File: <relative_path> (SUMMARIZED)
- **Role**: [Short description of what this file does]
- **Classes**:
  - ClassName:
    - Role: [Short description]
    - Methods:
      - method_name(param1[type], param2[type]): [Short description]
- **Global Functions**:
  - function_name(param1, param2): [Short description]
- **Dependencies**: [List of internal imports if any]
"""


class ConfigurationLoader:
    """Handles loading configuration from multiple sources with priority."""
    
    @staticmethod
    def load_config(config_file: Optional[str] = None, 
                   cli_overrides: Optional[Dict[str, Any]] = None) -> CodectxConfig:
        """
        Load configuration from multiple sources with priority:
        1. CLI arguments (highest priority)
        2. Configuration file
        3. Environment variables
        4. Defaults (lowest priority)
        """
        # Start with defaults
        config_data = {}
        
        # Load from environment variables
        env_config = ConfigurationLoader._load_from_env()
        config_data.update(env_config)
        
        # Load from configuration file
        file_config = ConfigurationLoader._load_from_file(config_file)
        if file_config:
            config_data.update(file_config)
        
        # Apply CLI overrides
        if cli_overrides:
            config_data.update(cli_overrides)
        
        # Create and return configuration object
        return CodectxConfig(**config_data)
    
    @staticmethod
    def _load_from_env() -> Dict[str, Any]:
        """Load configuration from environment variables (backward compatibility)."""
        env_config = {}
        
        # Core API configuration
        if api_key := os.getenv('CODECTX_API_KEY'):
            env_config['api_key'] = api_key
        if api_url := os.getenv('CODECTX_API_URL'):
            env_config['api_url'] = api_url
        
        # New environment variables
        if retry_attempts := os.getenv('CODECTX_API_RETRY_ATTEMPTS'):
            try:
                env_config['api_retry_attempts'] = int(retry_attempts)
            except ValueError:
                pass
        
        if timeout := os.getenv('CODECTX_API_TIMEOUT'):
            try:
                env_config['api_timeout'] = float(timeout)
            except ValueError:
                pass
        
        if token_threshold := os.getenv('CODECTX_TOKEN_THRESHOLD'):
            try:
                env_config['token_threshold'] = int(token_threshold)
            except ValueError:
                pass
        
        if llm_provider := os.getenv('CODECTX_LLM_PROVIDER'):
            env_config['llm_provider'] = llm_provider
        
        if llm_model := os.getenv('CODECTX_LLM_MODEL'):
            env_config['llm_model'] = llm_model
        
        if custom_prompt := os.getenv('CODECTX_CUSTOM_PROMPT'):
            env_config['custom_system_prompt'] = custom_prompt
        
        if output_file := os.getenv('CODECTX_OUTPUT_FILENAME'):
            env_config['output_filename'] = output_file
        
        if log_level := os.getenv('CODECTX_LOG_LEVEL'):
            env_config['log_level'] = log_level.upper()
        
        if concurrent := os.getenv('CODECTX_CONCURRENT_REQUESTS'):
            try:
                env_config['concurrent_requests'] = int(concurrent)
            except ValueError:
                pass
                
        return env_config
    
    @staticmethod
    def _load_from_file(config_file: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load configuration from file (YAML, JSON, or TOML)."""
        if config_file:
            config_path = Path(config_file)
        else:
            # Look for default config files in current directory
            for filename in ['.codectx.yml', '.codectx.yaml', '.codectx.json', '.codectx.toml']:
                config_path = Path(filename)
                if config_path.exists():
                    break
            else:
                return None
        
        if not config_path.exists():
            return None
        
        try:
            content = config_path.read_text(encoding='utf-8')
            suffix = config_path.suffix.lower()
            
            if suffix in ['.yml', '.yaml']:
                return yaml.safe_load(content)
            elif suffix == '.json':
                return json.loads(content)
            elif suffix == '.toml' and HAS_TOML:
                return tomllib.loads(content)
            else:
                print(f"Unsupported config file format: {suffix}")
                return None
                
        except Exception as e:
            print(f"Error loading config file {config_path}: {e}")
            return None
    
    @staticmethod
    def generate_sample_config(format: str = 'yaml') -> str:
        """Generate a sample configuration file content."""
        config = CodectxConfig()
        
        if format.lower() == 'yaml':
            return ConfigurationLoader._generate_yaml_config(config)
        elif format.lower() == 'json':
            return ConfigurationLoader._generate_json_config(config)
        elif format.lower() == 'toml':
            return ConfigurationLoader._generate_toml_config(config)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def _generate_yaml_config(config: CodectxConfig) -> str:
        """Generate YAML configuration with comments."""
        return """
# codectx configuration file
# This file allows you to customize codectx behavior beyond environment variables

# API Configuration
api_key: "your-api-key-here"  # or set CODECTX_API_KEY env var
api_url: ""  # optional custom API endpoint
api_retry_attempts: 3  # number of retry attempts for failed API calls
api_timeout: 30.0  # timeout in seconds for each API call

# LLM Configuration (extensible for future providers)
llm_provider: "mistral"  # current: "mistral", future: "claude", "openai", "local"
llm_model: "codestral-latest"
# custom_system_prompt: |
#   Your custom prompt here...
#   Can be multiline

# File Processing
token_threshold: 200  # files above this estimated token count get summarized
max_file_size_mb: 10.0  # skip files larger than this
file_extensions:  # file types to process
  - ".py"
  - ".js"
  - ".ts"
  - ".md"
  # ... add more as needed
encoding_priority:  # encodings to try when reading files
  - "utf-8"
  - "latin1"
  - "cp1252"

# Processing Behavior
concurrent_requests: 5  # number of parallel API requests
default_mode: "update"  # default processing mode
cache_enabled: false  # enable API response caching (future feature)
cache_ttl_hours: 24

# Output Configuration
output_filename: "codectx.md"
output_format: "markdown"  # future: "json", "html"
timestamp_format: "%Y-%m-%d %H:%M:%S"

# UI/Display
log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
show_progress: true
color_output: true

# File Ignoring (in addition to .codectxignore)
ignore_patterns:
  - "__pycache__/*"
  - "*.pyc"
  - ".git/*"
  - "node_modules/*"
  - ".vscode/*"
  - ".idea/*"
  - "dist/*"
  - "build/*"
""".strip()
    
    @staticmethod
    def _generate_json_config(config: CodectxConfig) -> str:
        """Generate JSON configuration."""
        sample_config = {
            "api_key": "your-api-key-here",
            "api_url": "",
            "api_retry_attempts": 3,
            "api_timeout": 30.0,
            "llm_provider": "mistral",
            "llm_model": "codestral-latest",
            "token_threshold": 200,
            "max_file_size_mb": 10.0,
            "concurrent_requests": 5,
            "default_mode": "update",
            "cache_enabled": False,
            "cache_ttl_hours": 24,
            "output_filename": "codectx.md",
            "output_format": "markdown",
            "timestamp_format": "%Y-%m-%d %H:%M:%S",
            "log_level": "INFO",
            "show_progress": True,
            "color_output": True,
            "file_extensions": [".py", ".js", ".ts", ".md"],
            "encoding_priority": ["utf-8", "latin1", "cp1252"],
            "ignore_patterns": ["__pycache__/*", "*.pyc", ".git/*", "node_modules/*"]
        }
        return json.dumps(sample_config, indent=2)
    
    @staticmethod  
    def _generate_toml_config(config: CodectxConfig) -> str:
        """Generate TOML configuration."""
        return """
# codectx configuration file

[api]
key = "your-api-key-here"
url = ""
retry_attempts = 3
timeout = 30.0

[llm]
provider = "mistral"
model = "codestral-latest"
# custom_system_prompt = '''
# Your custom prompt here...
# '''

[processing]
token_threshold = 200
max_file_size_mb = 10.0
concurrent_requests = 5
default_mode = "update"
cache_enabled = false
cache_ttl_hours = 24

[output]
filename = "codectx.md"
format = "markdown"
timestamp_format = "%Y-%m-%d %H:%M:%S"

[ui]
log_level = "INFO"
show_progress = true
color_output = true

[files]
extensions = [".py", ".js", ".ts", ".md"]
encoding_priority = ["utf-8", "latin1", "cp1252"]
ignore_patterns = ["__pycache__/*", "*.pyc", ".git/*", "node_modules/*"]
""".strip()


# Convenience functions for backward compatibility
def get_config(config_file: Optional[str] = None, 
              cli_overrides: Optional[Dict[str, Any]] = None) -> CodectxConfig:
    """Main function to get configuration."""
    return ConfigurationLoader.load_config(config_file, cli_overrides)


def get_api_key() -> Optional[str]:
    """Backward compatibility function."""
    config = get_config()
    return config.api_key


def get_api_url() -> str:
    """Backward compatibility function."""
    config = get_config()
    return config.api_url