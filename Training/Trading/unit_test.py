import unittest
from unittest.mock import patch
import random
import pandas as pd
import numpy as np


from testSlippage import TradingStrategy


class TestWalkForward(unittest.TestCase):
    def setUp(self):
        """
        Common setup for all tests
        """
        self.strategy = TradingStrategy(
            initial_capital=100,
            leverage=10,
            account_risk_pct=0.1,
            take_profit_percent=0.02,
            stop_loss_percent=0.01,
            slippage_points=2,
        )
        self.strategy.take_profit_percent = 0.02
        self.strategy.stop_loss_percent = 0.01

    def test_long_position_profit(self):
        """
        Test a long position that closes with profit
        """
        self.strategy.execute_trade(trade_signal=1, current_price=100, i=1)
        # Updated latest_price to be equal or higher than the expected TP
        self.strategy.manage_open_trade(latest_price=102.021, i=2)
        self.assertTrue(
            self.strategy.position == 0, "Position did not close as expected"
        )
        self.assertTrue(
            self.strategy.capital > 100, "Capital did not increase as expected"
        )
        self.assertTrue(
            len(self.strategy.profitable_trades) > 0, "No profitable trades recorded"
        )

    def test_long_position_loss(self):
        """
        Test a long position that closes with loss
        """
        self.strategy.execute_trade(trade_signal=1, current_price=100, i=3)
        self.strategy.manage_open_trade(latest_price=99, i=4)  # Price below SL
        self.assertTrue(self.strategy.position == 0)
        self.assertTrue(self.strategy.capital < 100)
        self.assertTrue(len(self.strategy.non_profitable_trades) > 0)

    def test_short_position_profit(self):
        """
        Test a short position that closes with profit
        """
        self.strategy.execute_trade(trade_signal=-1, current_price=100, i=5)
        # Updated latest_price to be equal or lower than the expected TP
        self.strategy.manage_open_trade(latest_price=97.98, i=6)
        self.assertTrue(
            self.strategy.position == 0, "Position did not close as expected"
        )
        self.assertTrue(
            self.strategy.capital > 100, "Capital did not increase as expected"
        )
        self.assertTrue(
            len(self.strategy.profitable_trades) > 0, "No profitable trades recorded"
        )

    def test_short_position_loss(self):
        """
        Test a short position that closes with loss
        """
        self.strategy.execute_trade(trade_signal=-1, current_price=100, i=7)
        self.strategy.manage_open_trade(latest_price=101, i=8)  # Price above SL
        self.assertTrue(self.strategy.position == 0)
        self.assertTrue(self.strategy.capital < 100)
        self.assertTrue(len(self.strategy.non_profitable_trades) > 0)

    def test_no_position_or_insufficient_capital(self):
        """
        Test for no position or insufficient capital
        """
        self.strategy.capital = 0
        self.strategy.manage_open_trade(latest_price=102, i=9)
        self.assertTrue(self.strategy.position == 0)

    def test_standard_long_position_trade(self):
        """
        Test a standard long position trade
        """
        self.strategy.execute_trade(trade_signal=1, current_price=100, i=1)
        self.assertEqual(self.strategy.position, 1)
        self.assertTrue(self.strategy.take_profits[0][1] > self.strategy.entry_price)
        self.assertTrue(self.strategy.stop_losses[0][1] < self.strategy.entry_price)

    def test_standard_short_position_trade(self):
        """
        Test a standard short position trade
        """
        self.strategy.execute_trade(trade_signal=-1, current_price=100, i=2)
        self.assertEqual(self.strategy.position, -1)
        self.assertTrue(self.strategy.take_profits[0][1] < self.strategy.entry_price)
        self.assertTrue(self.strategy.stop_losses[0][1] > self.strategy.entry_price)

    def test_insufficient_capital(self):
        """
        Test for insufficient capital
        """
        self.strategy.capital = 0

        #  I am not supposed to enter a trade if capital is negative
        self.strategy.execute_trade(trade_signal=1, current_price=100, i=3)
        self.assertEqual(self.strategy.position, 0)

    def test_correct_take_profit_calculation_long(self):
        """
        Test correct take profit calculation for a long position
        """
        self.strategy.execute_trade(trade_signal=1, current_price=100, i=4)
        expected_tp = 100 * (1 + self.strategy.take_profit_percent)
        self.assertAlmostEqual(round(self.strategy.take_profits[0][1]), expected_tp)

    def test_correct_stop_loss_calculation_long(self):
        """
        Test correct stop loss calculation for a long position
        """
        self.strategy.execute_trade(trade_signal=1, current_price=100, i=5)
        expected_sl = 100 * (1 - self.strategy.stop_loss_percent)
        self.assertAlmostEqual(round(self.strategy.stop_losses[0][1]), expected_sl)

    def test_correct_take_profit_calculation_short(self):
        """
        Test correct take profit calculation for a short position
        """
        self.strategy.execute_trade(trade_signal=-1, current_price=100, i=6)
        expected_tp = 100 * (1 - self.strategy.take_profit_percent)
        self.assertAlmostEqual(round(self.strategy.take_profits[0][1]), expected_tp)

    def test_correct_stop_loss_calculation_short(self):
        """
        Test correct stop loss calculation for a short position
        """
        self.strategy.execute_trade(trade_signal=-1, current_price=100, i=7)
        expected_sl = 100 * (1 + self.strategy.stop_loss_percent)
        self.assertAlmostEqual(round(self.strategy.stop_losses[0][1]), expected_sl)

    def test_trade_risk_deduction_from_capital(self):
        """
        Test trade risk deduction from capital
        """
        initial_capital = self.strategy.capital
        self.strategy.execute_trade(trade_signal=1, current_price=100, i=8)
        expected_capital_after_trade = initial_capital - (
            initial_capital * self.strategy.account_risk_pct
        )
        self.assertAlmostEqual(self.strategy.capital, expected_capital_after_trade)

    def test_position_size_calculation(self):
        """
        Test position size calculation
        """
        self.strategy.execute_trade(trade_signal=1, current_price=100, i=9)
        initial_capital = 100  # Assuming initial capital is 100
        expected_position_size = (
            initial_capital * self.strategy.account_risk_pct
        ) * self.strategy.leverage

        self.assertAlmostEqual(self.strategy.position_size, expected_position_size)

    def tearDown(self):
        # Reset the strategy object
        self.strategy = TradingStrategy(
            initial_capital=100,
            leverage=10,
            account_risk_pct=0.1,
            take_profit_percent=0.02,
            stop_loss_percent=0.01,
            slippage_points=2,
        )

    """
        Test cases for the walk_forward_on_Data method in the TradingStrategy class
    """

    def test_walk_forward_no_gaps(self):
        data = pd.DataFrame(
            {
                "Open": np.arange(100, 110, 1),
                "High": np.arange(101, 111, 1),
                "Low": np.arange(
                    100.5, 110.5, 1
                ),  # Set 'Low' higher than initial stop_loss
                "Close": np.arange(100.5, 110.5, 1),
            }
        )

        sign = 1  # Long position
        result = self.strategy.walk_forward_on_Data(data, sign)
        print(f"Trailing stop loss result: {result}")

        self.assertIsNone(result, "Expected open trade, got a closed trade")

    def test_increasing_trend(self):
        data = pd.DataFrame(
            {
                "Open": np.arange(100, 110, 1),
                "High": np.arange(100.5, 110.5, 1),
                "Low": np.arange(100, 110, 1),
                "Close": np.arange(100.5, 110.5, 1),
            }
        )
        sign = 1  # Long position
        result = self.strategy.walk_forward_on_Data(data, sign)
        print(f"Trailing increasing trend result: {result}")

        self.assertIsNone(result, "Expected open trade, got a closed trade")

    def test_decreasing_trend(self):
        data = pd.DataFrame(
            {
                "Open": np.arange(100, 90, -1),
                "High": np.arange(100, 90, -1),
                "Low": np.arange(99, 89, -1),
                "Close": np.arange(99.5, 89.5, -1),
            }
        )
        sign = 1  # Long position
        result = self.strategy.walk_forward_on_Data(data, sign)
        print(f"Trailing decreasing trend result: {result}")

        self.assertIsNotNone(result, "Expected open trade, got a closed trade")

    def test_fluctuating_prices(self):
        data = pd.DataFrame(
            {
                "Open": [100, 101, 102, 101, 100, 99],
                "High": [101, 102, 103, 102, 101, 100],
                "Low": [99, 100, 101, 100, 99, 98],
                "Close": [100, 101, 102, 101, 100, 99],
            }
        )
        sign = 1  # Long position
        result = self.strategy.walk_forward_on_Data(data, sign)
        print(f"Trailing fluctuating result: {result}")

        self.assertIsNotNone(
            result, "Expected position to close due to stop-loss breach"
        )

    def test_gapping_prices(self):
        data = pd.DataFrame(
            {
                "Open": [100, 90],
                "High": [100, 90],
                "Low": [100, 90],
                "Close": [100, 90],
            }
        )
        sign = 1  # Long position
        result = self.strategy.walk_forward_on_Data(data, sign)
        print(f"Trailing gapping result: {result}")

        self.assertIsNotNone(result, "Expected position to close due to price gap")

    def test_sideways_market(self):
        data = pd.DataFrame(
            {
                "Open": np.arange(100, 110, 1),
                "High": np.arange(101, 111, 1),
                "Low": np.arange(99, 109, 1),
                "Close": np.arange(100, 110, 1),
            }
        )
        sign = 1  # Long position
        result = self.strategy.walk_forward_on_Data(data, sign)
        print(f"Trailing sideways market result: {result}")

        self.assertIsNone(result, "Expected position to remain open in sideways market")

    def test_sharp_price_increase(self):
        data = pd.DataFrame(
            {
                "Open": np.arange(100, 120, 2),
                "High": np.arange(101, 121, 2),
                "Low": np.arange(100, 120, 2),
                "Close": np.arange(101, 121, 2),
            }
        )
        sign = 1  # Long position
        result = self.strategy.walk_forward_on_Data(data, sign)
        print(f"Trailing sharp price increase result: {result}")

        self.assertIsNone(
            result, "Expected position to remain open with sharp price increase"
        )

    def test_false_breakout(self):
        data = pd.DataFrame(
            {
                "Open": [100, 105, 104, 103, 102],
                "High": [106, 106, 105, 104, 103],
                "Low": [99, 104, 103, 102, 101],
                "Close": [105, 104, 103, 102, 101],
            }
        )
        sign = 1  # Long position
        result = self.strategy.walk_forward_on_Data(data, sign)
        print(f"Trailing false breakout result: {result}")

        self.assertIsNotNone(result, "Expected position to close due to false breakout")


if __name__ == "__main__":
    unittest.main()
