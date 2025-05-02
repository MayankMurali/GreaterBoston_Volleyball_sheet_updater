import os
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# CONFIG
SHEET_NAME = 'Volleyball signup'
WEATHER_API_KEY = os.environ['WEATHER_API_KEY']
LOCATION = 'Boston,US'
DAY_COLUMNS = ['B', 'C', 'D', 'E', 'F', 'G', 'H']
WEATHER_ROW = 10

# Load credentials JSON from environment variable
creds_json = json.loads(os.environ['GOOGLE_SHEET_CREDENTIALS'])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Get 5-day / 3-hour forecast
url = f'https://api.openweathermap.org/data/2.5/forecast?q={LOCATION}&appid={WEATHER_API_KEY}&units=metric'
response = requests.get(url)
data = response.json()

# Emoji map
emoji_map = {
    'Clear': '☀️',
    'Clouds': '☁️',
    'Rain': '🌧️',
    'Snow': '❄️',
    'Thunderstorm': '⛈️',
    'Drizzle': '🌦️',
    'Mist': '🌫️',
}

# Group by day
daily_summary = {}
for entry in data['list']:
    dt = datetime.fromtimestamp(entry['dt'])
    date_str = dt.strftime('%Y-%m-%d')
    if date_str not in daily_summary:
        daily_summary[date_str] = entry

# Update each day (up to 5 days, fallback repeats for 7)
dates = list(daily_summary.keys())
for i, col in enumerate(DAY_COLUMNS):
    if i < len(dates):
        day_data = daily_summary[dates[i]]
    else:
        # Repeat last available day if fewer than 7
        day_data = daily_summary[dates[-1]]
    weather_main = day_data['weather'][0]['main']
    temp = day_data['main']['temp']
    emoji = emoji_map.get(weather_main, '🌈')
    weather_summary = f'{emoji} {weather_main}, {round(temp)}°C'
    cell = f'{col}{WEATHER_ROW}'
    sheet.update(cell, [[weather_summary]])
    print(f'Updated {cell} → {weather_summary}')