import os
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# CONFIG
SHEET_NAME = 'Volleyball signup'
WEATHER_API_KEY = os.environ['WEATHER_API_KEY']
LOCATION = 'Cambridge,US'
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

# Filter entries at 6 PM only
six_pm_forecasts = {}
for entry in data['list']:
    dt = datetime.fromtimestamp(entry['dt'])
    if dt.strftime('%H:%M:%S') == '18:00:00':
        date_str = dt.strftime('%Y-%m-%d')
        six_pm_forecasts[date_str] = entry

# Update each day (up to 7 columns)
dates = list(six_pm_forecasts.keys())
for i, col in enumerate(DAY_COLUMNS):
    if i < len(dates):
        day_data = six_pm_forecasts[dates[i]]
    else:
        day_data = six_pm_forecasts[dates[-1]]
    weather_main = day_data['weather'][0]['main']
    temp = day_data['main']['temp']
    emoji = emoji_map.get(weather_main, '🌈')
    weather_summary = f'{emoji} {weather_main}, {round(temp)}°C'
    cell = f'{col}{WEATHER_ROW}'
    sheet.update(cell, [[weather_summary]])
    print(f'Updated {cell} → {weather_summary}')
