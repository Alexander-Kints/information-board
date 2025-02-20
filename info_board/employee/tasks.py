import requests
from bs4 import BeautifulSoup
from base64 import b64decode

url = 'https://www.pgups.ru/employee/?PAGEN_2=1&SIZEN_2=20'
resp = requests.get(url)
soup = BeautifulSoup(resp.text, 'lxml')

info_tables = soup.find_all('div', class_='table faculty')

# for pers in info_tables:
#     print(pers.find('a', class_='title').get_text(strip=True))

pers = info_tables[9]
full_name = pers.find('a', itemprop="fio").get_text(strip=True)
name_arr = full_name.split(' ')
# TODO full_name из 2 или 4 слов
last_name = name_arr[0]
first_name = name_arr[1]
patronymic = name_arr[2]
academic_degree = pers.find('dd', itemprop="Degree")
academic_status = pers.find('dd', itemprop="AcademStat")

positions = pers.find('dd', itemprop="post")
pos_arr = list()
if positions:
    items = list(filter(lambda s: s, map(lambda el: el.get_text(strip=True), positions.contents)))
    print(items)
    for item in ' '.join(items).split(' , '):
        print(item.strip())

print(first_name)
print(patronymic)
print(last_name)
print(academic_degree.get_text(strip=True) if academic_degree else None)
print(academic_status.get_text(strip=True) if academic_status else None)

phones = pers.find('div', itemprop='telephone')
if phones:
    items = list(filter(lambda s: s, map(lambda el: el.get_text(strip=True), phones.contents)))
    print(items)

email = pers.find('a', itemprop='e-mail')

print(b64decode(email.get_text(strip=True)).decode('utf-8') if email else None)

has_address = pers.find('i', class_='user-icon map')
if has_address:
    print(list(filter(lambda s: s != '\n', has_address.parent.parent.contents))[1].get_text(strip=True))
    address = has_address.parent.next_sibling
    # print(address.get_text(strip=True))
