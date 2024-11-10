import requests
from bs4 import BeautifulSoup
import json
import warnings
import csv
from datetime import date, datetime, timedelta
import os
from PyQt5 import QtWidgets, QtCore

# Suppress the DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

def get_fund_info(symbol):
    url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={symbol}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return f"Error: Unable to fetch data for symbol {symbol}"
    
    soup = BeautifulSoup(response.content, 'html.parser')
    # Extract main-indicators div
    main_indicators_div = soup.find('div', class_='main-indicators')
    if not main_indicators_div:
        return "Error: Unable to find main-indicators div"

    # Extract price-indicators div
    price_indicators_div = soup.find('div', class_='price-indicators')
    if not price_indicators_div:
        return "Error: Unable to find price-indicators div"
    
    fund_info = {}
    
    # Extract fund name
    fund_name = soup.find('span', {'id': 'MainContent_FormViewMainIndicators_LabelFund'})
    if fund_name:
        fund_info['Fon İsmi'] = fund_name.text.strip()
    
    # Extract necessary items from main-indicators div
    main_indicators = soup.find('div', class_='main-indicators')
    if main_indicators:
        # Extract items from top-list
        top_list = main_indicators.find('ul', class_='top-list')
        if top_list:
            li_elements = top_list.find_all('li')
            for li in li_elements:
                label = li.contents[0].strip().rstrip('<br/>')
                value = li.find('span').text.strip()
                fund_info[label] = value
        
        # Extract items from the second ul
        second_ul = main_indicators.find_all('ul')[1]
        if second_ul:
            li_elements = second_ul.find_all('li')
            for li in li_elements:
                label = li.contents[0].strip().rstrip('<br/>')
                value = li.find('span').text.strip()
                fund_info[label] = value
    
    # Extract additional items from price-indicators
    price_indicators = soup.find('div', class_='price-indicators')
    if price_indicators:
        ul_element = price_indicators.find('ul')
        if ul_element:
            li_elements = ul_element.find_all('li')
            for li in li_elements:
                label = li.contents[0].strip().rstrip('<br />')
                span = li.find('span')
                if span:
                    value = span.text.strip()
                    fund_info[label] = value
    
    return fund_info

def get_all_fund_list():
    base_url = "https://www.takasbank.com.tr/tr/kaynaklar/tefas-yatirim-fonlari"
    fund_list = {}
    page = 1
    
    while True:
        url = f"{base_url}?page={page}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error: Unable to fetch data from page {page}")
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('tbody')
        
        if not table:
            print(f"Error: Unable to find the table in the HTML on page {page}")
            break
        
        rows = table.find_all('tr')
        if not rows:
            break
        
        for row in rows:
            columns = row.find_all('td')
            if len(columns) == 2:
                fund_name = columns[0].text.strip()
                fund_symbol = columns[1].text.strip()
                fund_list[fund_symbol] = fund_name
        
        pagination = soup.find('ul', class_='pagination')
        if not pagination or not pagination.find('a', class_='next'):
            break
        
        page += 1
    
    # Read additional funds from JSON file
    try:
        with open('extra_funds_for_fund_list.json', 'r', encoding='utf-8') as file:
            extra_funds = json.load(file)
            if isinstance(extra_funds, list):
                for fund in extra_funds:
                    if 'fund_name' in fund and 'fund_symbol' in fund:
                        fund_name = fund['fund_name']
                        fund_symbol = fund['fund_symbol']
                        if fund_name and fund_symbol:
                            fund_list[fund_symbol] = fund_name
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading extra funds: {e}")
    
    return fund_list

def get_todays_data():
    # Get all funds
    all_funds = get_all_fund_list()

    # Prepare data for CSV
    csv_data = []
    for symbol, name in all_funds.items():
        fund_data = get_fund_info(symbol)
        fund_data['Symbol'] = symbol
        fund_data['Name'] = name
        csv_data.append(fund_data)

    # Generate filename with today's date
    today = date.today().strftime("%Y-%m-%d")
    filename = f"fund_data_{today}.csv"

    # Write data to CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        if csv_data:
            fieldnames = csv_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in csv_data:
                writer.writerow(row)

    print(f"Data has been saved to {filename}")

def get_fund_historical_data(symbol, start_date, end_date):
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"
    
    historical_data = []
    
    while start_date < end_date:
        interval_end = min(start_date + timedelta(days=90), end_date)
        
        data = {
            "fontip": "YAT",
            "fonkod": symbol,
            "bastarih": start_date.strftime("%d.%m.%Y"),
            "bittarih": interval_end.strftime("%d.%m.%Y"),
            "fonturkod": "",
            "fonunvantip": ""
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code != 200:
            print(f"Error: Unable to fetch historical data for symbol {symbol}")
            return []
        
        json_data = response.json()
        
        if 'data' not in json_data:
            print(f"Error: Unexpected response format for symbol {symbol}")
            return []
        
        for item in json_data['data']:
            historical_data.append({
                'Date': datetime.fromtimestamp(int(item['TARIH']) / 1000).strftime('%Y-%m-%d'),
                'Symbol': item['FONKODU'],
                'Name': item['FONUNVAN'],
                'Price': item['FIYAT'],
                'Number_of_Shares': item['TEDPAYSAYISI'],
                'Number_of_Investors': item['KISISAYISI'],
                'Portfolio_Size': item['PORTFOYBUYUKLUK'],
                'Stock_Market_Price': item['BORSABULTENFIYAT']
            })
        
        start_date = interval_end + timedelta(days=1)
    
    return historical_data

def get_all_historical_data():
    all_funds = get_all_fund_list()
    total_funds = len(all_funds)
    
    if not os.path.exists('funds'):
        os.makedirs('funds')
    
    # Create a progress dialog
    progress_dialog = QtWidgets.QProgressDialog("Fetching historical data...", "Cancel", 0, total_funds)
    progress_dialog.setWindowTitle("Progress")
    progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
    progress_dialog.setMinimumDuration(0)
    
    for index, (symbol, name) in enumerate(all_funds.items(), 1):
        # Update progress dialog
        progress_dialog.setValue(index)
        progress_dialog.setLabelText(f"Processing fund {index}/{total_funds}: {symbol} - {name}")
        
        # Check if the user canceled the operation
        if progress_dialog.wasCanceled():
            break
        
        print(f"Processing fund {index}/{total_funds}: {symbol} - {name}")
        
        filename = f"funds/{symbol}.json"
        end_date = date.today()
        start_date = end_date - timedelta(days=5*365)  # 5 years ago
        
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            if existing_data:
                last_date = datetime.strptime(existing_data[0]['Date'], '%Y-%m-%d').date()
                start_date = last_date + timedelta(days=1)
                
                print(f"  Existing data found. Updating from {start_date} to {end_date}")
            else:
                print(f"  Existing file is empty. Fetching all available data.")
        else:
            print(f"  No existing data. Fetching all available data.")
        
        new_data = get_fund_historical_data(symbol, start_date, end_date)
        
        if new_data:
            if os.path.exists(filename):
                new_data.extend(existing_data)
            
            new_data.sort(key=lambda x: x['Date'], reverse=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=4)
            
            print(f"  Data saved to {filename}")
            print(f"  Number of records: {len(new_data)}")
            print(f"  Date range: {new_data[-1]['Date']} to {new_data[0]['Date']}")
        else:
            print(f"  No new data available for {symbol}")
        
        print()  # Empty line for readability
    
    progress_dialog.setValue(total_funds)  # Ensure the progress dialog is complete
    print("All historical data has been retrieved and saved.")

# Uncomment the line below to run the function
# get_all_historical_data()
