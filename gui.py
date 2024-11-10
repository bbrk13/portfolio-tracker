from PyQt5 import QtWidgets, QtGui, QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import json
import os
from datetime import datetime, timedelta
from main import get_all_fund_list, get_all_historical_data

class NumericTableWidgetItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text):
        super().__init__(text)

    def __lt__(self, other):
        # Check if the column is numeric
        try:
            # Convert text to float for comparison
            return float(self.text().replace('₺', '').replace('%', '')) < float(other.text().replace('₺', '').replace('%', ''))
        except ValueError:
            # Fallback to string comparison if conversion fails
            return self.text() < other.text()

class FundDataVisualization(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fund Data Visualization")
        self.setGeometry(100, 100, 800, 600)

        # Create portfolios directory if it doesn't exist
        if not os.path.exists('./portfolios'):
            os.makedirs('./portfolios')

        # Load portfolio data
        self.portfolio_data = self.load_portfolio_data()

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Create and setup tabs
        self.setup_tabs()

        # Setup visualization tab
        self.setup_visualization_tab()

        # Setup portfolio tab
        self.setup_portfolio_tab()

        # Connect table click event to function
        self.my_funds_table.itemClicked.connect(self.on_fund_table_click)

        # Initialize sort order dictionary
        self.column_sort_order = {}

    def setup_tabs(self):
        self.tabs = QtWidgets.QTabWidget()
        self.portfolio_tab = QtWidgets.QWidget()
        self.visualization_tab = QtWidgets.QWidget()
        
        # Switch the order of adding tabs
        self.tabs.addTab(self.portfolio_tab, "My Portfolio")
        self.tabs.addTab(self.visualization_tab, "Visualization")
        
        self.main_layout.addWidget(self.tabs)

    def setup_visualization_tab(self):
        viz_layout = QtWidgets.QVBoxLayout(self.visualization_tab)
        
        # Chart Frame
        self.chart_frame = QtWidgets.QFrame()
        chart_layout = QtWidgets.QVBoxLayout(self.chart_frame)
        viz_layout.addWidget(self.chart_frame)

        # Add time filter buttons
        self.time_filter_layout = QtWidgets.QHBoxLayout()
        self.last_week_button = QtWidgets.QPushButton("Last Week")
        self.last_month_button = QtWidgets.QPushButton("Last Month")
        self.last_3_months_button = QtWidgets.QPushButton("Last 3 Months")
        self.last_6_months_button = QtWidgets.QPushButton("Last 6 Months")
        self.last_year_button = QtWidgets.QPushButton("Last Year")
        self.last_3_years_button = QtWidgets.QPushButton("Last 3 Years")
        self.since_new_year_button = QtWidgets.QPushButton("Since New Year")
        self.all_data_button = QtWidgets.QPushButton("All Data")

        self.time_filter_layout.addWidget(self.last_week_button)
        self.time_filter_layout.addWidget(self.last_month_button)
        self.time_filter_layout.addWidget(self.last_3_months_button)
        self.time_filter_layout.addWidget(self.last_6_months_button)
        self.time_filter_layout.addWidget(self.last_year_button)
        self.time_filter_layout.addWidget(self.last_3_years_button)
        self.time_filter_layout.addWidget(self.since_new_year_button)
        self.time_filter_layout.addWidget(self.all_data_button)

        viz_layout.addLayout(self.time_filter_layout)

        # Control Frame
        control_frame = QtWidgets.QFrame()
        control_layout = QtWidgets.QHBoxLayout(control_frame)

        # Fund Selection
        self.fund_label = QtWidgets.QLabel("Search Fund:")
        control_layout.addWidget(self.fund_label)

        # Get fund data
        self.fund_data = get_all_fund_list()
        if not self.fund_data:
            self.fund_data = {
                "GUH": "Sample Fund 1",
                "GGK": "Sample Fund 2", 
                "GHS": "Sample Fund 3",
                "GAK": "Sample Fund 4",
                "GKS": "Sample Fund 5",
                "GUV": "Sample Fund 6"
            }

        # Create searchable combobox
        self.fund_dropdown = QtWidgets.QComboBox()
        self.fund_dropdown.setEditable(True)
        self.fund_dropdown.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.fund_dropdown.completer().setFilterMode(QtCore.Qt.MatchContains)
        self.fund_dropdown.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        
        # Add items with both symbol and name
        for symbol, name in self.fund_data.items():
            self.fund_dropdown.addItem(f"{symbol} - {name}", symbol)

        control_layout.addWidget(self.fund_dropdown)

        # Fetch Data Button
        self.fetch_data_button = QtWidgets.QPushButton("Fetch Historical Data")
        self.fetch_data_button.clicked.connect(self.fetch_data_with_progress)
        control_layout.addWidget(self.fetch_data_button)

        # Update Chart Button
        self.update_button = QtWidgets.QPushButton("Update Chart")
        self.update_button.clicked.connect(self.update_chart)
        self.update_button.clicked.connect(self.all_data_button.click)
        control_layout.addWidget(self.update_button)

        viz_layout.addWidget(control_frame)

        # Add a new frame for transaction details and buttons
        self.transaction_frame = QtWidgets.QFrame()
        transaction_layout = QtWidgets.QVBoxLayout(self.transaction_frame)
        viz_layout.addWidget(self.transaction_frame)

        # Initial Chart Update
        self.update_chart()

        # Connect buttons to functions
        self.last_week_button.clicked.connect(lambda: self.update_chart_with_filter('week'))
        self.last_month_button.clicked.connect(lambda: self.update_chart_with_filter('month'))
        self.last_3_months_button.clicked.connect(lambda: self.update_chart_with_filter('3_months'))
        self.last_6_months_button.clicked.connect(lambda: self.update_chart_with_filter('6_months'))
        self.last_year_button.clicked.connect(lambda: self.update_chart_with_filter('year'))
        self.last_3_years_button.clicked.connect(lambda: self.update_chart_with_filter('3_years'))
        self.since_new_year_button.clicked.connect(lambda: self.update_chart_with_filter('since_new_year'))
        self.all_data_button.clicked.connect(lambda: self.update_chart_with_filter('all'))

    def load_portfolio_data(self):
        portfolio_file = './portfolios/my_portfolio_1.json'
        try:
            with open(portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create an empty portfolio file with the correct structure
            with open(portfolio_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return []

    def setup_portfolio_tab(self):
        layout = QtWidgets.QVBoxLayout(self.portfolio_tab)

        self.my_funds_table = QtWidgets.QTableWidget()
        self.my_funds_table.setColumnCount(9)
        self.my_funds_table.setHorizontalHeaderLabels([
            "Symbol", "Full Name", "Quantity", "Total Value", "Total Cost", 
            "Change (%)", "Change (₺)", "C%/AHD", "AHD"
        ])
        
        # Set the size policy to expanding
        self.my_funds_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        # Set the horizontal header to stretch
        header = self.my_funds_table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # Add the table to the layout with a stretch factor
        layout.addWidget(self.my_funds_table, stretch=1)

        # Enable sorting
        self.my_funds_table.setSortingEnabled(True)
        self.my_funds_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

        # Create a horizontal layout for the summary labels
        summary_layout = QtWidgets.QHBoxLayout()

        # QLabel for displaying total cost
        self.total_cost_label = QtWidgets.QLabel("Total Cost: N/A")
        summary_layout.addWidget(self.total_cost_label)

        # QLabel for displaying average holding days
        self.avg_holding_days_label = QtWidgets.QLabel("Average Holding Days: N/A")
        summary_layout.addWidget(self.avg_holding_days_label)

        # QLabel for displaying total change
        self.total_change_label = QtWidgets.QLabel("Total Change: N/A")
        summary_layout.addWidget(self.total_change_label)

        # QLabel for displaying total change percentage
        self.total_change_percentage_label = QtWidgets.QLabel("Total Change (%): N/A")
        summary_layout.addWidget(self.total_change_percentage_label)

        # QLabel for displaying total change percentage per average holding day
        self.total_change_per_ahd_label = QtWidgets.QLabel("Total Change (%)/AHD: N/A")
        summary_layout.addWidget(self.total_change_per_ahd_label)

        # Add the summary layout to the main layout
        layout.addLayout(summary_layout)

        # Update My Funds table
        self.update_my_funds_table()

        # Portfolio list
        self.portfolio_list = QtWidgets.QListWidget()
        layout.addWidget(self.portfolio_list)

        # Load existing portfolio data into the list
        for entry in self.portfolio_data:
            action_str = f"{entry['type'].capitalize()} {entry['quantity']} of {entry['symbol']} on {entry['date']}"
            self.portfolio_list.addItem(action_str)

        # Buy and Sell buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.buy_button = QtWidgets.QPushButton("Buy Fund")
        self.sell_button = QtWidgets.QPushButton("Sell Fund")
        self.update_funds_button = QtWidgets.QPushButton("Update My Funds")
        button_layout.addWidget(self.buy_button)
        button_layout.addWidget(self.sell_button)
        button_layout.addWidget(self.update_funds_button)
        layout.addLayout(button_layout)

        # Connect buttons to functions
        self.buy_button.clicked.connect(self.show_buy_dialog)
        self.sell_button.clicked.connect(self.show_sell_dialog)
        self.update_funds_button.clicked.connect(self.update_my_funds_table)

    def adjust_column_widths(self):
        total_width = self.my_funds_table.viewport().width()
        column_count = self.my_funds_table.columnCount()
        column_width = total_width // column_count

        for col in range(column_count):
            self.my_funds_table.setColumnWidth(col, column_width)

    def update_my_funds_table(self):
        # Reload portfolio data
        self.portfolio_data = self.load_portfolio_data()

        self.my_funds_table.setRowCount(0)  # Clear the table
        fund_status = {}
        total_cost_all_funds = 0.0
        total_change_money = 0.0
        total_initial_value = 0.0
        change_percentages = []  # List to store change percentages
        total_weighted_days = 0
        total_quantity = 0

        for entry in self.portfolio_data:
            try:
                action = entry['type']
                quantity = entry['quantity']
                symbol = entry['symbol']

                if action == "buy":
                    if symbol in fund_status:
                        fund_status[symbol] += quantity
                    else:
                        fund_status[symbol] = quantity
                elif action == "sell":
                    if symbol in fund_status:
                        fund_status[symbol] -= quantity
                        if fund_status[symbol] <= 0:
                            del fund_status[symbol]
            except KeyError as e:
                print(f"Error processing entry '{entry}': {e}")
                continue

        for symbol, quantity in fund_status.items():
            full_name = self.fund_data.get(symbol, "Unknown Fund")
            change_percentage, change_money, avg_holding_days, total_cost = self.calculate_current_change(symbol, quantity)
            
            # Calculate the total value
            latest_price = self.get_latest_price(symbol)
            total_value = latest_price * quantity

            # Accumulate total cost and total change in money
            total_cost_all_funds += total_cost
            total_change_money += change_money

            # Accumulate initial total value
            total_initial_value += total_cost

            # Store change percentage for color calculation
            change_percentages.append(change_percentage)

            # Accumulate weighted days and quantity for average holding days calculation
            total_weighted_days += avg_holding_days * quantity
            total_quantity += quantity

            row_position = self.my_funds_table.rowCount()
            self.my_funds_table.insertRow(row_position)
            self.my_funds_table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(symbol))
            self.my_funds_table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(full_name))
            self.my_funds_table.setItem(row_position, 2, NumericTableWidgetItem(str(quantity)))  # Quantity
            self.my_funds_table.setItem(row_position, 3, NumericTableWidgetItem(f"₺{total_value:.2f}"))  # Total Value
            self.my_funds_table.setItem(row_position, 4, NumericTableWidgetItem(f"₺{total_cost:.2f}"))  # Total Cost
            self.my_funds_table.setItem(row_position, 5, NumericTableWidgetItem(f"{change_percentage:.2f}%"))  # Change (%)
            self.my_funds_table.setItem(row_position, 6, NumericTableWidgetItem(f"₺{change_money:.2f}"))  # Change (₺)
            self.my_funds_table.setItem(row_position, 7, NumericTableWidgetItem(f"{change_percentage / avg_holding_days:.2f}"))  # C%/AHD
            self.my_funds_table.setItem(row_position, 8, NumericTableWidgetItem(f"{avg_holding_days:.1f}"))  # AHD

        # Calculate min and max change percentages for color scaling
        min_change = min(change_percentages) if change_percentages else 0
        max_change = max(change_percentages) if change_percentages else 0

        # Apply color to rows based on change percentage
        for row in range(self.my_funds_table.rowCount()):
            change_item = self.my_funds_table.item(row, 5)
            change_value = float(change_item.text().strip('%'))
            color = self.calculate_color(change_value, min_change, max_change)
            for col in range(self.my_funds_table.columnCount()):
                self.my_funds_table.item(row, col).setBackground(color)

        # Update the QLabel with the total cost
        self.total_cost_label.setText(f"Total Cost: ₺{total_cost_all_funds:.2f}")

        # Update the QLabel with the total change
        self.total_change_label.setText(f"Total Change: ₺{total_change_money:.2f}")
        self.total_change_label.setStyleSheet("color: green;" if total_change_money > 0 else "color: red;")

        # Update the QLabel with the total change percentage
        total_change_percentage = (total_change_money / total_initial_value * 100) if total_initial_value > 0 else 0
        self.total_change_percentage_label.setText(f"Total Change (%): {total_change_percentage:.2f}%")
        self.total_change_percentage_label.setStyleSheet("color: green;" if total_change_percentage > 0 else "color: red;")

        # Calculate and update average holding days
        average_holding_days = total_weighted_days / total_quantity if total_quantity > 0 else 0
        self.avg_holding_days_label.setText(f"Average Holding Days: {average_holding_days:.1f}")

        # Calculate and update total change percentage per average holding day
        total_change_per_ahd = total_change_percentage / average_holding_days if average_holding_days > 0 else 0
        self.total_change_per_ahd_label.setText(f"Total Change (%)/AHD: {total_change_per_ahd:.2f}")

    def get_latest_price(self, symbol):
        try:
            with open(f'funds/{symbol}.json', 'r', encoding='utf-8') as f:
                historical_data = json.load(f)
            if not historical_data:
                return 0.0
            # Sort data by date to find the latest price
            historical_data.sort(key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d'))
            return float(historical_data[-1]['Price'])
        except (FileNotFoundError, json.JSONDecodeError):
            return 0.0

    def calculate_current_change(self, symbol, quantity):
        # Load historical data for the symbol
        try:
            with open(f'funds/{symbol}.json', 'r', encoding='utf-8') as f:
                historical_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0.0, 0.0, 0, 0.0  # Return 0 for average holding days and total cost

        if not historical_data:
            return 0.0, 0.0, 0, 0.0

        # Sort data by date to find the latest price
        historical_data.sort(key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d'))
        latest_price = float(historical_data[-1]['Price'])

        # Calculate the weighted average holding period and total cost
        total_weighted_days = 0
        total_quantity = 0
        total_cost = 0.0
        total_buying_price = 0.0

        for entry in self.portfolio_data:
            if entry['symbol'] == symbol and entry['type'] == 'buy':
                buying_date = datetime.strptime(entry['date'], '%Y-%m-%d')
                days_held = (datetime.now() - buying_date).days
                total_weighted_days += entry['quantity'] * days_held
                total_quantity += entry['quantity']

                # Find the buying price for cost calculation
                for data in historical_data:
                    if datetime.strptime(data['Date'], '%Y-%m-%d') >= buying_date:
                        buying_price = float(data['Price'])
                        total_cost += entry['quantity'] * buying_price
                        total_buying_price += entry['quantity'] * buying_price
                        break

        average_holding_days = total_weighted_days / total_quantity if total_quantity > 0 else 0
        average_buying_price = total_buying_price / total_quantity if total_quantity > 0 else 0

        if total_quantity == 0:
            return 0.0, 0.0, average_holding_days, total_cost

        # Calculate changes
        change_percentage = ((latest_price - average_buying_price) / average_buying_price) * 100
        change_money = (latest_price - average_buying_price) * quantity

        return change_percentage, change_money, average_holding_days, total_cost

    def update_chart(self, historical_data=None):
        # Ensure selected_fund is defined
        selected_fund = self.fund_dropdown.currentData()
        if not selected_fund:
            selected_fund = self.fund_dropdown.currentText().split(' - ')[0]

        if historical_data is None:
            try:
                with open(f'funds/{selected_fund}.json', 'r', encoding='utf-8') as f:
                    historical_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading data for {selected_fund}: {e}")
                return

        if not historical_data:
            print(f"No data available for the selected fund")
            return

        # Sort data by date to ensure correct order
        historical_data.sort(key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d'))

        dates = [datetime.strptime(item['Date'], '%Y-%m-%d') for item in historical_data]
        prices = [float(item['Price']) for item in historical_data]

        # Calculate percentage change
        if len(prices) > 1:
            initial_price = prices[0]
            final_price = prices[-1]
            if initial_price != 0:
                percentage_change = ((final_price - initial_price) / initial_price) * 100
            else:
                percentage_change = 0.0
        else:
            percentage_change = 0.0

        # Extract buy and sell dates
        buy_dates = [datetime.strptime(entry['date'], '%Y-%m-%d') for entry in self.portfolio_data if entry['symbol'] == selected_fund and entry['type'] == 'buy']
        sell_dates = [datetime.strptime(entry['date'], '%Y-%m-%d') for entry in self.portfolio_data if entry['symbol'] == selected_fund and entry['type'] == 'sell']

        # Filter buy and sell dates to only include those present in the historical data
        buy_dates = [date for date in buy_dates if date in dates]
        sell_dates = [date for date in sell_dates if date in dates]

        plt.clf()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, prices, label=f'Price (Change: {percentage_change:.2f}%)', linewidth=2)

        # Plot buy and sell markers
        ax.scatter(buy_dates, [prices[dates.index(date)] for date in buy_dates], color='green', marker='^', label='Buy')
        ax.scatter(sell_dates, [prices[dates.index(date)] for date in sell_dates], color='red', marker='v', label='Sell')

        ax.set_title(f"Price History", fontsize=12, pad=10)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Price", fontsize=10)
        ax.legend(fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()

        for i in reversed(range(self.chart_frame.layout().count())):
            widget = self.chart_frame.layout().itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        canvas = FigureCanvas(fig)
        self.chart_frame.layout().addWidget(canvas)

        # Ensure selected_fund is defined before calling update_transaction_details
        if historical_data:
            self.update_transaction_details(selected_fund)

    def fetch_data_with_progress(self):
        # Implement the method to fetch historical data
        get_all_historical_data()
        # Optionally, you can add a progress bar or a message to indicate data fetching

    def show_buy_dialog(self):
        self.show_fund_dialog("Buy Fund")

    def show_sell_dialog(self):
        self.show_fund_dialog("Sell Fund")

    def show_fund_dialog(self, action, pre_selected_symbol=None):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(action)
        dialog_layout = QtWidgets.QVBoxLayout(dialog)

        # Searchable combobox
        fund_combobox = QtWidgets.QComboBox(dialog)
        fund_combobox.setEditable(True)
        fund_combobox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        fund_combobox.completer().setFilterMode(QtCore.Qt.MatchContains)
        fund_combobox.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        for symbol, name in self.fund_data.items():
            fund_combobox.addItem(f"{symbol} - {name}", symbol)
        dialog_layout.addWidget(fund_combobox)

        # Pre-select the fund if provided
        if pre_selected_symbol:
            index = fund_combobox.findData(pre_selected_symbol)
            if index != -1:
                fund_combobox.setCurrentIndex(index)

        # Date picker
        date_picker = QtWidgets.QDateEdit(dialog)
        date_picker.setCalendarPopup(True)
        date_picker.setDate(QtCore.QDate.currentDate())
        dialog_layout.addWidget(date_picker)

        # Quantity input
        quantity_input = QtWidgets.QSpinBox(dialog)
        quantity_input.setRange(1, 1000000)
        dialog_layout.addWidget(quantity_input)

        # Save button
        save_button = QtWidgets.QPushButton("Save", dialog)
        save_button.clicked.connect(lambda: self.save_fund_action(action, fund_combobox, date_picker, quantity_input))
        dialog_layout.addWidget(save_button)

        # Close button
        close_button = QtWidgets.QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.close)
        dialog_layout.addWidget(close_button)

        dialog.exec_()

    def save_fund_action(self, action, fund_combobox, date_picker, quantity_input):
        selected_fund = fund_combobox.currentData()
        date = date_picker.date().toString("yyyy-MM-dd")
        quantity = quantity_input.value()

        # Check if selling more than available
        if action == "Sell Fund":
            fund_status = {}
            for entry in self.portfolio_data:
                act = entry['type']
                qty = entry['quantity']
                sym = entry['symbol']

                if act == "buy":
                    if sym in fund_status:
                        fund_status[sym] += qty
                    else:
                        fund_status[sym] = qty
                elif act == "sell":
                    if sym in fund_status:
                        fund_status[sym] -= qty
                        if fund_status[sym] <= 0:
                            del fund_status[sym]

            if selected_fund not in fund_status or fund_status[selected_fund] < quantity:
                QtWidgets.QMessageBox.warning(self, "Error", "Not enough funds to sell.")
                return

        # Create a new action
        new_action = {
            "portfolio_id": 1,  # Assuming this is for my_portfolio_1.json
            "id": len(self.portfolio_data) + 1,
            "symbol": selected_fund,
            "date": date,
            "type": "buy" if action == "Buy Fund" else "sell",
            "quantity": quantity
        }

        # Update portfolio data
        self.portfolio_data.append(new_action)

        # Save portfolio data to JSON file
        with open('./portfolios/my_portfolio_1.json', 'w', encoding='utf-8') as f:
            json.dump(self.portfolio_data, f, ensure_ascii=False, indent=4)

        # Update portfolio list
        self.portfolio_list.addItem(f"{action} {quantity} of {selected_fund} on {date}")

        # Log the action
        with open("portfolio_log.txt", "a") as log_file:
            log_file.write(f"{action} {quantity} of {selected_fund} on {date}\n")

        # Update My Funds table
        self.update_my_funds_table()  # Recalculate and update the table

        print(new_action)

    def on_fund_table_click(self, item):
        # Get the row of the clicked item
        row = item.row()
        # Get the symbol from the first column of the clicked row
        symbol_item = self.my_funds_table.item(row, 0)
        if symbol_item:
            symbol = symbol_item.text()
            # Switch to the Visualization tab
            self.tabs.setCurrentWidget(self.visualization_tab)
            # Find the index of the symbol in the dropdown
            index = self.fund_dropdown.findData(symbol)
            if index != -1:
                # Set the dropdown to the selected fund
                self.fund_dropdown.setCurrentIndex(index)
                # Click the "Update Chart" button
                self.update_button.click()

    def update_transaction_details(self, symbol):
        # Clear previous content
        for i in reversed(range(self.transaction_frame.layout().count())):
            widget = self.transaction_frame.layout().itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Filter portfolio data for the selected symbol
        transactions = [entry for entry in self.portfolio_data if entry['symbol'] == symbol]

        # Display transaction details
        transaction_list = QtWidgets.QListWidget()
        for entry in transactions:
            action_str = f"{entry['type'].capitalize()} {entry['quantity']} on {entry['date']}"
            transaction_list.addItem(action_str)
        self.transaction_frame.layout().addWidget(transaction_list)


    def calculate_color(self, change_value, min_change, max_change):
        # Normalize the change value to a 0-1 range
        if max_change == min_change:
            normalized_value = 0.5  # Neutral color if all changes are the same
        else:
            normalized_value = (change_value - min_change) / (max_change - min_change)

        # Calculate color based on normalized value
        if change_value > 0:
            # Green color gradient
            red = int(255 * (1 - normalized_value))
            green = 255
            blue = int(255 * (1 - normalized_value))
        else:
            # Red color gradient
            red = 255
            green = int(255 * (1 - normalized_value))
            blue = int(255 * (1 - normalized_value))

        return QtGui.QColor(red, green, blue)

    def update_chart_with_filter(self, period):
        selected_fund = self.fund_dropdown.currentData()
        if not selected_fund:
            selected_fund = self.fund_dropdown.currentText().split(' - ')[0]

        try:
            with open(f'funds/{selected_fund}.json', 'r', encoding='utf-8') as f:
                historical_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data for {selected_fund}: {e}")
            return

        if not historical_data:
            print(f"No data available for {selected_fund}")
            return

        # Determine the date range
        end_date = datetime.now()
        if period == 'week':
            start_date = end_date - timedelta(weeks=1)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == '3_months':
            start_date = end_date - timedelta(days=90)
        elif period == '6_months':
            start_date = end_date - timedelta(days=180)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        elif period == '3_years':
            start_date = end_date - timedelta(days=3*365)
        elif period == 'since_new_year':
            start_date = datetime(end_date.year, 1, 1)
        else:
            start_date = None

        # Filter data based on the date range
        if start_date:
            historical_data = [item for item in historical_data if datetime.strptime(item['Date'], '%Y-%m-%d') >= start_date]

        # If no data is available for the specified range, show all available data
        if not historical_data:
            print(f"Not enough data for the selected period, showing all available data.")
            historical_data = json.load(open(f'funds/{selected_fund}.json', 'r', encoding='utf-8'))

        # Update the chart with the filtered data
        self.update_chart(historical_data)

    def on_header_clicked(self, logicalIndex):
        # Determine the current sort order for the column
        current_order = self.column_sort_order.get(logicalIndex, QtCore.Qt.AscendingOrder)
        
        # Toggle the sort order
        new_order = QtCore.Qt.DescendingOrder if current_order == QtCore.Qt.AscendingOrder else QtCore.Qt.AscendingOrder
        
        # Sort the items in the table
        self.my_funds_table.sortItems(logicalIndex, new_order)
        
        # Update the sort order for the column
        self.column_sort_order[logicalIndex] = new_order

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = FundDataVisualization()
    window.show()
    app.exec_()