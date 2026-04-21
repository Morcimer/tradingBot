import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import main
except ImportError:
    main = None

class TestImports(unittest.TestCase):
    """Test that main modules can be imported without errors"""
    
    def test_main_import(self):
        """Test that main.py can be imported"""
        self.assertIsNotNone(main, "main module should be importable")
        
    def test_dependencies(self):
        """Test that key dependencies are available"""
        try:
            import yfinance
            import pandas
            import numpy
        except ImportError as e:
            self.fail(f"Required dependency not installed: {e}")

if __name__ == '__main__':
    unittest.main()
