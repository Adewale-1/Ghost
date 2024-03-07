import pandas as pd
import numpy as np

class PatternDetector:
    def __init__(self, error_allowed):
        self.error_allowed = error_allowed
    
        
    def is_gartley_pattern(self,lines):
        # print("Gartley Pattern")
        XA = lines[0]
        AB = lines[1]
        BC = lines[2]
        CD = lines[3]

        AB_range = np.array([0.618 - self.error_allowed, 0.618 + self.error_allowed]) * abs(XA)
        BC_range = np.array([0.382 - self.error_allowed, 0.886 + self.error_allowed]) * abs(XA)
        CD_range = np.array([1.27 - self.error_allowed, 1.618 + self.error_allowed]) * abs(XA)

        direction = 0
        # Check for Pattern Validity
        if XA > 0 and AB < 0 and BC > 0 and CD < 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = 1
            else:
                direction = np.NAN

        elif XA < 0 and AB > 0 and BC < 0 and CD > 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = -1
            else:
                direction = np.NAN

        else:
            direction = np.NAN

        return direction


    def is_butterfly_pattern(self, lines):
        # print("Butterfly Pattern")
        XA = lines[0]
        AB = lines[1]
        BC = lines[2]
        CD = lines[3]

        AB_range = np.array([0.786 - self.error_allowed, 0.786 + self.error_allowed]) * abs(XA)
        BC_range = np.array([0.382 - self.error_allowed, 0.886 + self.error_allowed]) * abs(AB)
        CD_range = np.array([1.618 - self.error_allowed, 2.618 + self.error_allowed]) * abs(BC)

        direction = 0
        # Check for Pattern Validity
        if XA > 0 and AB < 0 and BC > 0 and CD < 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = 1
            else:
                direction = np.NAN

        elif XA < 0 and AB > 0 and BC < 0 and CD > 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = -1
            else:
                direction = np.NAN
        else:
            direction = np.NAN

        return direction


    def is_bat_pattern(self, lines):
        # print("Bat Pattern")
        XA = lines[0]
        AB = lines[1]
        BC = lines[2]
        CD = lines[3]

        AB_range = np.array([0.382 - self.error_allowed, 0.5 + self.error_allowed]) * abs(XA)
        BC_range = np.array([0.382 - self.error_allowed, 0.886 + self.error_allowed]) * abs(AB)
        CD_range = np.array([1.618 - self.error_allowed, 2.618 + self.error_allowed]) * abs(BC)

        direction = 0
        # Check for Pattern Validity
        if XA > 0 and AB < 0 and BC > 0 and CD < 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = 1
            else:
                direction = np.NAN

        elif XA < 0 and AB > 0 and BC < 0 and CD > 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = -1
            else:
                direction = np.NAN
        else:
            direction = np.NAN

        return direction


    def is_crab_pattern(self, lines):
        # print("Crab Pattern")
        XA = lines[0]
        AB = lines[1]
        BC = lines[2]
        CD = lines[3]

        AB_range = np.array([0.382 - self.error_allowed, 0.618 + self.error_allowed]) * abs(XA)
        BC_range = np.array([0.382 - self.error_allowed, 0.886 + self.error_allowed]) * abs(AB)
        CD_range = np.array([2.24 - self.error_allowed, 3.618 + self.error_allowed]) * abs(BC)

        direction = 0
        # Check for Pattern Validity
        if XA > 0 and AB < 0 and BC > 0 and CD < 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = 1
            else:
                direction = np.NAN

        elif XA < 0 and AB > 0 and BC < 0 and CD > 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = -1
            else:
                direction = np.NAN
        else:
            direction = np.NAN

        return direction


    """
    def is_shark_pattern(lines, error_allowed):
        XA = lines[0]
        AB = lines[1]
        BC = lines[2]
        CD = lines[3]

        AB_range = np.array([0.382 - error_allowed, 0.886 + error_allowed]) * abs(XA)
        BC_range = np.array([1.618 - error_allowed, 2.24 + error_allowed]) * abs(AB)
        CD_range = np.array([0.886 - error_allowed, 1.13 + error_allowed]) * abs(BC)

        direction = 0
        # Check for Pattern Validity
        if XA > 0 and AB < 0 and BC > 0 and CD < 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = 1
            else:
                direction = np.NAN

        elif XA < 0 and AB > 0 and BC < 0 and CD > 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = -1
            else:
                direction = np.NAN
        else:
            direction = np.NAN

        return direction
    """


    def is_cypher_pattern(self, lines):
        # print("Cypher Pattern")
        XA = lines[0]
        AB = lines[1]
        BC = lines[2]
        CD = lines[3]

        AB_range = np.array([0.382 - self.error_allowed, 0.618 + self.error_allowed]) * abs(XA)
        BC_range = np.array([1.272 - self.error_allowed, 1.414 + self.error_allowed]) * abs(AB)
        CD_range = np.array([1.618 - self.error_allowed, 2.618 + self.error_allowed]) * abs(BC)

        direction = 0
        # Check for Pattern Validity
        if XA > 0 and AB < 0 and BC > 0 and CD < 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = 1
            else:
                direction = np.NAN

        elif XA < 0 and AB > 0 and BC < 0 and CD > 0:
            if (
                AB_range[0] < abs(AB) < AB_range[1]
                and BC_range[0] < abs(BC) < BC_range[1]
                and CD_range[0] < abs(CD) < CD_range[1]
            ):
                direction = -1
            else:
                direction = np.NAN
        else:
            direction = np.NAN

        return direction


    # def walk_forward(price, sign, slippage=4, stop=10):
    #     slippage = float(slippage) / float(10000)
    #     stop_amount = float(stop) / float(10000)

    #     if sign == 1:
    #         initial_stop_loss = price[0] - stop_amount

    #         stop_loss = initial_stop_loss

    #         for i in range(1, len(price)):
    #             move = price[i] - price[i - 1]

    #             if move > 0 and (price[i] - stop_amount) > initial_stop_loss:
    #                 stop_loss = price[i] - stop_amount
    #             elif price[i] < stop_loss:
    #                 return stop_loss - price[0] - slippage

    #     elif sign == -1:
    #         initial_stop_loss = price[0] + stop_amount

    #         stop_loss = initial_stop_loss

    #         for i in range(1, len(price)):
    #             move = price[i] - price[i - 1]

    #             if move < 0 and (price[i] + stop_amount) < initial_stop_loss:
    #                 stop_loss = price[i] + stop_amount
    #             elif price[i] > stop_loss:
    #                 return price[0] - stop_loss - slippage


    # def walk_forward_on_Data(
    #     prices_df, sign, slippage_percent=0.02, stop_loss_percent=0.01
    # ):
    #     entry_price = prices_df["Close"].iloc[0]

    #     # Calculate slippage and stop-loss amount as percentages of the entry price
    #     slippage_amount = entry_price * slippage_percent
    #     stop_amount = entry_price * stop_loss_percent

    #     # Initialize the stop-loss based on the position's sign
    #     initial_stop_loss = (
    #         entry_price - stop_amount if sign == 1 else entry_price + stop_amount
    #     )
    #     stop_loss = initial_stop_loss

    #     for i in range(1, len(prices_df)):
    #         # Update stop-loss logic for long position
    #         if sign == 1:
    #             if prices_df["Close"].iloc[i] > stop_loss + stop_amount:
    #                 stop_loss = prices_df["Close"].iloc[i] - stop_amount

    #             if prices_df["Close"].iloc[i] < stop_loss:
    #                 exit_price = max(prices_df["Open"].iloc[i], stop_loss) - slippage_amount
    #                 pnl = exit_price - entry_price
    #                 return pnl

    #         # Update stop-loss logic for short position
    #         elif sign == -1:
    #             if prices_df["Close"].iloc[i] < stop_loss - stop_amount:
    #                 stop_loss = prices_df["Close"].iloc[i] + stop_amount

    #             if prices_df["Close"].iloc[i] > stop_loss:
    #                 exit_price = min(prices_df["Open"].iloc[i], stop_loss) + slippage_amount
    #                 pnl = entry_price - exit_price
    #                 return pnl

    #     return None  # Return None if the stop-loss is not hit