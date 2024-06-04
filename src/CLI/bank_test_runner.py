import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.discover('.', pattern='test*.py'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)