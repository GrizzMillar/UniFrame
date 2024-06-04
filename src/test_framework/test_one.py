import unittest

import unittest

class TestMathOperations(unittest.TestCase):

    def setUp(self):
        # This method will be called before each test case runs.
        self.a = 10
        self.b = 5

    def test_addition(self):
        # Test case for addition
        result = self.a + self.b
        self.assertEqual(result, 15)

    def test_subtraction(self):
        # Test case for subtraction
        result = self.a - self.b
        self.assertEqual(result, 5)

    def test_multiplication(self):
        # Test case for multiplication
        result = self.a * self.b
        self.assertEqual(result, 50)

    def test_division(self):
        # Test case for division
        result = self.a / self.b
        self.assertEqual(result, 2)

    def tearDown(self):
        # This method will be called after each test case runs.
        pass

if __name__ == '__main__':
    unittest.main()
