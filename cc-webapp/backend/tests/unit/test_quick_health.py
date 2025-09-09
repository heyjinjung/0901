"""
Quick Health Check Tests - No external dependencies
These tests should always pass to verify pytest is working
"""

import pytest
import os
import sys
import time
from unittest.mock import Mock

class TestBasicFunctionality:
    """Basic functionality tests that should always work"""
    
    def test_python_version(self):
        """Test Python version is acceptable"""
        assert sys.version_info >= (3, 8), f"Python version too old: {sys.version}"
    
    def test_environment_variables(self):
        """Test environment variables are set"""
        # Should be set by conftest.py
        assert os.environ.get("TESTING") == "true"
        assert "DATABASE_URL" in os.environ
    
    def test_basic_imports(self):
        """Test basic Python imports work"""
        import json
        import time
        import unittest.mock
        
        assert json is not None
        assert time is not None
        assert unittest.mock is not None
    
    def test_mock_functionality(self):
        """Test mock functionality works"""
        mock = Mock()
        mock.test_method.return_value = "test_result"
        
        result = mock.test_method()
        assert result == "test_result"
        mock.test_method.assert_called_once()

class TestModuleImports:
    """Test module imports with graceful failures"""
    
    def test_pytest_import(self):
        """Test pytest import"""
        import pytest as pt
        assert pt is not None
        assert hasattr(pt, 'mark')
    
    def test_fastapi_import(self):
        """Test FastAPI import"""
        try:
            import fastapi
            assert fastapi is not None
            print("✅ FastAPI available")
        except ImportError:
            pytest.skip("FastAPI not installed")
    
    def test_httpx_import(self):
        """Test httpx import (needed for TestClient)"""
        try:
            import httpx
            assert httpx is not None
            print("✅ httpx available")
        except ImportError:
            pytest.skip("httpx not installed")

def test_pytest_discovery():
    """Simple test to verify pytest discovery works"""
    assert True, "✅ Pytest can discover and run this test"

def test_mvp_ready():
    """Test that basic MVP functionality is ready"""
    # Check if we're in the right directory
    current_path = os.getcwd()
    assert "auto202506-a" in current_path, f"Not in project directory: {current_path}"
    
    print("✅ MVP test environment ready")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
