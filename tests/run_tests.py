import unittest
import sys
import os
from pathlib import Path

def run_tests():
    # Add project root to Python path
    project_root = str(Path(__file__).parent.parent.absolute())
    sys.path.insert(0, project_root)
    
    print(f"Added to Python path: {project_root}")
    
    # Get all test files
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)