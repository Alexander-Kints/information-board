import requests
from bs4 import BeautifulSoup, PageElement
from typing import List

def page_count_employee(url: str) -> int:
    resp = requests.get(url)

    if not resp.ok:
        return 0

    soup = BeautifulSoup(resp.text, 'lxml')
    pages_raw_data = soup.find('ul', class_='pagination-nav')
    pages = clear_data(pages_raw_data.contents, '', '...', '»')
    return int(pages[-1])

def clear_data(content: List[PageElement], *exclude_elements) -> List[str]:
    return list(
        filter(
            lambda s: s not in exclude_elements,
            map(
                lambda el: el.get_text(strip=True),
                content
            )
        )
    )

def parse_name(full_name: List[str]):
    last_name = full_name[0]
    first_name = full_name[1]

    if len(full_name) == 3:
        patronymic = full_name[2]
    elif len(full_name) == 4:
        patronymic = f'{full_name[2]} {full_name[3]}'
    else:
        patronymic = None

    return last_name, first_name, patronymic
