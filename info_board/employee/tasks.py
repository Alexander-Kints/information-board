import logging
import time
from base64 import b64decode
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.db import transaction
from requests.exceptions import RequestException

from info_board.config import main_config
from info_board.employee.models import Contact, Employee
from info_board.employee.utils import (clear_data, page_count_employee,
                                       parse_name)


@shared_task
def parse_employee_info():
    url = main_config.employee.parse_url
    pages_count = page_count_employee(url.format(1))

    for page_number in range(1, pages_count + 1):
        try:
            resp = requests.get(url.format(page_number))
        except RequestException as e:
            logging.error(
                f'fatal error while parsing employee: {e}'
            )
            return None

        if not resp.ok:
            logging.warning(
                f'url: {url}, page {page_number}, status: {resp.status_code}'
            )
            continue

        soup = BeautifulSoup(resp.text, 'lxml')
        info_tables = soup.find_all('div', class_='table faculty')
        if not info_tables:
            logging.warning(
                f'div table faculty not found on page {page_number}'
            )
            continue

        for table in info_tables:
            new_contacts = list()

            full_name = table.find(
                'a', itemprop='fio'
            ).get_text(strip=True).split(' ')
            last_name, first_name, patronymic = parse_name(full_name)

            academic_degree = table.find('dd', itemprop='Degree')
            if academic_degree:
                academic_degree = academic_degree.get_text(strip=True)

            academic_status = table.find('dd', itemprop='AcademStat')
            if academic_status:
                academic_status = academic_status.get_text(strip=True)

            positions = table.find('dd', itemprop='post')
            if positions:
                positions = clear_data(positions.contents, '')
                positions = [
                    item.strip() for item in ' '.join(positions).split(' , ')
                ]

            phones = table.find('div', itemprop='telephone')
            if phones:
                phones = clear_data(phones.contents, '')
                for phone in phones:
                    new_contacts.append(Contact(
                        contact_type=Contact.ContactType.PHONE,
                        value=phone
                    ))

            email = table.find('a', itemprop='e-mail')
            if email:
                email = b64decode(email.get_text(strip=True)).decode('utf-8')
                new_contacts.append(Contact(
                    contact_type=Contact.ContactType.EMAIL,
                    value=email
                ))

            address = table.find('i', class_='user-icon map')
            if address:
                address = clear_data(address.parent.parent.contents, '\n', '')
                address = address.pop() if address else None
                new_contacts.append(Contact(
                    contact_type=Contact.ContactType.ADDRESS,
                    value=address
                ))

            photo = table.find('img')
            if photo:
                photo = urljoin(
                    main_config.employee.base_photo_url,
                    photo.get('src')
                )
            else:
                photo = main_config.employee.default_photo

            try:
                with transaction.atomic():
                    employee, _ = Employee.objects.get_or_create(
                        first_name=first_name,
                        patronymic=patronymic,
                        last_name=last_name
                    )
                    employee.academic_degree = academic_degree
                    employee.academic_status = academic_status
                    employee.current_positions = positions
                    employee.photo = photo
                    employee.save()

                    employee.contacts.all().delete()
                    for contact in new_contacts:
                        contact.employee = employee
                        contact.save()
            except Exception as e:
                logging.error(f'url {url}, page {page_number}, error: {e}')
            else:
                logging.info(
                    f'updated employee: {first_name} {patronymic} {last_name}'
                )
        logging.info(f'page {page_number} was parsed')
        time.sleep(main_config.parse_delay_sec)
