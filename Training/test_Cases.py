import unittest
from unittest.mock import patch
import random
import pandas as pd
import numpy as np


from backtest import TradingStrategy


class TestWalkForward(unittest.TestCase):
    def setUp(self):
        self.strategy = TradingStrategy(
            initial_capital=10000, position_size=1000, slippage_points=2
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

    """
        Test cases for the execute method in the TradingStrategy class
    """

    def test_buy_trade_execution_no_existing_position(self):
        current_price = 100
        self.strategy.execute_trade(1, current_price, 0)
        self.assertEqual(self.strategy.position, 1)
        self.assertEqual(len(self.strategy.entry_points), 1)
        self.assertEqual(len(self.strategy.take_profits), 1)
        self.assertEqual(len(self.strategy.stop_losses), 1)

    def test_sell_trade_execution_no_existing_position(self):
        current_price = 100
        self.strategy.execute_trade(-1, current_price, 0)
        self.assertEqual(self.strategy.position, -1)
        self.assertEqual(len(self.strategy.entry_points), 1)
        self.assertEqual(len(self.strategy.take_profits), 1)
        self.assertEqual(len(self.strategy.stop_losses), 1)

    def test_no_trade_execution_existing_position(self):
        self.strategy.position = 1  # Mock existing position
        current_price = 100
        self.strategy.execute_trade(1, current_price, 0)
        self.assertEqual(len(self.strategy.entry_points), 0)

    def test_close_long_position_take_profit(self):
        # Mock a long position
        self.strategy.position = 1
        self.strategy.entry_points.append((0, 100))
        self.strategy.take_profits.append((0, 102))
        self.strategy.stop_losses.append((0, 99))
        self.strategy.manage_open_trade(102, 1)
        self.assertEqual(self.strategy.position, 0)
        self.assertTrue(self.strategy.capital > 10000)

    def test_close_long_position_stop_loss(self):
        # Mock a long position
        self.strategy.position = 1
        self.strategy.entry_points.append((0, 100))
        self.strategy.take_profits.append((0, 102))
        self.strategy.stop_losses.append((0, 99))
        self.strategy.manage_open_trade(99, 1)
        self.assertEqual(self.strategy.position, 0)
        self.assertTrue(self.strategy.capital < 10000)

    def test_close_short_position_take_profit(self):
        # Mock a short position
        self.strategy.position = -1
        self.strategy.entry_points.append((0, 100))
        self.strategy.take_profits.append((0, 98))
        self.strategy.stop_losses.append((0, 101))
        self.strategy.manage_open_trade(98, 1)
        self.assertEqual(self.strategy.position, 0)
        self.assertTrue(self.strategy.capital > 10000)

    def test_close_short_position_stop_loss(self):
        # Mock a short position
        self.strategy.position = -1
        self.strategy.entry_points.append((0, 100))
        self.strategy.take_profits.append((0, 98))
        self.strategy.stop_losses.append((0, 101))
        self.strategy.manage_open_trade(101, 1)
        self.assertEqual(self.strategy.position, 0)
        self.assertTrue(self.strategy.capital < 10000)

    def test_realistic_slippage_calculation(self):
        with patch("random.randint", return_value=3):
            current_price = 100
            self.strategy.execute_trade(1, current_price, 0)
            self.assertNotEqual(self.strategy.entry_price, current_price)

    def test_correct_tp_sl_calculation(self):
        current_price = 100
        self.strategy.execute_trade(1, current_price, 0)
        expected_tp = 100 * 1.02
        expected_sl = 100 * 0.99
        self.assertAlmostEqual(self.strategy.take_profits[0][1], expected_tp, places=2)
        self.assertAlmostEqual(self.strategy.stop_losses[0][1], expected_sl, places=2)

    def test_trade_execution_with_random_slippage(self):
        with patch("random.randint", return_value=3):
            current_price = 100
            self.strategy.execute_trade(1, current_price, 0)
            expected_slippage = 3 / 10000
            entry_price_with_slippage = current_price + expected_slippage
            self.assertAlmostEqual(
                self.strategy.entry_price, entry_price_with_slippage, places=5
            )
    """

    def test_close_long_position_take_profit_manage(self):
        self.strategy.entry_points = [(0, 100)]
        self.strategy.position = 1  # Long position
        self.strategy.take_profits = [(0, 105)]
        self.strategy.stop_losses = [(0, 95)]
        latest_close = 106  # Above take profit
        self.strategy.manage_open_trade(latest_close, 1)
        expected_pnl = 105 - 0.0002 - 100  # Expected pnl after slippage
        self.assertEqual(self.strategy.capital, 10000 + expected_pnl)
        self.assertEqual(self.strategy.position, 0)

    def test_close_long_position_stop_loss_manage(self):
        self.strategy.entry_points = [(0, 100)]
        self.strategy.position = 1  # Long position
        self.strategy.take_profits = [(0, 105)]
        self.strategy.stop_losses = [(0, 95)]
        latest_close = 94  # Below stop loss
        self.strategy.manage_open_trade(latest_close, 1)
        expected_pnl = 95 + 0.0002 - 100  # Expected pnl after slippage
        self.assertEqual(self.strategy.capital, 10000 + expected_pnl)
        self.assertEqual(self.strategy.position, 0)

    def test_close_short_position_take_profit_manage(self):
        self.strategy.entry_points = [(0, 100)]
        self.strategy.position = -1  # Short position
        self.strategy.take_profits = [(0, 95)]
        self.strategy.stop_losses = [(0, 105)]
        latest_close = 94  # Below take profit
        self.strategy.manage_open_trade(latest_close, 1)
        expected_pnl = 100 - (95 + 0.0002)  # Expected pnl after slippage
        self.assertEqual(self.strategy.capital, 10000 + expected_pnl)
        self.assertEqual(self.strategy.position, 0)

    def test_close_short_position_stop_loss_manage(self):
        self.strategy.entry_points = [(0, 100)]
        self.strategy.position = -1  # Short position
        self.strategy.take_profits = [(0, 95)]
        self.strategy.stop_losses = [(0, 105)]
        latest_close = 106  # Above stop loss
        self.strategy.manage_open_trade(latest_close, 1)
        expected_pnl = 100 - (105 - 0.0002)  # Expected pnl after slippage
        self.assertEqual(self.strategy.capital, 10000 + expected_pnl)
        self.assertEqual(self.strategy.position, 0)

    """
if __name__ == "__main__":
    unittest.main()
