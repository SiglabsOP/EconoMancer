# EconoMancer
 

EconoMancer
Version 3.9
Developed by Sig Labs - Peter De Ceuster

EconoMancer is a comprehensive software application for analyzing and visualizing the impact of macroeconomic events on financial markets. With powerful features like event scraping, market reaction backtesting, and customizable UI themes, EconoMancer empowers traders, analysts, and enthusiasts to make data-driven decisions.

Features
Economic Calendar Scraping: Automatically fetches the latest economic events from trusted sources like Investing.com.
Dynamic Symbol Assignment: Maps events to their respective financial instruments or currencies based on keywords.
Market Reaction Backtesting: Visualizes market price movements before and after specific events.
Customizable Themes: Switch between light and dark modes for a personalized user experience.
Interactive UI: Built with PyQt5 for a smooth and responsive user interface.
Advanced Charting: Displays clear and detailed market charts using Matplotlib. 




1. Scrape Economic Events
EconoMancer scrapes economic calendar data using BeautifulSoup4 and dynamically assigns symbols to events based on a comprehensive keyword mapping.

2. Backtest Market Reaction
Use the Backtest Market Reaction feature to visualize how financial instruments (e.g., stocks, indices, or currencies) behaved before and after specific macroeconomic events.

3. Interactive UI
The PyQt5-powered UI includes:

Economic Calendar Tab: Displays upcoming events with their assigned importance.
Market Data Tab: Allows users to select events and view corresponding market reactions.
Settings Tab: Customize themes and settings.
Market Reaction Chart

Customizations
Adding New Keywords and Symbols
You can extend the keyword-to-symbol mapping by editing the assign_symbol_based_on_keywords function in main.py:

python
Code kopiëren
keyword_mapping = {
    "Lagarde": "EURUSD=X",
    "Fed": "^GSPC",
    # Add new mappings here...
}
Adjusting Event Scraping
Update the scraping logic in the scrape_economic_calendar function to use alternative sources or parse additional data fields.

A manual version has been included in case you want to pull html files manually and parse them.
Run news-generative to use full automated features (auto pull source, and auto parse)
 



If you enjoy this program, buy me a coffee https://buymeacoffee.com/siglabo
You can use it free of charge or build upon my code. 
 
(c) Peter De Ceuster 2024
Software Distribution Notice: https://peterdeceuster.uk/doc/code-terms 
This software is released under the FPA General Code License.
 
 ![Screenshot 2024-12-04 085305](https://github.com/user-attachments/assets/30fd0583-9565-41ac-bf97-393fc20a0c58)
![Screenshot 2024-12-04 085311](https://github.com/user-attachments/assets/ded08cb4-a091-4b5b-b7e5-cc593c93f7af)

