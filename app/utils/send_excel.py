import requests
from openpyxl.styles import Border, Side
from openpyxl.workbook import Workbook


def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data from the endpoint.")
        return None


def write_to_excel(data):
    wb = Workbook()
    ws = wb.active
    ws.append(["Наименование", "Цена"])

    for item in data:
        name = item["name"]
        price = item["price"]
        if item["quantity"] < 10:
            name += f" ({item['quantity']})"
        ws.append([name, price])

    # Добавляем обводку таблицы
    border = Border(left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin'))

    for row in ws.iter_rows():
        for cell in row:
            cell.border = border

    wb.save("price.xlsx")
    print("Data has been written to price.xlsx")


def write_to_excel_default(data):
    wb = Workbook()
    ws = wb.active
    ws.append(["Наименование", "Количество", "Цена"])

    for item in data:
        name = item["name"]
        quantity = item["quantity"]
        price = item["price"]
        if quantity < 10:
            name += f" ({quantity})"
        ws.append([name, quantity, price])

    # Добавляем обводку таблицы
    border = Border(left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin'))

    for row in ws.iter_rows():
        for cell in row:
            cell.border = border

    wb.save("price_default.xlsx")
    print("Data has been written to price_default.xlsx")
