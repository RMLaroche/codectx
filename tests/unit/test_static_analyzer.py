"""
Tests for static analyzer functionality
"""
import pytest
import tempfile
import os
from pathlib import Path

from codectx.static_analyzer import StaticAnalyzer, CodeSignature, format_signatures_output


class TestStaticAnalyzer:
    """Test cases for StaticAnalyzer class"""
    
    def test_analyzer_initialization(self):
        """Test that StaticAnalyzer initializes without errors"""
        analyzer = StaticAnalyzer()
        # Should initialize even if tree-sitter fails (fallback mode)
        assert analyzer is not None
        assert hasattr(analyzer, 'fallback_mode')
    
    def test_language_detection(self):
        """Test programming language detection from file extensions"""
        analyzer = StaticAnalyzer()
        
        assert analyzer._detect_language('test.py') == 'python'
        assert analyzer._detect_language('Test.java') == 'java'
        assert analyzer._detect_language('app.js') == 'javascript'
        assert analyzer._detect_language('component.jsx') == 'javascript'
        assert analyzer._detect_language('module.ts') == 'typescript'
        assert analyzer._detect_language('component.tsx') == 'typescript'
        assert analyzer._detect_language('README.md') is None
        assert analyzer._detect_language('config.txt') is None


class TestPythonASTAnalysis:
    """Test Python AST-based signature extraction"""
    
    def test_simple_function_extraction(self):
        """Test extraction of simple function signatures"""
        analyzer = StaticAnalyzer()
        
        code = '''
def hello_world():
    """Simple function"""
    print("Hello, World!")

def add_numbers(a: int, b: int) -> int:
    """Function with type annotations"""
    return a + b
'''
        
        signatures = analyzer._analyze_python_with_ast(code)
        
        assert len(signatures) == 2
        
        # Check first function
        hello_func = next(s for s in signatures if s.name == 'hello_world')
        assert hello_func.type == 'function'
        assert hello_func.signature == 'def hello_world():'
        assert hello_func.parameters == []
        assert hello_func.parent_class is None
        
        # Check second function with type annotations
        add_func = next(s for s in signatures if s.name == 'add_numbers')
        assert add_func.type == 'function'
        assert add_func.signature == 'def add_numbers(a: int, b: int) -> int:'
        assert add_func.parameters == ['a', 'b']
        assert add_func.return_type == 'int'
    
    def test_class_and_method_extraction(self):
        """Test extraction of class and method signatures"""
        analyzer = StaticAnalyzer()
        
        code = '''
class Calculator:
    """Simple calculator class"""
    
    def __init__(self, name: str):
        self.name = name
    
    def add(self, a: int, b: int) -> int:
        return a + b
    
    @property
    def version(self) -> str:
        return "1.0"

class AdvancedCalculator(Calculator):
    """Advanced calculator with inheritance"""
    
    def multiply(self, a: float, b: float) -> float:
        return a * b
'''
        
        signatures = analyzer._analyze_python_with_ast(code)
        
        # Should have 2 classes and 4 methods
        classes = [s for s in signatures if s.type == 'class']
        methods = [s for s in signatures if s.type == 'method']
        
        assert len(classes) == 2
        assert len(methods) == 4
        
        # Check Calculator class
        calc_class = next(s for s in classes if s.name == 'Calculator')
        assert calc_class.signature == 'class Calculator:'
        
        # Check AdvancedCalculator with inheritance
        adv_calc = next(s for s in classes if s.name == 'AdvancedCalculator')
        assert adv_calc.signature == 'class AdvancedCalculator(Calculator):'
        
        # Check methods belong to correct classes
        calc_methods = [m for m in methods if m.parent_class == 'Calculator']
        adv_methods = [m for m in methods if m.parent_class == 'AdvancedCalculator']
        
        assert len(calc_methods) == 3  # __init__, add, version
        assert len(adv_methods) == 1   # multiply
        
        # Check specific method
        add_method = next(m for m in calc_methods if m.name == 'add')
        assert add_method.signature == 'def add(self, a: int, b: int) -> int:'
        assert add_method.parameters == ['self', 'a', 'b']
        assert add_method.return_type == 'int'
    
    def test_async_function_extraction(self):
        """Test extraction of async function signatures"""
        analyzer = StaticAnalyzer()
        
        code = '''
import asyncio

async def fetch_data(url: str) -> dict:
    """Async function example"""
    # Simulate async operation
    await asyncio.sleep(1)
    return {"data": "example"}

class ApiClient:
    async def get_user(self, user_id: int) -> dict:
        """Async method example"""
        return await fetch_data(f"/users/{user_id}")
'''
        
        signatures = analyzer._analyze_python_with_ast(code)
        
        # Find async function
        fetch_func = next(s for s in signatures if s.name == 'fetch_data')
        assert fetch_func.type == 'function'
        assert fetch_func.signature == 'async def fetch_data(url: str) -> dict:'
        assert fetch_func.return_type == 'dict'
        
        # Find async method
        get_user_method = next(s for s in signatures if s.name == 'get_user')
        assert get_user_method.type == 'method'
        assert get_user_method.signature == 'async def get_user(self, user_id: int) -> dict:'
        assert get_user_method.parent_class == 'ApiClient'
    
    def test_decorator_extraction(self):
        """Test extraction of function decorators"""
        analyzer = StaticAnalyzer()
        
        code = '''
@property
def my_property(self):
    return self._value

@staticmethod
@cache
def utility_function(x: int) -> int:
    return x * 2

class MyClass:
    @classmethod
    def create(cls, name: str):
        return cls(name)
'''
        
        signatures = analyzer._analyze_python_with_ast(code)
        
        # Check property decorator
        prop_func = next(s for s in signatures if s.name == 'my_property')
        assert '@property' in prop_func.decorators
        
        # Check multiple decorators
        util_func = next(s for s in signatures if s.name == 'utility_function')
        assert '@staticmethod' in util_func.decorators
        assert '@cache' in util_func.decorators
        
        # Check classmethod decorator
        create_method = next(s for s in signatures if s.name == 'create')
        assert '@classmethod' in create_method.decorators
    
    def test_syntax_error_handling(self):
        """Test handling of Python syntax errors"""
        analyzer = StaticAnalyzer()
        
        # Invalid Python syntax
        code = '''
def broken_function(
    # Missing closing parenthesis and colon
    print("This won't parse")
'''
        
        signatures = analyzer._analyze_python_with_ast(code)
        assert signatures == []  # Should return empty list on syntax error


