from bs4 import BeautifulSoup

# Function to assign market symbol based on event title
def assign_symbol_based_on_keywords(event_title):
    keyword_mapping = {
        "Lagarde": "EURUSD=X",
        "Fed": "^GSPC",  # S&P 500 for Federal Reserve-related events
        "PMI": "^DJI",  # Dow Jones for PMI events
        "ECB": "EURUSD=X",  # European Central Bank
        "Oil": "CL=F",  # Crude Oil
        # Add more mappings as needed
    }

    for keyword, symbol in keyword_mapping.items():
        if keyword.lower() in event_title.lower():
            return symbol

    return "SPY"  # Default symbol for unmatched events


# Load the HTML file
with open('investing_data.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Initialize the list of events
events = []

# Extract event details
for event_row in soup.select('tr.js-event-item'):
    try:
        time_cell = event_row.select_one('td.time')
        time = time_cell.get_text(strip=True) if time_cell else "N/A"

        title_cell = event_row.select_one('td.event')
        title = title_cell.get_text(strip=True) if title_cell else "N/A"

        # Dynamically assign market symbol
        symbol = assign_symbol_based_on_keywords(title)

        # Assign importance based on the event title
        importance = "High" if "Speaks" in title or "Federal Reserve" in title else ("Medium" if "PMI" in title or "Index" in title else "Low")

        # Append the event with its time, title, importance, and symbol
        events.append((time, title, importance, symbol))

    except AttributeError:
        continue  # Skip any rows that don't have the necessary data

# Sort the events by title (or any other logic you prefer)
events_sorted = sorted(events, key=lambda x: x[1])  # Sorting by event name (title)

# Write the sorted events to the results.txt file
with open('resultsgen.txt', 'w', encoding='utf-8') as results_file:
    for event in events_sorted:
        # Format: Time, Event Name, Importance, Symbol
        results_file.write(f"{event[0]} | {event[1]} | {event[2]} | {event[3]}\n")

print("Events have been written to results.txt")
