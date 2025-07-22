"""
Basic integration tests for codectx
"""
import pytest
import os
from pathlib import Path

from codectx.cli import main
from unittest.mock import patch


class TestBasicIntegration:
    """Basic integration tests"""
    
    def test_mock_mode_integration(self, temp_dir, sample_files):
        """Test running codectx in mock mode"""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Test mock mode which doesn't need API key
            with patch('sys.argv', ['codectx', '--mock-mode', '--scan-all']):
                try:
                    main()
                except SystemExit as e:
                    # Expected successful exit
                    assert e.code == 0
                    
            # Check output file was created
            output_file = Path(temp_dir) / 'codectx.md'
            assert output_file.exists()
            
            # Check content has expected structure
            content = output_file.read_text()
            assert 'Project Summary' in content
            assert 'mocked summary' in content.lower()
            
        finally:
            os.chdir(original_cwd)
            
    def test_status_mode_integration(self, temp_dir, sample_files):
        """Test running codectx in status mode"""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Status mode doesn't need API key
            with patch('sys.argv', ['codectx', '--status']):
                try:
                    main()
                except SystemExit as e:
                    # Expected successful exit
                    assert e.code == 0
                    
        finally:
            os.chdir(original_cwd)