import openpyxl
import requests
from openpyxl.cell import MergedCell
from requests.exceptions import RequestException
import logging
import os
import pandas as pd

def download_file(url: str, file_path: str) -> bool:
    try:
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
    except RequestException as e:
        logging.warning(
            f'error while download file: {e}'
        )
        return False

    with open(file_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    logging.info(
        f'file {file_path} successfully download'
    )

    return True

def start_str_idx(df) -> int:
    column = df.iloc[:, 0]
    for idx in range(len(column)):
        if str(column[idx]) == 'nan':
            continue
        return idx

    return 0

def is_cell_merged(wb, row, column):
    sheet = wb.active
    cell = sheet.cell(row=row, column=column)
    return isinstance(cell, MergedCell)

def parse_schedule_info():
    url = 'https://rasp.pgups.ru/files/b/2024/ait_2.xlsx'
    file_path = os.path.join(os.path.dirname(__file__), 'schedule_files', 'ait_2.xlsx')
    data_frame = pd.read_excel(file_path)
    wb = openpyxl.load_workbook(file_path)
    str_start = start_str_idx(data_frame)
    print(str_start)
    str_count, col_count = data_frame.shape
    days_iterator = data_frame.iloc[:, 0]
    time_iterator = data_frame.iloc[:, 1]
    for col_idx in range(2, col_count):
        col_iterator = data_frame.iloc[:, col_idx]
        group_name = col_iterator[str_start - 1].strip()
        print(f"Группа: {group_name}")
        for str_delta in range(str_count - str_start - 1):
            day = str(days_iterator[str_start + str_delta])
            if day != 'nan':
                print(day.strip().lower())

            schedule_str_raw = str(col_iterator[str_start + str_delta])
            if schedule_str_raw == 'nan':
                continue

            t = str(time_iterator[str_start + str_delta])
            if t != 'nan':
                print(t.strip())

            if is_cell_merged(wb, str_start + str_delta + 3, col_idx + 1):
                week_type = 'всегда'
            elif str_delta % 2 == 0:
                week_type = 'нечетная'
            else:
                week_type = 'четная'
            print(' '.join(schedule_str_raw.split()))
            print('Неделя:', week_type)

#parse_schedule_info()


# download_file(
#     'https://rasp.pgups.ru/files/b/2024/ait_2.xlsx',
#     os.path.join(os.path.dirname(__file__), 'schedule_files', 'ait_2.xlsx')
# )