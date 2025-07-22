"""
Smoke tests to verify basic functionality works
"""
import pytest
import os
from codectx import discovery, processing, ui, cli


class TestSmokeTests:
    """Basic smoke tests to verify modules load and basic functionality works"""
    
    def test_discovery_module_imports(self):
        """Test that discovery module imports correctly"""
        assert hasattr(discovery, 'discover_files')
        assert hasattr(discovery, 'FileInfo')
        assert callable(discovery.discover_files)
        
    def test_processing_module_imports(self):
        """Test that processing module imports correctly"""
        assert hasattr(processing, 'ProcessingMode')
        assert hasattr(processing, 'ProcessingConfig')
        
    def test_ui_module_imports(self):
        """Test that UI module imports correctly"""
        assert hasattr(ui, 'display_welcome')
        assert hasattr(ui, 'display_info')
        assert callable(ui.display_welcome)
        
    def test_cli_module_imports(self):
        """Test that CLI module imports correctly"""
        assert hasattr(cli, 'main')
        assert callable(cli.main)
        
    def test_basic_file_discovery(self, temp_dir, sample_files):
        """Test basic file discovery functionality"""
        result = discovery.discover_files(temp_dir)
        
        assert len(result.files_to_process) > 0
        assert isinstance(result.files_to_process[0], discovery.FileInfo)
        
    def test_processing_config_creation(self):
        """Test basic processing config creation"""
        config = processing.ProcessingConfig(
            mode=processing.ProcessingMode.MOCK,
            api_key="test"
        )
        
        assert config.mode == processing.ProcessingMode.MOCK
        assert config.api_key == "test"