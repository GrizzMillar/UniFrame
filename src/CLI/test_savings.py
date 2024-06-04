import unittest
from src.SavingsAccount import SavingsAccount
class TestCurrentAccount(unittest.TestCase):
      
      def InitialiseCurrentAccount(self):
          current_account = SavingsAccount("Test Current Account", 500, 100)
          return current_account
      
      def test_getName(self):
          current_account = self.InitialiseCurrentAccount()
          self.assertEqual(current_account.getName(), "Test Current Account")

      def test_getBalance(self):
          current_account = self.InitialiseCurrentAccount()
          self.assertEqual(current_account.getBalance(), 500)

      def test_getOverdraft(self):
          current_account = self.InitialiseCurrentAccount()
          self.assertEqual(current_account.getOverdraft(), 100)

      def test_deposit(self):
          current_account = self.InitialiseCurrentAccount()
          current_account.deposit(100)
          self.assertEqual(current_account.getBalance(), 600)

      def test_deposit_false(self):
          current_account = self.InitialiseCurrentAccount()
          current_account.deposit(0)
          self.assertEqual(current_account.getBalance(), 500)

      def test_withdraw(self):
          current_account = self.InitialiseCurrentAccount()
          current_account.withdraw(100)
          self.assertEqual(current_account.getBalance(), 400)

      def test_withdraw_false(self):
          current_account = self.InitialiseCurrentAccount()
          current_account.withdraw(0)
          self.assertEqual(current_account.getBalance(), 500)

