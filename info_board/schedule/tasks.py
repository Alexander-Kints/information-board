import logging
import os
import time
from typing import List

import openpyxl
import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
from celery import shared_task
from django.db import transaction
from django.db.models import ObjectDoesNotExist
from openpyxl.cell import MergedCell
from requests.exceptions import RequestException

from info_board.config import main_config
from info_board.employee.models import Employee
from info_board.employee.utils import clear_data, parse_name
from info_board.schedule.models import (Faculty, Room, ScheduleEntry,
                                        StudentsGroup, Subgroup)


@shared_task
def parse_schedule_info_excel():
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
                        f'faculty: {faculty}, course: {course_number} parsed'
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

    for col_idx in range(2, col_count):
        col_iterator = data_frame.iloc[:, col_idx]
        students_group = str(col_iterator[str_start - 1]).strip()

        if students_group == 'nan':
            continue

        group, created = StudentsGroup.objects.get_or_create(
            name=students_group,
            course_number=course_number,
            faculty=faculty
        )
        if not created:
            group.subgroups.all().delete()

        subgroup = Subgroup.objects.create(number=1, group=group)
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

            formatted_time = ScheduleEntry.format_study_time(times_storage[-1])
            subject_number = ScheduleEntry.time_to_number(formatted_time)

            if is_cell_merged(wb, str_start + str_delta + 3, col_idx + 1):
                type_of_week = ScheduleEntry.TypesOfWeek.ALWAYS
            elif str_delta % 2 == 0:
                type_of_week = ScheduleEntry.TypesOfWeek.ODD
            else:
                type_of_week = ScheduleEntry.TypesOfWeek.EVEN

            subject = ' '.join(schedule_str_raw.split())
            schedule_entry = ScheduleEntry(
                subject=subject,
                day_of_week=days_storage[-1],
                type_of_week=type_of_week,
                study_time=formatted_time,
                subject_number=subject_number,
                subgroup=subgroup
            )
            schedule_entry.save()


@shared_task
def parse_schedule_info_rasp() -> None:
    pages_count = schedule_pages_count(
        main_config.schedule.parse_url_rasp.format(1)
    )

    for page_number in range(pages_count):
        url = main_config.schedule.parse_url_rasp.format(page_number)
        groups_urls = group_names_dict(url)

        for group_name, group_url in groups_urls.items():
            try:
                group = StudentsGroup.objects.get(name=group_name)
            except ObjectDoesNotExist:
                continue

            try:
                with transaction.atomic():
                    subgroup_urls = get_subgroup_urls(group_url)
                    group.subgroups.all().delete()
                    group.save()

                    for subgroup_number, subgroup_url in enumerate(subgroup_urls):
                        subgroup = Subgroup.objects.create(
                            number=subgroup_number + 1,
                            group=group
                        )
                        subgroup_to_db(
                            subgroup, subgroup_url, 0,
                            ScheduleEntry.TypesOfWeek.EVEN
                        )
                        time.sleep(main_config.parse_delay_sec)

                        subgroup_to_db(
                            subgroup, subgroup_url, 1,
                            ScheduleEntry.TypesOfWeek.ODD
                        )
                        time.sleep(main_config.parse_delay_sec)
            except Exception as e:
                logging.error(e)
            else:
                logging.info(f'group {group_name} was parsed from rasp')


def get_subgroup_urls(url: str) -> list:
    result_urls = list()
    resp = requests.get(url)

    if not resp.ok:
        raise Exception(f'error while parsing {url}')

    soup = BeautifulSoup(resp.text, 'lxml')
    subgroup_div = soup.find('div', class_='kt-portlet__head-group')

    if not subgroup_div:
        raise Exception(f'error while parsing (no schedule) {url}')

    for a_el in subgroup_div.contents:
        if isinstance(a_el, Tag):
            result_urls.append(a_el.get('href'))

    return result_urls


def subgroup_to_db(subgroup: Subgroup, subgroup_url, odd, week_type) -> None:
    url = f'{subgroup_url}?odd={odd}'
    resp = requests.get(url)
    if not resp.ok:
        raise Exception(f'bad status code resp: {url}')

    soup = BeautifulSoup(resp.text, 'lxml')

    tables = soup.find_all('table', class_="table m-table mb-5")

    if not tables:
        logging.warning(f'no tables: {url}')
        return None

    tables.pop()

    for table in tables:
        day_of_week = table.find('h4', class_="kt-font-dark")
        if day_of_week:
            day_of_week = day_of_week.get_text(strip=True).lower()

        schedule_entries = table.find_all('tr')
        if not schedule_entries:
            continue

        for entry in schedule_entries:
            study_time = entry.find('span', style=" white-space: nowrap;")
            if study_time:
                study_time = ''.join(
                    study_time.get_text(strip=True).split()
                ).replace('—', '-')

            room = entry.find('div', class_="text-center mt-2")
            if room:
                room = room.find('a', class_="kt-link")
                room = ''.join(room.get_text(strip=True).split())
                room, _ = Room.objects.get_or_create(name=room)

            subject_data = entry.find('div', class_="mb-2")
            if subject_data:
                lesson_data = clear_data(
                    subject_data.contents, ' ', '\n', ''
                )
                subject = ' '.join(lesson_data[0].split())
                subject_type = ' '.join(lesson_data[1].split())
            else:
                raise Exception(f'no subject data: {url}')

            employees = entry.find('td', class_='align-middle')
            if employees:
                employees = employees.find_all('a', class_="kt-link")
                employees = list(map(
                    lambda el: ' '.join(el.get_text(strip=True).split()),
                    employees
                ))

            schedule_entry = ScheduleEntry.objects.create(
                subject=subject,
                day_of_week=day_of_week,
                type_of_week=week_type,
                study_time=study_time,
                subject_number=ScheduleEntry.time_to_number(study_time),
                subject_type=subject_type,
                subgroup=subgroup,
                room=room
            )
            schedule_entry.employees.set(get_or_create_employees(employees))


def get_or_create_employees(employees: List[str]) -> List[Employee] | None:
    employee_objects = list()
    if not employees:
        return employee_objects

    for employee in employees:
        last_name, first_name, patronymic = parse_name(employee.split())
        emp_obj, _ = Employee.objects.get_or_create(
            first_name=first_name,
            patronymic=patronymic,
            last_name=last_name,
        )
        employee_objects.append(
            emp_obj
        )
    return employee_objects


def schedule_pages_count(url) -> int:
    try:
        resp = requests.get(url)
    except RequestException as e:
        logging.error(e)
        return 0

    if not resp.ok:
        logging.error(f'error while parsing {url}')
        return 0

    soup = BeautifulSoup(resp.text, 'lxml')
    return int(clear_data(
        soup.find(
            'ul', class_='pagination'
        ).contents,
        '\n', '', ' ', '›'
    )[-1])


def group_names_dict(url) -> dict:
    groups = dict()
    resp = requests.get(url)

    if not resp.ok:
        logging.warning(f'error while parsing {url}')
        return groups

    soup = BeautifulSoup(resp.text, 'lxml')
    cards = soup.find(
        'div',
        class_="kt-section__content kt-section__content--border"
    ).find_all('a', class_="kt-link")

    for a_el in cards:
        group_name = ''.join(a_el.get_text(strip=True).split())
        groups[group_name] = a_el.get('href')

    return groups
