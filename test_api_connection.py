import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


creds_json = json.loads(os.environ['GOOGLE_SHEET_CREDENTIALS'])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)


sheet = client.open('Volleyball signup').sheet1


print("Spreadsheet title:", sheet.spreadsheet.title)
print("Worksheet title:", sheet.title)
print("Worksheet ID:", sheet.id)
print("Rows:", sheet.row_count)
print("Columns:", sheet.col_count)
print("Worksheet URL:", sheet.spreadsheet.url)


all_values = sheet.get_all_values()
print("First few rows of data:")
for row in all_values[:5]: 
    print(row)