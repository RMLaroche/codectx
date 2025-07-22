"""
Unit tests for the discovery module
"""
import pytest
import os
import hashlib
from pathlib import Path
from unittest.mock import patch, mock_open
from datetime import datetime

from codectx.discovery import discover_files, FileInfo, _load_ignore_patterns, _should_ignore


class TestFileInfo:
    """Test the FileInfo class"""
    
    def test_file_info_creation(self, temp_dir):
        """Test FileInfo object creation with basic file"""
        # Create test file
        test_file = Path(temp_dir) / 'test.py'
        test_file.write_text('print("hello")')
        
        # Get file stats
        stat = test_file.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        file_info = FileInfo(
            path=str(test_file),
            relative_path='test.py',
            size=stat.st_size,
            modified_time=modified_time
        )
        
        assert file_info.path == str(test_file)
        assert file_info.relative_path == 'test.py'
        assert file_info.size > 0
        assert file_info.modified_time is not None
        assert file_info.checksum is not None
        assert len(file_info.checksum) == 64  # SHA256 hex digest length
        
    def test_file_info_checksum_consistency(self, temp_dir):
        """Test that checksum is consistent for same file content"""
        test_file = Path(temp_dir) / 'test.py'
        test_file.write_text('print("hello")')
        
        stat = test_file.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        file_info1 = FileInfo(str(test_file), 'test.py', stat.st_size, modified_time)
        file_info2 = FileInfo(str(test_file), 'test.py', stat.st_size, modified_time)
        
        assert file_info1.checksum == file_info2.checksum
        
    def test_file_info_checksum_accuracy(self, temp_dir):
        """Test that checksum matches manual calculation"""
        content = "test content for checksum"
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text(content)
        
        # Manual checksum calculation
        expected_checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        stat = test_file.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        file_info = FileInfo(str(test_file), 'test.txt', stat.st_size, modified_time)
        assert file_info.checksum == expected_checksum
        
    def test_file_info_size_str(self, temp_dir):
        """Test human readable size formatting"""
        test_file = Path(temp_dir) / 'test.txt'
        test_file.write_text('x' * 500)
        
        stat = test_file.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        file_info = FileInfo(str(test_file), 'test.txt', stat.st_size, modified_time)
        
        assert file_info.size_str == '500B'
        
    def test_file_info_modified_str(self, temp_dir):
        """Test human readable modified time formatting"""
        test_file = Path(temp_dir) / 'test.txt'
        test_file.write_text('test')
        
        stat = test_file.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        file_info = FileInfo(str(test_file), 'test.txt', stat.st_size, modified_time)
        
        # Should return formatted time string
        assert isinstance(file_info.modified_str, str)
        assert len(file_info.modified_str) > 0
        
    def test_file_info_unreadable_file(self, temp_dir):
        """Test FileInfo with unreadable file"""
        test_file = Path(temp_dir) / 'test.txt'
        test_file.write_text('test')
        
        stat = test_file.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            file_info = FileInfo(str(test_file), 'test.txt', stat.st_size, modified_time)
            assert file_info.checksum == "unreadable"


class TestIgnorePatterns:
    """Test ignore pattern functionality"""
    
    def test_load_ignore_patterns_no_file(self, temp_dir):
        """Test loading ignore patterns when no .codectxignore file exists"""
        patterns = _load_ignore_patterns(temp_dir)
        
        # Should have default patterns
        assert len(patterns) > 0
        assert any('__pycache__' in pattern for pattern in patterns)
        assert any('*.tmp' in pattern for pattern in patterns)
        
    def test_load_ignore_patterns_with_file(self, temp_dir):
        """Test loading ignore patterns with custom .codectxignore file"""
        # Create custom ignore file
        ignore_content = '''
# Test ignore patterns
*.test
build/
custom_dir/*
'''
        ignore_file = Path(temp_dir) / '.codectxignore'
        ignore_file.write_text(ignore_content.strip())
        
        patterns = _load_ignore_patterns(temp_dir)
        
        # Should include both default and custom patterns
        assert '*.test' in patterns
        assert 'build/' in patterns
        assert 'custom_dir/*' in patterns
        assert any('__pycache__' in pattern for pattern in patterns)
        
    def test_should_ignore_basic_patterns(self, temp_dir):
        """Test basic ignore patterns"""
        patterns = _load_ignore_patterns(temp_dir)
        
        # Test default patterns
        assert _should_ignore(os.path.join(temp_dir, 'file.tmp'), temp_dir, patterns) == True
        assert _should_ignore(os.path.join(temp_dir, '__pycache__/module.pyc'), temp_dir, patterns) == True
        assert _should_ignore(os.path.join(temp_dir, '.git/config'), temp_dir, patterns) == True
        assert _should_ignore(os.path.join(temp_dir, 'src/main.py'), temp_dir, patterns) == False
        
    def test_should_ignore_custom_patterns(self, temp_dir):
        """Test custom ignore patterns"""
        # Create custom ignore file
        ignore_content = '''
*.log
build/*
test_*
'''
        ignore_file = Path(temp_dir) / '.codectxignore'
        ignore_file.write_text(ignore_content.strip())
        
        patterns = _load_ignore_patterns(temp_dir)
        
        # Test custom patterns
        assert _should_ignore(os.path.join(temp_dir, 'debug.log'), temp_dir, patterns) == True
        assert _should_ignore(os.path.join(temp_dir, 'build/output.bin'), temp_dir, patterns) == True
        assert _should_ignore(os.path.join(temp_dir, 'test_data.txt'), temp_dir, patterns) == True
        assert _should_ignore(os.path.join(temp_dir, 'src/main.py'), temp_dir, patterns) == False


