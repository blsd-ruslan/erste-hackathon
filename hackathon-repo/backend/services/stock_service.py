from time import time
from typing import Dict

from alpha_vantage.async_support.timeseries import TimeSeries
import pandas as pd
import asyncio

from utils.environment_variables import ALPHAVANTAGE_API_KEY

ts = TimeSeries(key=ALPHAVANTAGE_API_KEY, output_format='pandas')

def save_all_possible_stocks() -> None:
    url = f"https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={ALPHAVANTAGE_API_KEY}"

    try:
        active_symbols = pd.read_csv(url)
        active_symbols.to_csv('active_symbols.csv', index=False)
        print("Data successfully saved to 'active_symbols.csv'.")
    except Exception as e:
        print(f"An error occurred: {e}")

async def get_stock_growth_over_calendar_year(stock_symbol: str) -> float:
    ts = TimeSeries(key=ALPHAVANTAGE_API_KEY, output_format='pandas')

    data, _ = await ts.get_daily(symbol=stock_symbol, outputsize='full')

    await ts.close()

    data.sort_index(inplace=True)
    start_date = '2024-01-02'

    if start_date not in data.index:
        raise ValueError(f"No data available for {start_date} for symbol {stock_symbol}")

    start_price = data.loc[start_date]['4. close']
    end_price = data['4. close'].iloc[-1]

    percent_growth = ((end_price - start_price) / start_price) * 100
    return percent_growth

async def get_multiple_stock_growth(stock_symbols: list[str]) -> Dict[str, float]:
    tasks = [
        get_stock_growth_over_calendar_year(symbol)
        for symbol in stock_symbols
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    result_dict = {}

    for symbol, result in zip(stock_symbols, results):
        if isinstance(result, Exception):
            print(f"Error processing {symbol}: {result}")
        else:
            print(f"{symbol}: {result:.2f}% growth since 2024-01-02")
            result_dict[symbol] = result

    return result_dict


if __name__ == '__main__':
    start_time = time()

    asyncio.run(get_multiple_stock_growth(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']))

    print(f"Ececution time: {time() - start_time:.2f} seconds")