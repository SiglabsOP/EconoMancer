import sys
import os
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QLabel, QComboBox, QRadioButton, QHBoxLayout, QTabWidget
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton
import subprocess

plt.rcParams['figure.dpi'] = 100  # Adjust DPI for better clarity

# Function to scrape the economic calendar
# Function to assign importance based on event title
def assign_importance(title):
    if "Speaks" in title or "Federal Reserve" in title:
        return "High"
    elif "PMI" in title or "Index" in title:
        return "Medium"
    else:
        return "Low"
        

# Function to fetch historical market data
def fetch_historical_data(symbol, start_date, end_date):
    print(f"Fetching data for {symbol} from {start_date} to {end_date}")  # Log the symbol and dates
    data = yf.download(symbol, start=start_date, end=end_date)
    
    # Check if data is fetched correctly
    if data.empty:
        print(f"No data fetched for {symbol}")
    else:
        print(f"Data fetched for {symbol}: {data.head()}")  # Log the first few rows of data

    return data


# Function to backtest market reaction to an event
def backtest_market_reaction(event_time, event_name, symbol, before_days=3, after_days=3):
    today = datetime.now()
    event_date = today.strftime("%Y-%m-%d")
    event_datetime = datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M")

    start_date = (event_datetime - timedelta(days=before_days)).strftime("%Y-%m-%d")
    end_date = (event_datetime + timedelta(days=after_days)).strftime("%Y-%m-%d")

    # Fetch market data for the corresponding symbol
    market_data = fetch_historical_data(symbol, start_date, end_date)

    if market_data.empty:
        print(f"No market data available for {symbol} during {start_date} to {end_date}")
        return None

    closest_data_point = (
        market_data.index[0]
        if event_datetime < market_data.index[0]
        else market_data.index[-1]
        if event_datetime > market_data.index[-1]
        else event_datetime
    )

    # Proceed with plotting
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

    ax.plot(market_data.index, market_data['Close'], label='Market Price', linewidth=2)

    ax.axvline(x=closest_data_point, color='r', linestyle='--', label=f'{event_name} Time', linewidth=1.5)
    ax.axvspan(closest_data_point - timedelta(hours=1), closest_data_point + timedelta(hours=1), color='red', alpha=0.3, label='Event Impact Window')

    ax.set_title(f'Market Reaction to {event_name}', fontsize=18)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_ylabel('Price', fontsize=14)
    ax.legend(fontsize=12)

    return fig


        
        

