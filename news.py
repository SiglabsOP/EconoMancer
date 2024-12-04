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
plt.rcParams['figure.dpi'] = 100  # Adjust DPI for better clarity


# Event-to-Market Symbol Mapping
EVENT_SYMBOLS = {
    "30-Year JGB Auction": "^N225",  # Nikkei 225
    "30-Year Treasury Gilt Auction": "GB30.GB",  # UK Gilt
    "7-Year Treasury Gilt Auction": "GB7.GB",  # UK Gilt
    "ADP Nonfarm Employment Change  (Nov)": "^DJI",  # Dow Jones
    "Beige Book": "^GSPC",  # S&P 500
    "BoE Gov Bailey Speaks": "GBPUSD=X",  # GBP/USD
    "BoJ Board Member Nakamura Speaks": "^N225",  # Nikkei 225
    "Car Registration (MoM)  (Nov)": "AUTO.MI",  # Auto index (placeholder)
    "Car Registration (YoY)  (Nov)": "AUTO.MI",
    "Crude Oil Imports": "CL=F",  # Crude Oil Futures
    "Crude Oil Inventories": "CL=F",
    "Cushing Crude Oil Inventories": "CL=F",
    "Distillate Fuel Production": "HO=F",  # Heating Oil Futures
    "Durables Excluding Defense (MoM)  (Oct)": "^DJI",
    "Durables Excluding Transport (MoM)  (Oct)": "^DJI",
    "ECB President Lagarde Speaks": "EURUSD=X",  # Euro to USD
    "EIA Refinery Crude Runs  (WoW)": "CL=F",
    "EIA Weekly Distillates Stocks": "HO=F",
    "EIA Weekly Refinery Utilization Rates (WoW)": "CL=F",
    "Exports (MoM)  (Oct)": "^GSPC",
    "Factory Orders (MoM)  (Oct)": "^GSPC",
    "Factory orders ex transportation (MoM)  (Oct)": "^GSPC",
    "Fed Chair Powell Speaks": "^GSPC",
    "Foreign Bonds Buying": "USDJPY=X",  # USD/JPY
    "Foreign Exchange Flows": "DXY",  # US Dollar Index
    "Foreign Investments in Japanese Stocks": "USDJPY=X",
    "French Government Budget Balance  (Oct)": "^FCHI",  # CAC 40
    "GDP (QoQ)  (Q3)": "^GSPC",
    "GDP (YoY)  (Q3)": "^GSPC",
    "Gasoline Inventories": "RB=F",  # Gasoline Futures
    "Gasoline Production": "RB=F",
    "German 10-Year Bund Auction": "DE10Y.BND",
    "German 2-Year Schatz Auction": "DE2Y.BND",
    "German Buba President Nagel Speaks": "EURUSD=X",
    "German Car Registration (YoY)": "^GDAXI",  # DAX
    "GlobalDairyTrade Price Index": "NZDUSD=X",  # NZD/USD
    "HCOB Eurozone Composite PMI  (Nov)": "^STOXX50E",  # Euro Stoxx 50
    "HCOB Eurozone Services PMI  (Nov)": "^STOXX50E",
    "HCOB France Composite PMI  (Nov)": "^FCHI",
    "HCOB France Services PMI  (Nov)": "^FCHI",
    "HCOB Germany Composite PMI  (Nov)": "^GDAXI",
    "HCOB Germany Services PMI  (Nov)": "^GDAXI",
    "HCOB Italy Composite PMI  (Nov)": "FTSEMIB.MI",  # FTSE MIB
    "HCOB Italy Services PMI  (Nov)": "FTSEMIB.MI",
    "HCOB Spain Services PMI  (Nov)": "^IBEX",  # IBEX 35
    "HSBC India Services PMI  (Nov)": "^NSEI",  # Nifty 50
    "Heating Oil Stockpiles": "HO=F",
    "ISM Non-Manufacturing Business Activity  (Nov)": "^DJI",
    "ISM Non-Manufacturing Employment  (Nov)": "^DJI",
    "ISM Non-Manufacturing New Orders  (Nov)": "^DJI",
    "ISM Non-Manufacturing PMI  (Nov)": "^DJI",
    "ISM Non-Manufacturing Prices  (Nov)": "^DJI",
    "Imports (MoM)  (Oct)": "^GSPC",
    "Industrial Production (MoM)  (Oct)": "^GSPC",
    "Industrial Production (YoY)  (Oct)": "^GSPC",
    "Labor Productivity (QoQ)  (Q3)": "^GSPC",
    "MBA 30-Year Mortgage Rate": "^GSPC",
    "MBA Mortgage Applications (WoW)": "^GSPC",
    "MBA Purchase Index": "^GSPC",
    "Manufacturing PMI  (Nov)": "^GSPC",
    "Milk Auctions": "NZDUSD=X",
    "Mortgage Market Index": "^GSPC",
    "Mortgage Refinance Index": "^GSPC",
    "Natural Gas Storage": "NG=F",  # Natural Gas Futures
    "PPI (MoM)  (Oct)": "^GSPC",
    "PPI (YoY)  (Oct)": "^GSPC",
    "Reserve Assets Total  (Nov)": "USDJPY=X",
    "Reuters Tankan Index  (Dec)": "^N225",
    "Russian Forex Intervention  (Dec)": "USDRUB=X",  # USD/RUB
    "Russian S&P Global Services PMI  (Nov)": "MOEX.ME",  # Moscow Exchange
    "S&P Global Composite PMI  (Nov)": "^GSPC",
    "S&P Global Services PMI  (Nov)": "^GSPC",
    "S&P Global South Africa PMI  (Nov)": "ZAR=X",  # USD/ZAR
    "S&P Global/CIPS UK Composite PMI  (Nov)": "^FTSE",  # FTSE 100
    "S&P Global/CIPS UK Services PMI  (Nov)": "^FTSE",
    "Trade Balance  (Oct)": "USDCAD=X",
}



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
            symbol = EVENT_SYMBOLS.get(title, "SPY")  # Default to SPY if no match

            # Assign dynamic importance
            importance = assign_importance(title)

            events.append((time, title, importance, symbol))
        except AttributeError:
            continue

    return pd.DataFrame(events, columns=['Time', 'Event', 'Importance', 'Symbol'])


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
    return yf.download(symbol, start=start_date, end=end_date)


