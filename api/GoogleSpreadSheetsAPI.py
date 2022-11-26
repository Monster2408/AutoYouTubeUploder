from typing import List
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# Google Excelのデータを...
SPREADSHEET_KEY = "1ZtN8ZxxEd-S9ZXF2SoUZdiWw6f-D6mGpJ2kF6g2CJRg"
SHEET_NAME = "切り抜き動画" # リリース用

GOOGLE_API_PRIVATE_KEY = 'credentials.json'

# 地震速報の最終更新時間を記録したセル番号
EEW_DATA_CELL = 26

# MLS Twitter 自動更新 最終時間を記録したセル番号
TWITTER_DATA_CELL = 27

# 豆知識
MLS_TIPS_DATA_CELL = 28

def getDatas() -> List:
    """GoogleSpreadSheetsからデータを取得

    Returns:
        List: A1:Z1000のデータを取得。A1～Z1の次にA2～Z2へ進む。
    """
    global SCOPE
    global SPREADSHEET_KEY
    global GOOGLE_API_PRIVATE_KEY
    global SHEET_NAME
    credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_API_PRIVATE_KEY, SCOPE)
    gc = gspread.authorize(credentials)
    ws = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)

    ds = ws.range('A1:Z1000')
    return ds

def setDatas(ds: List):
    """GoogleSpreadSheetsのデータを上書き

    Returns:
        List: A1:Z1000のデータを書き込み。A1～Z1の次にA2～Z2へ進む。
    """
    global SCOPE
    global SPREADSHEET_KEY
    global GOOGLE_API_PRIVATE_KEY
    global SHEET_NAME
    credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_API_PRIVATE_KEY, SCOPE)
    gc = gspread.authorize(credentials)
    ws = gc.open_by_key(SPREADSHEET_KEY).worksheet(SHEET_NAME)
    ws.update_cells(ds)