import unittest

def run_tests(test_directory='.'):
    # Create a loader object
    loader = unittest.TestLoader()
    
    # Discover and load all unittest test cases from the test_directory
    suite = loader.discover(start_dir=test_directory, pattern='test*.py')
    
    # Create a test runner that will print the results to the console
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the test suite
    runner.run(suite)

if __name__ == "__main__":
    test_directory = 'test_framework'  # Replace with the correct path to your tests
    run_tests()
