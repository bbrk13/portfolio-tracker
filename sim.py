# Import necessary modules
import json
from datetime import date, datetime, timedelta
import os
import numpy as np

# Define the main simulation function
def simulate_best_fund(starting_money):
    # Load all fund data from JSON files
    funds_data = load_all_funds_data()
    # After line 10
    print(f"Number of funds loaded: {len(funds_data)}")
    
    # Set simulation parameters
    start_date = datetime.now() - timedelta(days=5*365)  # Start date is 5 years ago
    end_date = datetime.now() - timedelta(days=7)  # End date is a week ago
    current_date = start_date  # Start simulation from the beginning
    portfolio = {'cash': starting_money, 'fund': None, 'shares': 0}  # Initialize portfolio

    # Main simulation loop
    # Replace lines 21-24 with:
    for fund_symbol, fund_data in funds_data.items():
        rsi = calculate_rsi(fund_data, current_date)
        print(f"{fund_symbol} RSI calculation result: {rsi}")
        if rsi is not None:
            print(f"{fund_symbol} RSI: {rsi:.2f}")
        else:
            print(f"Unable to calculate RSI for {fund_symbol} on {current_date}")
            if rsi is not None:
                print(f"{fund_symbol} RSI: {rsi:.2f}")
        
        if portfolio['fund']:
            price = get_fund_price(funds_data, portfolio['fund'], current_date)
            if price is not None:
                print(f"{portfolio['fund']}: ${price:.2f}")
        
        current_date += timedelta(days=1)  # Move to the next day

    # Calculate and print final performance (which will be unchanged)
    final_value = portfolio['cash']
    total_gain_loss = final_value - starting_money
    total_percentage = (total_gain_loss / starting_money) * 100
    print(f"\nFinal Results:")
    print(f"Starting Amount: ${starting_money:.2f}")
    print(f"Ending Amount: ${final_value:.2f}")
    print(f"Total Gain/Loss: ${total_gain_loss:.2f}")
    print(f"Total Percentage: {total_percentage:.2f}%")

# Function to load all fund data from JSON files
def load_all_funds_data():
    funds_data = {}
    funds_dir = 'funds'
    for filename in os.listdir(funds_dir):
        if filename.endswith('.json'):
            fund_symbol = filename[:-5]  # Remove .json extension
            with open(os.path.join(funds_dir, filename), 'r') as f:
                fund_data = json.load(f)
                funds_data[fund_symbol] = {datetime.strptime(item['Date'], '%Y-%m-%d').date(): item for item in fund_data}
    return funds_data

# Function to get the price of a fund on a specific date
def get_fund_price(funds_data, fund_symbol, date):
    print(f"Calculating RSI for date: {current_date}, data points: {len(fund_data)}")
    if fund_symbol in funds_data and date.date() in funds_data[fund_symbol]:
        return float(funds_data[fund_symbol][date.date()]['Price'])
    return None

# Function to calculate RSI
def calculate_rsi(fund_data, current_date, period=14):
    prices = []
    date = current_date.date()
    while len(prices) < period + 1 and date in fund_data:
        prices.append(float(fund_data[date]['Price']))
        date -= timedelta(days=1)
    
    if len(prices) < period + 1:
        return None
    
    prices.reverse()
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down if down != 0 else 0
    rsi = 100 - (100/(1+rs))
    return rsi

# Example usage of the simulation function
simulate_best_fund(10000)  # Start simulation with $10,000
