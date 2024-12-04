from bs4 import BeautifulSoup

# Load the HTML file
with open('Economic Calendar - Investing.com.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extract unique event names
event_names = set()
for event in soup.select('td.event'):
    if event.get_text(strip=True):
        event_names.add(event.get_text(strip=True))

# Sort the event names
sorted_event_names = sorted(event_names)

# Write the sorted event names to a file
with open('results.txt', 'w', encoding='utf-8') as results_file:
    for name in sorted_event_names:
        results_file.write(name + '\n')

print("Event names have been written to results.txt")