class TestFileAnalysis:
    """Test file-level analysis functionality"""
    
    def test_analyze_python_file(self):
        """Test analyzing a complete Python file"""
        analyzer = StaticAnalyzer()
        
        file_content = '''#!/usr/bin/env python3
"""
Example Python module for testing
"""
from typing import Optional, List

class UserManager:
    """Manages user accounts"""
    
    def __init__(self, database_url: str):
        self.db_url = database_url
    
    def create_user(self, email: str, password: str) -> bool:
        """Create a new user account"""
        return True
    
    async def find_user(self, email: str) -> Optional[dict]:
        """Find user by email"""
        return None

def validate_email(email: str) -> bool:
    """Validate email format"""
    return "@" in email and "." in email

if __name__ == "__main__":
    manager = UserManager("sqlite:///users.db")
    print("User manager initialized")
'''
        
        signatures = analyzer.analyze_file('test_user.py', file_content)
        
        # Should extract class, methods, and function
        assert len(signatures) > 0
        
        classes = [s for s in signatures if s.type == 'class']
        methods = [s for s in signatures if s.type == 'method']
        functions = [s for s in signatures if s.type == 'function']
        
        assert len(classes) == 1
        assert len(methods) == 3
        assert len(functions) == 1
        
        # Verify class
        user_manager = classes[0]
        assert user_manager.name == 'UserManager'
        
        # Verify methods
        method_names = {m.name for m in methods}
        assert method_names == {'__init__', 'create_user', 'find_user'}
        
        # Verify function
        validate_func = functions[0]
        assert validate_func.name == 'validate_email'
    
    def test_analyze_non_python_file(self):
        """Test handling of non-Python files in fallback mode"""
        analyzer = StaticAnalyzer()
        analyzer.fallback_mode = True  # Force fallback mode
        
        # Java code (not supported in fallback mode)
        java_content = '''
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
'''
        
        signatures = analyzer.analyze_file('HelloWorld.java', java_content)
        assert signatures == []  # Should return empty for unsupported languages


class TestOutputFormatting:
    """Test signature output formatting"""
    
    def test_format_signatures_output(self):
        """Test formatting of signatures into markdown"""
        signatures = [
            CodeSignature(
                type='class',
                name='Calculator',
                signature='class Calculator:',
                parameters=[],
                return_type=None,
                decorators=[],
                parent_class=None,
                line_number=1
            ),
            CodeSignature(
                type='method',
                name='add',
                signature='def add(self, a: int, b: int) -> int:',
                parameters=['self', 'a', 'b'],
                return_type='int',
                decorators=[],
                parent_class='Calculator',
                line_number=3
            ),
            CodeSignature(
                type='function',
                name='helper',
                signature='def helper(x: str) -> bool:',
                parameters=['x'],
                return_type='bool',  
                decorators=['@staticmethod'],
                parent_class=None,
                line_number=8
            )
        ]
        
        output = format_signatures_output('test.py', signatures, 'abc123')
        
        assert '## test.py' in output
        assert 'checksum: abc123' in output
        assert '**SIGNATURE ANALYSIS**' in output
        assert '### Classes' in output
        assert '- **Calculator**' in output
        assert '  - `add`' in output
        assert '### Functions' in output
        assert '- `helper`' in output
    
    def test_format_empty_signatures(self):
        """Test formatting when no signatures are found"""
        output = format_signatures_output('empty.py', [], 'def456')
        
        assert '## empty.py' in output
        assert 'checksum: def456' in output
        assert 'No signatures found.' in output


if __name__ == '__main__':
    pytest.main([__file__])