# Function to backtest market reaction to an event
def backtest_market_reaction(event_time, event_name, symbol, before_days=3, after_days=3):
    # Convert the event time into a datetime object with the correct date
    today = datetime.now()
    event_date = today.strftime("%Y-%m-%d")  # Use today's date for simplicity, assuming event is today
    event_datetime = datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M")

    # Define the window of market data we want to look at (fetch daily data)
    start_date = (event_datetime - timedelta(days=before_days)).strftime("%Y-%m-%d")
    end_date = (event_datetime + timedelta(days=after_days)).strftime("%Y-%m-%d")

    # Fetch market data for the corresponding symbol
    market_data = fetch_historical_data(symbol, start_date, end_date)

    # Ensure market data is available
    if market_data.empty:
        print(f"No market data available for {symbol} during {start_date} to {end_date}")
        return None

    # Ensure event time is within the market data range
    closest_data_point = (
        market_data.index[0]
        if event_datetime < market_data.index[0]
        else market_data.index[-1]
        if event_datetime > market_data.index[-1]
        else event_datetime
    )

    # Plot the market data
    fig, ax = plt.subplots(figsize=(12, 8))  # Larger figure
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)  # Reduce margins

    ax.plot(market_data.index, market_data['Close'], label='Market Price', linewidth=2)

    # Add a vertical red line for the event time
    ax.axvline(x=closest_data_point, color='r', linestyle='--', label=f'{event_name} Time', linewidth=1.5)

    # Add shaded impact window
    ax.axvspan(closest_data_point - timedelta(hours=1), closest_data_point + timedelta(hours=1),
               color='red', alpha=0.3, label='Event Impact Window')

    # Set plot labels and title
    ax.set_title(f'Market Reaction to {event_name}', fontsize=18)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_ylabel('Price', fontsize=14)
    ax.legend(fontsize=12)

    return fig





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
        self.event_dropdown.setStyleSheet("font-size: 14px; padding: 5px;")
    
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
            # Print for debugging to see what events are in the DataFrame and what is selected
            print("Available events:", self.events_df['Event'].tolist())
            print(f"Selected event: {selected_event}")
    
            # Strip leading/trailing spaces for both the selected event and DataFrame events
            event_data = self.events_df[self.events_df['Event'].str.strip() == selected_event.strip()]
            
            if event_data.empty:
                print(f"No event found for {selected_event}")
                return  # Exit early if no matching event is found
            
            # Safely access the event data
            event_row = event_data.iloc[0]  # Get the first matching row
            event_time = event_row['Time']
            symbol = event_row['Symbol']
    
            # Plot market reaction for the specific event
            fig = backtest_market_reaction(event_time, selected_event, symbol)
            
            if fig:  # Only draw if a valid figure is returned
                self.plot_canvas.figure = fig
                self.plot_canvas.draw()
            else:
                print("No valid figure returned, skipping plot.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MacroEconomicNewsImpactApp()
    window.showMaximized()  # Ensure the window is maximized
    sys.exit(app.exec_())
