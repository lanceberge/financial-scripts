#!/usr/bin/env python3

import sys
import yfinance as yf
import pandas as pd
import argparse
from datetime import datetime, timedelta

from tickers import tickers


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Calculate correlation matrix of asset returns."
    )
    parser.add_argument("--tickers", help="Tickers to add")
    parser.add_argument(
        "--timerange", type=int, default=5, help="Number of years for historical data"
    )
    return parser.parse_args()


def get_correlation_matrix(tickers, years):
    try:
        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=years * 365)).strftime(
            "%Y-%m-%d"
        )

        data = yf.download(tickers, start=start_date, end=end_date)["Close"]

        if data.empty or data.shape[0] < 2:
            raise ValueError("Insufficient data for correlation calculation.")

        returns = data.pct_change().dropna()

        correlation = returns.corr()
        return correlation

    except Exception as e:
        print(f"Error fetching data or calculating correlation: {e}")
        sys.exit(1)


def highlight_top_and_bottom_correlations(correlation_matrix):
    """Format correlation matrix to exclude self-correlations, highlight < 0.2 in green and > 0.55 in red."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"

    for ticker in correlation_matrix.index:
        correlation_matrix.loc[ticker, ticker] = pd.NA

    print("\nCorrelation Matrix:")
    header = " " * 10 + "".join(f"{t:>10}" for t in correlation_matrix.columns)
    print(header)

    for row_ticker in correlation_matrix.index:
        line = f"{row_ticker:<10}"
        for col_ticker in correlation_matrix.columns:
            value = correlation_matrix.loc[row_ticker, col_ticker]
            if pd.isna(value):
                line += f"{'--':>10}"
            else:
                formatted_value = f"{value:>10.3f}"
                if value > 0.55:
                    line += f"{RED}{formatted_value}{RESET}"
                elif value < 0.2:
                    line += f"{GREEN}{formatted_value}{RESET}"
                else:
                    line += formatted_value
        print(line)


def main():
    args = parse_arguments()
    years = args.timerange
    ticker_list = args.tickers.split() if args.tickers else tickers

    if len(ticker_list) < 2:
        print("Please provide at least two ticker symbols.")
        sys.exit(1)

    if years <= 0:
        print("Timerange must be a positive number of years.")
        sys.exit(1)

    correlation_matrix = get_correlation_matrix(ticker_list, years)
    highlight_top_and_bottom_correlations(correlation_matrix)


if __name__ == "__main__":
    main()