class TestFileDiscovery:
    """Test file discovery functionality"""
    
    def test_discover_files_basic(self, temp_dir, sample_files):
        """Test basic file discovery"""
        result = discover_files(temp_dir)
        
        # Should find sample files
        file_names = {os.path.basename(f.path) for f in result.files_to_process}
        expected_files = {'small.py', 'large.py', 'binary_file.bin', 'README.md', 'config.json'}
        
        assert expected_files.issubset(file_names)
        assert len(result.files_to_process) >= len(expected_files)
        
    def test_discover_files_with_ignore(self, temp_dir, sample_files):
        """Test file discovery with ignore patterns"""
        # Create files that should be ignored
        (Path(temp_dir) / 'debug.log').write_text('log content')
        (Path(temp_dir) / 'file.tmp').write_text('temp content')
        (Path(temp_dir) / '__pycache__').mkdir()
        (Path(temp_dir) / '__pycache__' / 'module.pyc').write_text('bytecode')
        
        result = discover_files(temp_dir)
        
        file_names = {os.path.basename(f.path) for f in result.files_to_process}
        
        # Should not include ignored files
        assert 'debug.log' not in file_names
        assert 'file.tmp' not in file_names
        assert 'module.pyc' not in file_names
        
        # Should still include regular files
        assert 'small.py' in file_names
        assert 'README.md' in file_names
        
    def test_discover_files_empty_directory(self, temp_dir):
        """Test file discovery in empty directory"""
        empty_dir = Path(temp_dir) / 'empty'
        empty_dir.mkdir()
        
        result = discover_files(str(empty_dir))
        
        assert len(result.files_to_process) == 0
        
    def test_discover_files_nested_directories(self, temp_dir):
        """Test file discovery in nested directories"""
        # Create nested structure
        nested_dir = Path(temp_dir) / 'src' / 'utils'
        nested_dir.mkdir(parents=True)
        
        (nested_dir / 'helper.py').write_text('def helper(): pass')
        (Path(temp_dir) / 'main.py').write_text('import src.utils.helper')
        
        result = discover_files(temp_dir)
        
        file_paths = {f.path for f in result.files_to_process}
        
        # Should find files in nested directories
        assert any('helper.py' in path for path in file_paths)
        assert any('main.py' in path for path in file_paths)
        
    def test_discover_files_nonexistent_directory(self):
        """Test file discovery with non-existent directory"""
        with pytest.raises(ValueError):
            discover_files('/path/to/nonexistent/directory')
            
    def test_discover_files_binary_detection(self, temp_dir, sample_files):
        """Test that binary files are properly included"""
        result = discover_files(temp_dir)
        
        binary_files = [f for f in result.files_to_process if f.relative_path == 'binary_file.bin']
        assert len(binary_files) == 1
        
        binary_file = binary_files[0]
        assert binary_file.size == 5
        assert binary_file.checksum is not None
        
    def test_discover_files_sorting(self, temp_dir):
        """Test that files are returned in consistent order"""
        # Create multiple files
        files_to_create = ['zebra.py', 'alpha.py', 'beta.py']
        for filename in files_to_create:
            (Path(temp_dir) / filename).write_text(f'# {filename}')
            
        result = discover_files(temp_dir)
        
        # Files should be sorted by path
        file_names = [os.path.basename(f.path) for f in result.files_to_process if f.relative_path in files_to_create]
        python_files = [name for name in file_names if name.endswith('.py')]
        
        assert python_files == sorted(python_files)
        
    def test_discover_files_large_number(self, temp_dir):
        """Test discovering large number of files"""
        # Create many small files
        for i in range(20):
            (Path(temp_dir) / f'file_{i:03d}.py').write_text(f'# File {i}')
            
        result = discover_files(temp_dir)
        
        # Should find all files
        assert len(result.files_to_process) >= 20