'''
Delta Neutral Options Trading Strategy

What is delta? It's a greek letter but in options and finance it is 
The change in price of an option contract due to the change in the underlying price

Delta is a percentage measure and represents some movement of the underlying security. Remember,
options are based off of other financial instruments (stocks, futures, etc.)
Source: https://www.cmegroup.com/education/courses/option-greeks/options-delta-the-greeks.html

TO DO: Caluclate the delta value for DJT (Trump Media: Stock) in any way you see fit. Be sure 
to make it clear what time horizon your delta is based off of.

The formula of delta = Change in the Price of Asset / Change in the Price of Underlying.
'''
##--------------------------------------------------------------------
#DELTA FOR DJT
#note: didnt need to calculate delta of option because of existing information in yfinance
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def fetch_option_data(ticker, expiration_date):
    stock = yf.Ticker(ticker)
    options = stock.option_chain(expiration_date)
    calls = options.calls
    puts = options.puts
    return calls, puts

def calculate_delta(options_data):
    return options_data[['strike', 'delta']]

#plot changes in delta of option
def plot_delta(calls_delta, puts_delta, expiration_date):
    plt.figure(figsize=(12, 6))
    plt.plot(calls_delta['strike'], calls_delta['delta'], label='Calls Delta')
    plt.plot(puts_delta['strike'], puts_delta['delta'], label='Puts Delta')
    plt.title(f'Option Delta vs Strike Price for DJT (Expiration: {expiration_date})')
    plt.xlabel('Strike Price')
    plt.ylabel('Delta')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    ticker = "DJT"
    
    # Fetch available expiration dates
    stock = yf.Ticker(ticker)
    expirations = stock.options
    
    print("Available expiration dates:")
    for i, date in enumerate(expirations):
        print(f"{i + 1}. {date}")
    
    # Let user choose expiration date
    choice = int(input("Enter the number of the expiration date you want to analyze: ")) - 1
    expiration_date = expirations[choice]
    
    calls, puts = fetch_option_data(ticker, expiration_date)
    
    calls_delta = calculate_delta(calls)
    puts_delta = calculate_delta(puts)
    
    plot_delta(calls_delta, puts_delta, expiration_date)

if __name__ == "__main__":
    main()
##-----------------------------------------------------------
