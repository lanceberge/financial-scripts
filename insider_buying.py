#!/usr/bin/env python3

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import argparse
from tickers import tickers

pd.set_option("display.max_colwidth", None)

excluded_tickers = ["SPY", "GLD", "QQQ", "IWM", "FXI"]


def get_insider_buying(tickers, days_back):
    """
    Retrieve insider buying data for a list of tickers.
    """
    insider_buys = {}

    date_threshold = datetime.now() - timedelta(days=days_back)

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            transactions = stock.insider_transactions

            if transactions.empty:
                continue

            transactions["Start Date"] = pd.to_datetime(
                transactions["Start Date"], format="%Y-%m-%d", errors="coerce"
            )

            buy_transactions = transactions[
                (transactions["Text"].str.contains("Purchase", case=False, na=False))
                & (transactions["Start Date"] >= date_threshold)
            ].sort_values(by="Start Date", ascending=False)

            if not buy_transactions.empty:
                filtered_buys = buy_transactions[
                    ["Start Date", "Insider", "Position"]
                ].copy()

                filtered_buys["Avg. Price"] = (
                    (buy_transactions["Value"] / buy_transactions["Shares"])
                    .round(2)
                    .apply(lambda x: f"{x:.2f}")
                )

                insider_buys[ticker] = filtered_buys

        except Exception as e:
            continue

    return insider_buys


def display_insider_buys(insider_buys):
    GREEN_BOLD = "\033[1;92m"
    RESET = "\033[0m"
    print("Insider Buying:")
    for ticker, buys in insider_buys.items():
        print(f"\n{GREEN_BOLD}{ticker}{RESET}")
        if buys.empty:
            print("No insider buy transactions found in the specified time frame.")
        else:
            print(buys.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(
        description="Fetch insider buying data for a list of stock tickers."
    )
    parser.add_argument(
        "--tickers",
        type=str,
        help="Comma-separated list of stock tickers (e.g., AAPL,MSFT,TSLA)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days to look back for insider buying transactions (default: 90)",
    )

    args = parser.parse_args()

    ticker_list = args.tickers.split() if args.tickers else tickers
    ticker_list = [t for t in ticker_list if t not in excluded_tickers]
    days_back = args.days

    if not ticker_list:
        print("At least one ticker must be provided.")
        sys.exit(1)
    if days_back <= 0:
        print("Days must be a positive number.")
        sys.exit(1)

    insider_buys = get_insider_buying(ticker_list, days_back)
    display_insider_buys(insider_buys)


if __name__ == "__main__":
    main()
