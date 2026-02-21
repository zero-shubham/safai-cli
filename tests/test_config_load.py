import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from safai.pipeline import PipelineCreator
from safai.config import PlatformEnum, Config


class TestConfigLoad:
    """Test config loading with only config and gemini sections available"""

    def test_load_config_with_config_and_gemini_sections(self):
        """Test loading config when only config and gemini sections exist in config file"""
        with patch.object(PipelineCreator, '_load_config_file_') as mock_load:
            mock_load.return_value = {
                'platform': 'gemini',
                'one_shot': 'false',
                'recursive': 'true',
                'api_key': 'test-gemini-api-key-123',
                'model': 'gemini-1.5-flash',
                'ignore': ['test1', 'test2']
            }
            
            config_dict = {
                'path': Path('/tmp/test'),
                'platform': PlatformEnum.gemini,
                'api_key': '',
                'one_shot': False,
                'recursive': False,
                'model': '',
                'ignore': []
            }
            
            # Test that config loading works correctly
            config_from_file = PipelineCreator._load_config_file_(PlatformEnum.gemini)
            assert config_from_file['platform'] == 'gemini'
            assert config_from_file['api_key'] == 'test-gemini-api-key-123'
            assert config_from_file['model'] == 'gemini-1.5-flash'
            
            # Test that the pipeline creation works
            result = PipelineCreator.create(config_dict)
            assert result is not None

    def test_load_config_missing_gemini_section(self):
        """Test loading config when gemini section is missing"""
        with patch.object(PipelineCreator, '_load_config_file_') as mock_load:
            mock_load.return_value = {
                'platform': 'gemini',
                'one_shot': 'false'
            }
            
            config_dict = {
                'path': Path('/tmp/test'),
                'platform': PlatformEnum.gemini,
                'api_key': 'test-api-key-123',
                'one_shot': False,
                'recursive': False,
                'model': 'test-model',
                'ignore': []
            }
            
            # Test that config loading works correctly
            config_from_file = PipelineCreator._load_config_file_(PlatformEnum.gemini)
            assert config_from_file['platform'] == 'gemini'
            assert 'api_key' not in config_from_file  # gemini section missing
            
            # Test that the pipeline creation works with CLI values
            result = PipelineCreator.create(config_dict)
            assert result is not None

    def test_load_config_with_default_model(self):
        """Test loading config when model is empty and should use default"""
        with patch.object(PipelineCreator, '_load_config_file_') as mock_load:
            mock_load.return_value = {
                'platform': 'gemini',
                'api_key': 'test-gemini-api-key-123',
                'model': ''
            }
            
            config_dict = {
                'path': Path('/tmp/test'),
                'platform': PlatformEnum.gemini,
                'api_key': '',
                'one_shot': False,
                'recursive': False,
                'model': '',
                'ignore': []
            }
            
            # Test that config loading works correctly
            config_from_file = PipelineCreator._load_config_file_(PlatformEnum.gemini)
            assert config_from_file['platform'] == 'gemini'
            assert config_from_file['api_key'] == 'test-gemini-api-key-123'
            assert config_from_file['model'] == ''
            
            # Test that the pipeline creation works and uses default model
            result = PipelineCreator.create(config_dict)
            assert result is not None

    def test_load_config_cli_overrides_file(self):
        """Test that CLI parameters override config file parameters"""
        with patch.object(PipelineCreator, '_load_config_file_') as mock_load:
            mock_load.return_value = {
                'platform': 'gemini',
                'one_shot': 'false',
                'api_key': 'file-api-key',
                'model': 'gemini-1.5-flash'
            }
            
            config_dict = {
                'path': Path('/tmp/test'),
                'platform': PlatformEnum.gemini,
                'api_key': 'cli-api-key',  # CLI override
                'one_shot': True,  # CLI override
                'recursive': False,
                'model': '',
                'ignore': []
            }
            
            # Test that config loading works correctly
            config_from_file = PipelineCreator._load_config_file_(PlatformEnum.gemini)
            assert config_from_file['platform'] == 'gemini'
            assert config_from_file['api_key'] == 'file-api-key'
            assert config_from_file['model'] == 'gemini-1.5-flash'
            
            # Test that the pipeline creation works with CLI overrides
            result = PipelineCreator.create(config_dict)
            assert result is not None

    def test_config_creation_with_only_config_and_gemini(self):
        """Test direct Config creation with only config and gemini sections"""
        config_data = {
            'path': Path('/tmp/test'),
            'platform': PlatformEnum.gemini,
            'api_key': 'test-gemini-key-12345',
            'one_shot': False,
            'recursive': True,
            'model': 'gemini-1.5-flash',
            'ignore': ['test1', 'test2']
        }
        
        # Test that Config can be created with gemini platform
        config = Config(**config_data)
        assert config.platform == PlatformEnum.gemini
        assert config.api_key == 'test-gemini-key-12345'
        assert config.model == 'gemini-1.5-flash'
        assert config.one_shot == False
        assert config.recursive == True
        assert config.ignore == ['test1', 'test2']

    def test_linux_uses_home_directory(self):
        """Test that Linux uses ~/.safai approach"""
        with patch('sys.platform', 'linux'):
            with patch('pathlib.Path.exists') as mock_exists:
                mock_exists.return_value = True
                with patch('configparser.ConfigParser.read') as mock_read:
                    PipelineCreator._load_config_file_(PlatformEnum.gemini)
                    # Should only call read once for ~/.safai
                    assert mock_read.call_count == 1
                    call_args = mock_read.call_args[0][0]
                    assert str(call_args).endswith('.safai')

    def test_macos_checks_platformdirs_first(self):
        """Test that macOS checks platformdirs first, then fallback"""
        with patch('sys.platform', 'darwin'):
            with patch('safai.pipeline.platformdirs') as mock_platformdirs:
                mock_platformdirs.user_config_dir.return_value = '/Users/test/Library/Application Support/safai'
                
                with patch('pathlib.Path.exists') as mock_exists:
                    # First check platform-specific config (doesn't exist)
                    # Then check platform-specific config.ini (doesn't exist) 
                    # Then check fallback path (exists)
                    mock_exists.side_effect = [False, False, True]
                    
                    with patch('configparser.ConfigParser.read') as mock_read:
                        PipelineCreator._load_config_file_(PlatformEnum.gemini)
                        
                        # Should check all three paths
                        assert mock_exists.call_count == 3
                        assert mock_read.call_count == 1
                        
                        # Should read the fallback path
                        call_args = mock_read.call_args[0][0]
                        assert str(call_args).endswith('.safai')

    def test_windows_checks_platformdirs_first(self):
        """Test that Windows checks platformdirs first, then fallback"""
        with patch('sys.platform', 'win32'):
            with patch('safai.pipeline.platformdirs') as mock_platformdirs:
                mock_platformdirs.user_config_dir.return_value = 'C:\\Users\\test\\AppData\\Roaming\\safai'
                
                with patch('pathlib.Path.exists') as mock_exists:
                    # Platform-specific path exists
                    mock_exists.return_value = True
                    
                    with patch('configparser.ConfigParser.read') as mock_read:
                        PipelineCreator._load_config_file_(PlatformEnum.gemini)
                        
                        # Should only check once since first path exists
                        assert mock_exists.call_count == 1
                        assert mock_read.call_count == 1

    def test_no_platformdirs_fallback(self):
        """Test fallback behavior when platformdirs is not available"""
        with patch('sys.platform', 'darwin'):
            with patch('safai.pipeline.platformdirs', None):
                with patch('pathlib.Path.exists') as mock_exists:
                    mock_exists.return_value = True
                    with patch('configparser.ConfigParser.read') as mock_read:
                        PipelineCreator._load_config_file_(PlatformEnum.gemini)
                        
                        # Should only check fallback path
                        assert mock_exists.call_count == 1
                        call_args = mock_read.call_args[0][0]
                        assert str(call_args).endswith('.safai')

    def test_config_file_not_found(self):
        """Test behavior when no config file is found"""
        with patch('sys.platform', 'darwin'):
            with patch('safai.pipeline.platformdirs') as mock_platformdirs:
                mock_platformdirs.user_config_dir.return_value = '/Users/test/Library/Application Support/safai'
                
                with patch('pathlib.Path.exists') as mock_exists:
                    # No config files exist
                    mock_exists.return_value = False
                    
                    with patch('configparser.ConfigParser.read') as mock_read:
                        result = PipelineCreator._load_config_file_(PlatformEnum.gemini)
                        
                        # Should check all paths but not read any file
                        assert mock_exists.call_count == 3  # platform config, platform config.ini, fallback
                        assert mock_read.call_count == 0
                        
                        # Should return empty dict
                        assert result == {}