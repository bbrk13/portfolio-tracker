# Fund Data Visualization

This project is a Python application designed to visualize and manage investment fund data. It provides functionalities to fetch, analyze, and display historical and current data of various funds.

## Features

- **Fetch Fund Data**: Retrieve current and historical data for investment funds.
- **Portfolio Management**: Manage and track your investment portfolio.
- **Data Visualization**: Visualize fund data using charts and graphs.
- **User Interface**: A GUI built with PyQt for easy interaction.

## Project Structure

- **`main.py`**: Contains the main logic for fetching and processing fund data.
- **`gui.py`**: Handles the graphical user interface for the application.
- **`extra_funds_for_fund_list.json`**: A JSON file containing additional fund data.
- **`portfolios/my_portfolio_1.json`**: A JSON file storing portfolio data.
- **`.gitignore`**: Specifies files and directories to be ignored by Git.
- **`portfolio_log.txt`**: A log file recording transactions made in the portfolio.

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies**:
   Ensure you have Python installed, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Execute the gui script to start the application:
   ```bash
   python gui.py
   ```

## Usage

- **Fetching Data**: Use the `get_all_historical_data()` function to fetch historical data for all funds.
- **Portfolio Management**: Add, remove, or update fund transactions in `my_portfolio_1.json`.
- **Visualization**: Use the GUI to visualize fund data and analyze performance.

## Notes

- The application uses `requests` and `BeautifulSoup` to scrape data from the web.
- Data is stored in JSON format for easy access and modification.
- The GUI is built using PyQt, providing a user-friendly interface for managing and visualizing fund data.