# Function to scrape the economic calendar
# Function to scrape the economic calendar
def scrape_economic_calendar(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    events = []

    for event_row in soup.select('tr.js-event-item'):
        try:
            time_cell = event_row.select_one('td.time')
            time = time_cell.get_text(strip=True) if time_cell else "N/A"

            title_cell = event_row.select_one('td.event')
            title = title_cell.get_text(strip=True) if title_cell else "N/A"

            # Dynamically assign market symbol
            symbol = assign_symbol_based_on_keywords(title)  # Assign dynamically
            importance = assign_importance(title)  # Assign importance dynamically

            events.append((time, title, importance, symbol))
        except AttributeError:
            continue

    return pd.DataFrame(events, columns=['Time', 'Event', 'Importance', 'Symbol'])



# Event-to-Market Symbol Mapping
EVENT_SYMBOLS = {
 

}


# Function to download HTML content from Investing.com
def download_html():
    url = "https://www.investing.com/economic-calendar/"
    response = requests.get(url)
    if response.status_code == 200:
        with open('investing_data.html', 'wb') as f:
            f.write(response.content)
        print("HTML content downloaded successfully.")
    else:
        print("Failed to download data.")


# Function to run the databank parser (assuming you have this script)
def run_parser():
    subprocess.run(['python', 'dpg.py'], check=True)


# Function to parse the results from results.txt
def parse_results_file():
    with open('resultsgen.txt', 'r') as file:
        events = file.readlines()
    return events


# Function to dynamically assign a market symbol based on event keywords
# Function to generate keyword-to-symbol mapping from known economic events
def assign_symbol_based_on_keywords(event_title):
    keyword_mapping = {
    # ECB-related events
    "Lagarde": "EURUSD=X",  # ECB President Lagarde speaks
    "ECB": "EURUSD=X",  # European Central Bank
    "Eurozone": "EURUSD=X",  # Eurozone-related events
    # Fed-related events
    "Fed": "^GSPC",  # S&P 500 for Federal Reserve-related events
    "Powell": "^GSPC",  # Fed Chair Powell Speaks
    "Beige Book": "^GSPC",  # Beige Book
    # PMI (Purchasing Managers Index) events
    "PMI": "^DJI",  # Dow Jones for PMI events
    "Manufacturing PMI": "^DJI",  # PMI - Manufacturing
    "Services PMI": "^DJI",  # PMI - Services
    "Composite PMI": "^DJI",  # Composite PMI
    # Crude Oil & Energy events
    "Oil": "CL=F",  # Crude Oil Futures
    "Crude Oil Inventories": "CL=F",  # Crude Oil Inventories
    "Gasoline Inventories": "RB=F",  # Gasoline Futures
    "Natural Gas": "NG=F",  # Natural Gas Futures
    "Heating Oil": "HO=F",  # Heating Oil Futures
    "Cushing Crude Oil Inventories": "CL=F",  # Cushing Oil Inventory
    # Stock indices events
    "S&P": "^GSPC",  # S&P 500
    "DJI": "^DJI",  # Dow Jones Index
    "Nikkei": "^N225",  # Nikkei 225
    "DAX": "^GDAXI",  # Germany DAX
    "FTSE": "^FTSE",  # UK FTSE 100
    "CAC": "^FCHI",  # France CAC 40
    "NSEI": "^NSEI",  # Indian Nifty 50
    "IBEX": "^IBEX",  # Spanish IBEX 35
    # Central Bank related events
    "BoE": "GBPUSD=X",  # Bank of England (GBP/USD)
    "BoJ": "^N225",  # Bank of Japan (Nikkei)
    "Fed Chair": "^GSPC",  # Federal Reserve Chair Speaks
    "Russia": "USDRUB=X",  # General Russia-related events
    "Russian": "USDRUB=X",  # Specifically mentioning Russian
    "Ruble": "USDRUB=X",  # Any mention of the Ruble
    "Moscow": "USDRUB=X",  # Moscow-related economic events
    "Central Bank of Russia": "USDRUB=X",  # Russian Central Bank actions
    # Economic reports & GDP
    "GDP": "^GSPC",  # General GDP events (S&P 500)
    "Exports": "^GSPC",  # Exports (S&P 500)
    "Imports": "^GSPC",  # Imports (S&P 500)
    "Trade Balance": "USDCAD=X",  # USD/CAD for trade balance
    # Inflation & Price-related
    "PPI": "^GSPC",  # Producer Price Index
    "CPI": "^GSPC",  # Consumer Price Index
    "Inflation": "^GSPC",  # Inflation Reports
    # Country-specific bonds and treasury events
    "Treasury": "^GSPC",  # U.S. Treasury
    "Bond Auction": "^GSPC",  # Bond Auctions
    # Other indicators and reports
    "Durables": "^DJI",  # Durable Goods Orders
    "Factory Orders": "^GSPC",  # Factory Orders
    "Retail Sales": "^DJI",  # Retail Sales
    "Unemployment": "^GSPC",  # Unemployment Rate
    "Jobless Claims": "^DJI",  # Jobless Claims
    # General terms
    "Speaks": "^GSPC",  # General speeches (S&P 500)
    "Index": "^DJI",  # General Index
    "Imports": "^GSPC",  # Imports data (S&P 500)
    # United States (Dollar)
    "United States": "EURUSD=X",  # USD exchange rate with EUR
    "USA": "EURUSD=X",
    "Federal Reserve": "^GSPC",
    "Treasury": "^GSPC",
    "Powell": "^GSPC",  # Federal Reserve Chair
    # Eurozone (Euro)
    "Eurozone": "EURUSD=X",
    "ECB": "EURUSD=X",
    "Lagarde": "EURUSD=X",  # ECB President Lagarde
    "Germany": "EURUSD=X",
    "France": "EURUSD=X",
    "Italy": "EURUSD=X",
    "Spain": "EURUSD=X",
    # United Kingdom (Pound)
    "United Kingdom": "GBPUSD=X",
    "UK": "GBPUSD=X",
    "BoE": "GBPUSD=X",  # Bank of England
    # Japan (Yen)
    "Japan": "USDJPY=X",
    "Yen": "USDJPY=X",
    "BoJ": "USDJPY=X",  # Bank of Japan
    # Russia (Ruble)
    "Russia": "USDRUB=X",
    "Russian": "USDRUB=X",
    "Ruble": "USDRUB=X",
    "Moscow": "USDRUB=X",
    "Central Bank of Russia": "USDRUB=X",
    # China (Yuan)
    "China": "USDCNY=X",
    "Yuan": "USDCNY=X",
    "PBOC": "USDCNY=X",  # People's Bank of China
    "Beijing": "USDCNY=X",
    # Canada (Dollar)
    "Canada": "USDCAD=X",
    "Canadian": "USDCAD=X",
    "BoC": "USDCAD=X",  # Bank of Canada
    # Australia (Dollar)
    "Australia": "AUDUSD=X",
    "Australian": "AUDUSD=X",
    "RBA": "AUDUSD=X",  # Reserve Bank of Australia
    # New Zealand (Dollar)
    "New Zealand": "NZDUSD=X",
    "Kiwi": "NZDUSD=X",
    "RBNZ": "NZDUSD=X",  # Reserve Bank of New Zealand
    # Switzerland (Franc)
    "Switzerland": "USDCHF=X",
    "Swiss": "USDCHF=X",
    "CHF": "USDCHF=X",
    "SNB": "USDCHF=X",  # Swiss National Bank
    # India (Rupee)
    "India": "USDINR=X",
    "Rupee": "USDINR=X",
    "RBI": "USDINR=X",  # Reserve Bank of India
    # Brazil (Real)
    "Brazil": "USDBRL=X",
    "Real": "USDBRL=X",
    "Brazilian": "USDBRL=X",
    # Mexico (Peso)
    "Mexico": "USDMXN=X",
    "Peso": "USDMXN=X",
    "Mexican": "USDMXN=X",
    # South Africa (Rand)
    "South Africa": "USDZAR=X",
    "Rand": "USDZAR=X",
    "South African": "USDZAR=X",
    # South Korea (Won)
    "South Korea": "USDKRW=X",
    "Won": "USDKRW=X",
    "Korean": "USDKRW=X",
    # Turkey (Lira)
    "Turkey": "USDTRY=X",
    "Lira": "USDTRY=X",
    "Turkish": "USDTRY=X",
    # Singapore (Dollar)
    "Singapore": "USDSGD=X",
    "SGD": "USDSGD=X",
    "MAS": "USDSGD=X",  # Monetary Authority of Singapore
    # Hong Kong (Dollar)
    "Hong Kong": "USDHKD=X",
    "HKD": "USDHKD=X",
    # Argentina (Peso)
    "Argentina": "USDARS=X",
    "Argentine": "USDARS=X",
    # Nigeria (Naira)
    "Nigeria": "USDNGN=X",
    "Naira": "USDNGN=X",
    # Saudi Arabia (Riyal)
    "Saudi Arabia": "USDSAR=X",
    "Riyal": "USDSAR=X",
    "Saudi": "USDSAR=X",
    # United Arab Emirates (Dirham)
    "UAE": "USDAED=X",
    "Dirham": "USDAED=X",
    # Israel (Shekel)
    "Israel": "USDILS=X",
    "Shekel": "USDILS=X",
    # Egypt (Pound)
    "Egypt": "USDEGP=X",
    "Egyptian": "USDEGP=X",
    # Thailand (Baht)
    "Thailand": "USDTHB=X",
    "Baht": "USDTHB=X",
    # Vietnam (Dong)
    "Vietnam": "USDVND=X",
    "Dong": "USDVND=X",
    # Malaysia (Ringgit)
    "Malaysia": "USDMYR=X",
    "Ringgit": "USDMYR=X",
    # Indonesia (Rupiah)
    "Indonesia": "USDIDR=X",
    "Rupiah": "USDIDR=X",
    # Philippines (Peso)
    "Philippines": "USDPHP=X",
    "Philippine": "USDPHP=X",
    # Chile (Peso)
    "Chile": "USDCLP=X",
    "Chilean": "USDCLP=X",
 
   # French nationality
    "French": "^FCHI", # French CAC 40 index
   
    # Spanish nationality
    "Spanish": "^IBEX", # Spanish IBEX 35 index
   
    # Russian nationality
    "Russian": "MOEX.ME", # Russian MOEX index
   
    # German nationality
    "German": "^GDAXI", # German DAX index
   
    # Dutch nationality
    "Dutch": "^AEX", # Netherlands AEX index
   
    # Italian nationality
    "Italian": "^FTSE MIB", # Italy FTSE MIB index
   
    # American nationality
    "American": "^DJI", # Dow Jones for American events
    "US": "^DJI", # Dow Jones for US-related events
   
    # British nationality
    "British": "^FTSE", # UK FTSE 100 index
   
    # Japanese nationality
    "Japanese": "^N225", # Japanese Nikkei 225 index
   
    # Canadian nationality
    "Canadian": "^GSPTSE", # Canada TSX index
   
    # Swiss nationality
    "Swiss": "^SSMI", # Switzerland SMI index
   
    # Australian nationality
    "Australian": "^AXJO", # Australia ASX 200 index
   
    # Indian nationality
    "Indian": "^NSEI", # India Nifty 50 index
   
    # Brazilian nationality
    "Brazilian": "^BVSP", # Brazil Bovespa index
   
    # South Korean nationality
    "Korean": "^KS11", # Korea KOSPI index
   
    # Chinese nationality
    "Chinese": "^SSEC", # China Shanghai Composite index
   
    # Mexican nationality
    "Mexican": "^MXX", # Mexico IPC index
   
    # Swedish nationality
    "Swedish": "^OMX", # Sweden OMX Stockholm 30 index
   
    # Belgian nationality
    "Belgian": "^BFX", # Belgium BEL 20 index
   
    # Argentine nationality
    "Argentine": "^MERVAL", # Argentina Merval index
   
    # Chilean nationality
    "Chilean": "^IPSA", # Chile IPC index
   
    # Norwegian nationality
    "Norwegian": "^OSEAX", # Norway OBX index
   
    # Danish nationality
    "Danish": "^OMX", # Denmark OMXC20 index
   
    # Finnish nationality
    "Finnish": "^OMXH25", # Finland OMX Helsinki 25 index
   
    # Greek nationality
    "Greek": "^ATG", # Greece Athens General Index
   
    # Portuguese nationality
    "Portuguese": "^PSI20", # Portugal PSI 20 index
   
    # Israeli nationality
    "Israeli": "^TA-35", # Israel Tel Aviv 35 index
   
    # Singaporean nationality
    "Singaporean": "^STI", # Singapore Straits Times Index
   
    # South African nationality
    "South African": "^JALSH", # South Africa JSE All Share index
   
    # Turkish nationality
    "Turkish": "^XU100", # Turkey Borsa Istanbul 100 index
   
    # Egyptian nationality
    "Egyptian": "^EGX30", # Egypt EGX 30 index
   
    # Iranian nationality
    "Iranian": "^TEDPIX", # Iran Tehran Stock Exchange index
   
    # Pakistani nationality
    "Pakistani": "^KSE100", # Pakistan KSE 100 index
   
    # Thai nationality
    "Thai": "^SET50", # Thailand SET50 index
   
    # Malaysian nationality
    "Malaysian": "^KLSE", # Malaysia FTSE Bursa Malaysia KLCI index
   
    # Indonesian nationality
    "Indonesian": "^JCI", # Indonesia Jakarta Composite index
   
    # Vietnamese nationality
    "Vietnamese": "^VNINDEX", # Vietnam VN-Index index
   
    # New Zealand nationality
    "New Zealand": "^NZ50", # New Zealand NZX 50 index
   
    # Lebanese nationality
    "Lebanese": "^BLOM", # Lebanon BLOM Stock Index
   
    # Saudi Arabian nationality
    "Saudi Arabian": "^TASI", # Saudi Arabia Tadawul All Share index
   
    # UAE nationality
    "Emirati": "^ADX", # UAE Abu Dhabi Securities Exchange index
   
    # Kuwaiti nationality
    "Kuwaiti": "^KWSE", # Kuwait KSE index
   
    # Omani nationality
    "Omani": "^MSM30", # Oman MSM 30 index
   
    # Bahraini nationality
    "Bahraini": "^BAX", # Bahrain BSE index
   
    # Qatar nationality
    "Qatari": "^QSI", # Qatar QE Index
   
    # Kuwaiti nationality
    "Kuwaiti": "^KWSE", # Kuwait Kuwait Stock Exchange index
   
    # Filipino nationality
    "Filipino": "^PCOMP", # Philippines PSEi index
   
    # Indonesian nationality
    "Indonesian": "^JKSE", # Indonesia Jakarta Composite index
   
    # Vietnamese nationality
    "Vietnamese": "^VNI", # Vietnam VN-Index index
   
    # Colombian nationality
    "Colombian": "^COLCAP", # Colombia COLCAP index
   
    # Peruvian nationality
    "Peruvian": "^SPBLPERU", # Peru Lima General index
   
    # Dominican nationality
    "Dominican": "^BVC", # Dominican Republic BVC index
   
    # Kenyan nationality
    "Kenyan": "^NSE", # Kenya Nairobi Securities Exchange index
   
    # Nigerian nationality
    "Nigerian": "^NGSE", # Nigeria NSE index
   
    # Kenyan nationality
    "Kenyan": "^NSE", # Kenya Nairobi Securities Exchange
   
    # Nepalese nationality
    "Nepalese": "^NEPSE", # Nepal Nepal Stock Exchange index       
 
    
    
    
    
    
    }

    # Iterate through the keyword mapping and check for a match
    for keyword, symbol in keyword_mapping.items():
        if keyword.lower() in event_title.lower():
            return symbol

    # Return "SPY" as a default symbol if no match is found
    return "SPY"




# Function to process the events and update the EVENT_SYMBOLS dictionary
# Function to process the events and update the EVENT_SYMBOLS dictionary
def update_event_symbols_from_results(events):
    updated_events = []

    for event in events:
        event_title = event.strip()  # Clean up the event title (remove whitespace)
        
        # Dynamically assign a symbol based on the event title
        symbol = assign_symbol_based_on_keywords(event_title)
        
        # If no match is found, default to SPY
        if not symbol:
            symbol = "SPY"

        updated_events.append((event_title, symbol))

    return updated_events


# Function to update the EVENT_SYMBOLS dictionary
def update_event_symbols():
    # Step 1: Download the HTML content
    download_html()

    # Step 2: Parse the downloaded HTML and generate results.txt
    run_parser()

    # Step 3: Read the events from results.txt
    events = parse_results_file()

    # Step 4: Update event symbols based on keywords
    updated_events = update_event_symbols_from_results(events)

    # Step 5: Update the EVENT_SYMBOLS dictionary with the new events and symbols
    for event, symbol in updated_events:
        if symbol != "Unknown":  # Only update if a valid symbol is found
            EVENT_SYMBOLS[event] = symbol

    # Optionally, print the updated dictionary or save it to a file
    for event, symbol in EVENT_SYMBOLS.items():
        print(f"Event: {event}, Symbol: {symbol}")


# Main flow
def main():
    # Step 1: Update the event symbols from Investing.com
    update_event_symbols()

    # Initialize your PyQt5 application or other parts of your program
    app = QApplication(sys.argv)
    window = MacroEconomicNewsImpactApp()
    window.showMaximized()  # Ensure the window is maximized
    sys.exit(app.exec_())


# Function to save settings to disk
def save_settings(theme):
    settings = {'theme': theme}
    with open('settings.json', 'w') as f:
        json.dump(settings, f)


# Function to load settings from disk
def load_settings():
    if os.path.exists('settings.json'):
        with open('settings.json', 'r') as f:
            return json.load(f)
    return {'theme': 'light'}  # Default to light theme


# PyQt5 Main Window Class
class MacroEconomicNewsImpactApp(QMainWindow):
    def __init__(self):
        super().__init__()
    
        self.setWindowTitle("EconoMancer  v 3.9 - Macroeconomic News Impact")
        self.setGeometry(100, 100, 800, 600)
    
        self.settings = load_settings()  # Load settings (theme)
        self.set_theme(self.settings['theme'])  # Apply theme
    
        # Main layout
        self.main_layout = QVBoxLayout()
    
        # Tab widget to organize sections
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_economic_calendar_tab(), "Economic Calendar")
        self.tabs.addTab(self.create_market_data_tab(), "Market Data")
        self.tabs.addTab(self.create_settings_tab(), "Settings")
        self.tabs.addTab(self.create_about_tab(), "About")  # Add About tab here
    
        self.main_layout.addWidget(self.tabs)
    
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)
    
        # Automatically load economic events
        self.load_upcoming_events()

    def create_about_tab(self):
        about_tab = QWidget()
        layout = QVBoxLayout()
    
        # Create the About content text
        about_text = """
        <h2>EconoMancer (c) 2024 Sig Labs - Peter De Ceuster</h2>
        <p>If you like this software, buy me a coffee:</p>
        <a href="https://buymeacoffee.com/siglabo">https://buymeacoffee.com/siglabo</a>
        """
    
        # Create QLabel to display the text
        about_label = QLabel(about_text)
        
        # Make the text wrap and align it properly
        about_label.setAlignment(Qt.AlignCenter)  # Center the text
        about_label.setWordWrap(True)  # Allow text to wrap within the label
    
        # Make the URL clickable
        about_label.setTextFormat(Qt.RichText)
        about_label.setOpenExternalLinks(True)
    
        # Force black font color
        about_label.setStyleSheet("color: black;")
    
        layout.addWidget(about_label)  # Add the label to the layout
    
        about_tab.setLayout(layout)  # Apply layout to the tab
    
        return about_tab


    def set_theme(self, theme):
        if theme == 'dark':
            self.setStyleSheet("""
                QMainWindow { background-color: #2E2E2E; color: white; }
                QPushButton, QTableWidget { background-color: #4D4D4D; color: white; }
                QLabel { color: white; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #FFFFFF; color: black; }
                QPushButton, QTableWidget { background-color: #F0F0F0; color: black; }
                QLabel { color: black; }
            """)
    
        # Save the theme setting
        save_settings(theme)

    def create_economic_calendar_tab(self):
        # Create Economic Calendar tab with table
        calendar_tab = QWidget()
        layout = QVBoxLayout()

        self.event_table = QTableWidget()
        self.event_table.setColumnCount(3)
        self.event_table.setHorizontalHeaderLabels(['Time', 'Event', 'Importance'])

        layout.addWidget(self.event_table)
        calendar_tab.setLayout(layout)
        return calendar_tab

    def create_market_data_tab(self):
        # Create Market Data tab
        market_data_tab = QWidget()
        layout = QVBoxLayout()
    
        self.plot_label = QLabel("Market Reaction to Event")
        self.plot_label.setAlignment(Qt.AlignCenter)
        self.plot_label.setStyleSheet("font-size: 16px; font-weight: bold;")
    
        self.plot_canvas = FigureCanvas(plt.figure(figsize=(12, 8)))
        self.plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
        # Dropdown to select event
        self.event_dropdown = QComboBox()
        self.event_dropdown.addItem("Select Event")
        self.event_dropdown.currentIndexChanged.connect(self.on_event_selected)
        self.event_dropdown.setStyleSheet("font-size: 38px; padding: 5px;")
    
        # Add widgets to layout
        layout.addWidget(self.event_dropdown)
        layout.addWidget(self.plot_label)
        layout.addWidget(self.plot_canvas, stretch=1)  # Give priority to the graph
    
        market_data_tab.setLayout(layout)
        return market_data_tab

    def create_settings_tab(self):
        settings_tab = QWidget()
        layout = QVBoxLayout()
    
        # Add stylish toggle buttons for themes
        self.dark_theme_button = QPushButton("Dark Theme")
        self.light_theme_button = QPushButton("Light Theme")
    
        # Style the buttons to look like toggles
        button_style = """
            QPushButton {
                background-color: #4D4D4D; color: white; border: 2px solid #555;
                border-radius: 10px; padding: 10px; font-size: 16px;
            }
            QPushButton:pressed {
                background-color: #666;
            }
            QPushButton:checked {
                background-color: #2E2E2E;
            }
        """
        self.dark_theme_button.setStyleSheet(button_style)
        self.light_theme_button.setStyleSheet(button_style)
    
        # Connect buttons to change themes
        self.dark_theme_button.clicked.connect(lambda: self.set_theme('dark'))
        self.light_theme_button.clicked.connect(lambda: self.set_theme('light'))
    
        # Add buttons to layout
        layout.addWidget(self.dark_theme_button)
        layout.addWidget(self.light_theme_button)
    
        settings_tab.setLayout(layout)
        return settings_tab

    def on_theme_changed(self):
        # Change theme based on user selection
        if self.dark_theme_radio.isChecked():
            self.set_theme('dark')
            self.settings['theme'] = 'dark'
        else:
            self.set_theme('light')
            self.settings['theme'] = 'light'
        
        save_settings(self.settings['theme'])  # Save settings to disk

    def load_upcoming_events(self):
        # Fetch and display economic events
        events_df = scrape_economic_calendar('https://www.investing.com/economic-calendar/')
        self.events_df = events_df  # Save for later use
    
        if events_df.empty:
            print("No events found.")
            return
    
        self.event_table.setRowCount(len(events_df))
    
        for i, row in events_df.iterrows():
            self.event_table.setItem(i, 0, QTableWidgetItem(row['Time']))
            self.event_table.setItem(i, 1, QTableWidgetItem(row['Event']))
    
            importance_item = QTableWidgetItem(row['Importance'])
            if row['Importance'] == 'High':
                importance_item.setForeground(Qt.red)  # High: Red
            elif row['Importance'] == 'Medium':
                importance_item.setForeground(Qt.darkYellow)  # Medium: Orange
            else:
                importance_item.setForeground(Qt.darkGreen)  # Low: Green
            self.event_table.setItem(i, 2, importance_item)
    
        # Populate the dropdown
        self.event_dropdown.clear()  # Clear existing items
        self.event_dropdown.addItem("Select Event")  # Add default placeholder
        self.event_dropdown.addItems(events_df['Event'].tolist())  # Add events

    def on_event_selected(self):
        selected_event = self.event_dropdown.currentText()
        
        if selected_event != "Select Event":
            print(f"Selected event: {selected_event}")
            event_data = self.events_df[self.events_df['Event'].str.strip() == selected_event.strip()]
            
            if event_data.empty:
                print(f"No event found for {selected_event}")
                return
            
            event_row = event_data.iloc[0]
            event_time = event_row['Time']
            symbol = event_row['Symbol']
            
            print(f"Event selected: {selected_event}, mapped to symbol: {symbol}")
        
            # Plot market reaction for the specific event
            fig = backtest_market_reaction(event_time, selected_event, symbol)
            
            if fig:
                self.plot_canvas.figure = fig
                self.plot_canvas.draw()
            else:
                print("No valid figure returned, skipping plot.")

if __name__ == "__main__":
    main()
