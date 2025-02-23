import time

import openpyxl
import requests
from openpyxl.cell import MergedCell
from requests.exceptions import RequestException
import logging
import os
import pandas as pd
from django.db import transaction
from celery import shared_task

from info_board.config import main_config
from info_board.schedule.models import ScheduleEntry, Faculty, StudentsGroup


@shared_task
def parse_schedule_info():
    for faculty in main_config.schedule.faculties:
        for course_number in main_config.schedule.course_numbers:
            url = main_config.schedule.parse_url.format(
                main_config.schedule.year,
                faculty,
                course_number
            )
            file_path = os.path.join(
                os.path.dirname(__file__),
                'schedule_files',
                f'{faculty}_{course_number}.xlsx'
            )
            if download_file(url, file_path):
                try:
                    parse_excel_to_db(file_path, course_number)
                except Exception as e:
                    logging.error(e)
                else:
                    logging.info(
                        f'faculty: {faculty}, course: {course_number} was parsed successfully'
                    )
                    time.sleep(main_config.parse_delay_sec)


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


@transaction.atomic()
def parse_excel_to_db(file_path, course_number):
    data_frame = pd.read_excel(file_path)
    wb = openpyxl.load_workbook(file_path)

    str_start = start_str_idx(data_frame)
    str_count, col_count = data_frame.shape
    faculty_name = str(wb.active.title).split()[0]

    days_iterator = data_frame.iloc[:, 0]
    time_iterator = data_frame.iloc[:, 1]

    faculty, _ = Faculty.objects.get_or_create(short_name=faculty_name)
    faculty.save()

    for col_idx in range(2, col_count):
        col_iterator = data_frame.iloc[:, col_idx]
        students_group = str(col_iterator[str_start - 1]).strip()

        if students_group == 'nan':
            continue

        group, _ = StudentsGroup.objects.get_or_create(
            name=students_group,
            course_number=course_number,
            faculty=faculty
        )
        group.schedule_entries.all().delete()
        group.save()

        days_storage = list()
        times_storage = list()

        for str_delta in range(str_count - str_start - 1):
            schedule_str_raw = str(col_iterator[str_start + str_delta])

            day_of_week = str(days_iterator[str_start + str_delta])
            if day_of_week != 'nan':
                days_storage.append(day_of_week.strip().lower())

            study_time = str(time_iterator[str_start + str_delta])
            if study_time != 'nan':
                times_storage.append(study_time.strip())

            if schedule_str_raw == 'nan':
                continue

            if is_cell_merged(wb, str_start + str_delta + 3, col_idx + 1):
                type_of_week = ScheduleEntry.TypesOfWeek.ALWAYS
            elif str_delta % 2 == 0:
                type_of_week = ScheduleEntry.TypesOfWeek.ODD
            else:
                type_of_week = ScheduleEntry.TypesOfWeek.EVEN

            entry = ' '.join(schedule_str_raw.split())
            schedule_entry = ScheduleEntry(
                entry=entry,
                day_of_week=days_storage[-1],
                type_of_week=type_of_week,
                study_time=times_storage[-1],
                students_group=group
            )
            schedule_entry.save()
