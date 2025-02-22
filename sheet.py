import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
CREDENTIALS_FILE = "./credential/gg_credential.json"
SPREADSHEET_ID = "1BZF7FL9cjJfipse_UTmZH4xq9ihxzLV6iTY9jwYQoOw"


# Kết nối với Google Sheets
def connect_google_sheets():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)


# Hàm ghi dữ liệu vào ô tương ứng với ngày hiện tại
def write_data_to_sheet(name, date_time):
    col = mapping.get(name, "")
    if not col:
        print(f"ERROR: can't write {name} to sheet.")
        return
    sheet = connect_google_sheets().sheet1
    today = date_time.strftime("%Y-%m-%d %H:%M")
    data = True

    sheet_data = sheet.col_values(1)
    if sheet_data[-1] == today:
        row_count = len(sheet_data)
    else:
        row_count = len(sheet_data) + 1

    sheet.update(f"A{row_count}", [[today]])
    sheet.update(f"{col}{row_count}", [[data]])


mapping = {
    "ahien": "B",
    "aluong": "C",
    "anh": "D",
    "atruong": "E",
    "d2": "F",
    "gam": "G",
    "hien": "H",
    "hoang": "I",
    "huy": "J",
    "sy": "K",
    "t_anh": "L",
    "thai": "M",
    "thong": "N",
    "thuong": "O",
    "tlinh": "P",
    "toan": "Q",
    "trang": "R",
    "truong": "S",
    "viet": "T",
    "nam": "U",
}
