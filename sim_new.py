import json
from datetime import datetime, timedelta
import os
import numpy as np
from sklearn.linear_model import LinearRegression # type: ignore
from sklearn.model_selection import train_test_split # type: ignore
import tensorflow as tf # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Dense # type: ignore

# Load all fund data from JSON files
def load_all_funds_data():
    funds_data = {}
    funds_dir = 'funds'
    for filename in os.listdir(funds_dir):
        if filename.endswith('.json'):
            fund_symbol = filename[:-5]  # Remove .json extension
            print(f"Loading data for fund: {fund_symbol}")
            with open(os.path.join(funds_dir, filename), 'r') as f:
                fund_data = json.load(f)
                funds_data[fund_symbol] = {datetime.strptime(item['Date'], '%Y-%m-%d').date(): item for item in fund_data}
    return funds_data

# Prepare data for machine learning
def prepare_data(fund_data, window=20):
    dates = sorted(fund_data.keys())
    X, y = [], []
    for i in range(len(dates) - window):
        window_data = [float(fund_data[dates[j]]['Price']) for j in range(i, i + window)]
        X.append(window_data)
        y.append(float(fund_data[dates[i + window]]['Price']))
    print(f"Prepared data with {len(X)} samples for training")
    return np.array(X), np.array(y)

# Train a deep learning model
def train_model(X_train, y_train):
    print("Training deep learning model...")
    print(f"X_train shape: {X_train.shape}")
    print(f"y_train shape: {y_train.shape}")
    model = Sequential([
        Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        Dense(32, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    if len(X_train) == 0 or len(y_train) == 0:
        raise ValueError("Training data is empty. Check your data preparation steps.")
    model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=1)
    print("Model training completed")
    return model

# Function to get the price of a fund on a specific date
def get_fund_price(funds_data, fund_symbol, date):
    if fund_symbol in funds_data and date.date() in funds_data[fund_symbol]:
        return float(funds_data[fund_symbol][date.date()]['Price'])
    return None

# Simulate different strategies
def simulate_strategies(starting_money):
    print("Starting simulation...")
    funds_data = load_all_funds_data()
    start_date = datetime.now() - timedelta(days=5*365)  # Start date is 5 years ago
    train_end_date = start_date + timedelta(days=2*365)  # Training data ends 2 years after start
    end_date = datetime.now() - timedelta(days=7)  # End date is a week ago
    current_date = train_end_date
    portfolio = {'cash': starting_money, 'fund': None, 'shares': 0}

    for fund_symbol, fund_data in funds_data.items():
        print(f"Simulating strategy for fund: {fund_symbol}")
        X, y = prepare_data(fund_data)
        if len(X) == 0:
            print(f"No sufficient data for fund: {fund_symbol}, skipping...")
            continue

        # Split data into training and simulation sets
        train_indices = [i for i, date in enumerate(sorted(fund_data.keys())) if date <= train_end_date.date()]
        X_train, y_train = X[train_indices], y[train_indices]

        # Debugging output
        print(f"Training data size for fund {fund_symbol}: X_train: {len(X_train)}, y_train: {len(y_train)}")

        if len(X_train) == 0 or len(y_train) == 0:
            print(f"Training data is empty for fund: {fund_symbol}, skipping...")
            continue

        model = train_model(X_train, y_train)

        while current_date <= end_date:
            if current_date.date() in fund_data:
                # Use the last available window to predict the next price
                recent_prices = [float(fund_data[date]['Price']) for date in sorted(fund_data.keys())[-20:]]
                recent_prices = np.array(recent_prices)  # Convert to NumPy array
                predicted_price = model.predict(recent_prices[np.newaxis, :])[0][0]  # Add batch dimension
                current_price = get_fund_price(funds_data, fund_symbol, current_date)

                if current_price is not None:
                    # Example strategy: Buy if predicted price is higher than current price, sell if lower
                    if predicted_price > current_price and portfolio['cash'] > 0:
                        shares_to_buy = portfolio['cash'] // current_price
                        if shares_to_buy > 0:
                            portfolio['shares'] += shares_to_buy
                            portfolio['cash'] -= shares_to_buy * current_price
                            portfolio['fund'] = fund_symbol
                            print(f"Date: {current_date.date()}, Fund: {fund_symbol}, Action: Bought {shares_to_buy} shares at {current_price}, Predicted Price: {predicted_price}")
                    elif predicted_price < current_price and portfolio['shares'] > 0:
                        portfolio['cash'] += portfolio['shares'] * current_price
                        print(f"Date: {current_date.date()}, Fund: {fund_symbol}, Action: Sold {portfolio['shares']} shares at {current_price}, Predicted Price: {predicted_price}")
                        portfolio['shares'] = 0
                        portfolio['fund'] = None

            current_date += timedelta(days=1)

    # Sell all funds on the last day
    if portfolio['shares'] > 0 and portfolio['fund'] is not None:
        final_price = get_fund_price(funds_data, portfolio['fund'], end_date)
        if final_price is not None:
            portfolio['cash'] += portfolio['shares'] * final_price
            print(f"Date: {end_date.date()}, Fund: {portfolio['fund']}, Action: Sold {portfolio['shares']} shares at {final_price}")
            portfolio['shares'] = 0
            portfolio['fund'] = None

    final_value = portfolio['cash']
    total_gain_loss = final_value - starting_money
    total_percentage = (total_gain_loss / starting_money) * 100 if starting_money != 0 else 0
    print(f"\nFinal Results:")
    print(f"Starting Amount: ${starting_money:.2f}")
    print(f"Ending Amount: ${final_value:.2f}")
    print(f"Total Gain/Loss: ${total_gain_loss:.2f}")
    print(f"Total Percentage: {total_percentage:.2f}%")

# Example usage of the simulation function
simulate_strategies(10000)  # Start simulation with $10,000