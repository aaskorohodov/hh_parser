import requests
from bs4 import BeautifulSoup

# HEADERS = {
#     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)' +
#                   'Chrome/96.0.4664.45 Safari/537.36'
# }
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}


def extract_max_page(url):
    """Находит в тексте запарсенной ссылки максимальное кол-во сгенерированных страниц с вакансиями
    Returns:
        максимальный номер страницы"""

    hh_request = requests.get(url, headers=HEADERS)
    hh_soup = BeautifulSoup(hh_request.text, 'html.parser')
    # Находим все ссылки в пагинаторе
    paginator = hh_soup.find_all('a', {'data-qa': 'pager-page'})
    pages = []
    for i in paginator:
        pages.append(int(i.text))  # Забираем текст ссылки
    return pages[-1] if pages else 0  # Максимальное число страниц с вакансиями


def extract_vacancy(vacancy):
    """
    Возвращает описание очередной вакансии
    :param vacancy: html-текст с описанием вакансии
    :return: словарь с описанием вакансии по ключам:
    'title' - название вакансии
    'company' - наименование работодателя
    'city' - местонахождение вакансии
    'link' - ссылка на подробное описание вакансии
    """

    name_vacancy = vacancy.find('span', {'class': 'serp-item__title'})
    title_vacancy = name_vacancy.text

    link_vacancy = vacancy.find('a', {'class': 'bloko-link'})
    link_vacancy = link_vacancy.get('href')

    company_vacancy = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).text

    city_vacancy = str(vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).text).split(',')[0]

    experience_div = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-work-experience'})

    # Check if the div is found before trying to access its text
    if experience_div:
        experience = experience_div.text
    else:
        experience = '---------'

    salary = vacancy.find('span', {'class': 'bloko-header-section-2'})
    salary = salary.text if salary else '---------'
    if salary != '---------':
        salary_from, salary_up_to, salary_currency = parse_salary(salary)
    else:
        salary_from = '---------'
        salary_up_to = '---------'
        salary_currency = '---------'

    return {'title': title_vacancy,
            'company': company_vacancy.replace(u'\xa0', ' '),
            'city': city_vacancy,
            'link': link_vacancy,
            'experience': experience,
            'salary_from': salary_from,
            'salary_up_to': salary_up_to,
            'salary_currency': salary_currency}


def parse_salary(input_string):
    # Split the input string by space
    input_string = input_string.replace(' ', ' ')
    parts = input_string.split()

    parts_formatted = []
    actual_salary = ''
    for part in parts:
        try:
            int(part)
            actual_salary += part
        except:
            if actual_salary:
                parts_formatted.append(actual_salary)
            actual_salary = ''
            parts_formatted.append(part)

    parts = parts_formatted

    # Initialize variables with empty strings
    from_value = ''
    up_to_value = ''
    currency = ''

    # Check the parts of the string and assign values accordingly
    if 'от' in parts:
        from_index = parts.index('от') + 1
        from_value = parts[from_index]

    if 'до' in parts:
        up_to_index = parts.index('до') + 1
        up_to_value = parts[up_to_index]

    if '-' in parts:
        hyphen_index = parts.index('-')
        from_value = parts[hyphen_index - 1] if not from_value else from_value
        up_to_value = parts[hyphen_index + 1]

    if '–' in parts:
        hyphen_index = parts.index('–')
        from_value = parts[hyphen_index - 1] if not from_value else from_value
        up_to_value = parts[hyphen_index + 1]

    # Find the currency in the last part of the string
    if parts:
        currency = parts[-1]

    return from_value.strip(), up_to_value.strip(), currency.strip()


def extract_jobs(last_page, url):
    """Возвращает результат поиска по всем вакансиям на всех страницах

    Args:
        url:
        last_page: максимальное число страниц с вакансиями
    Returns:
        список словарей с описанием вакансии"""

    jobs = []
    print(f'{last_page} pages to go...')
    for page_num in range(last_page):
        print(f'Getting page {page_num}')

        address = f'{url}&page={page_num}'
        page = requests.get(address, headers=HEADERS)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        vacancies = page_soup.find_all('div', {'class': 'vacancy-serp-item__layout'})
        for vacancy in vacancies:
            jobs.append(extract_vacancy(vacancy))
    return jobs


def get_all_jobs(inquiry):
    """Возвращает список вакансий по уникльному запросу

    Args:
        inquiry: текст запроса
    Returns:
        список словарей с описанием вакансии по уникальному запросу"""

    inquiry = inquiry.replace(' ', '+')
    # Упростим запрос и уберем лишние параметры
    # url = f'https://ekaterinburg.hh.ru/search/vacancy?text={inquiry}&salary=&ored_clusters=true&only_with_salary=true&area=113&hhtmFrom=vacancy_search_list&hhtmFromLabel=vacancy_search_line'
    url = f'https://ekaterinburg.hh.ru/search/vacancy?L_save_area=true&text={inquiry}&excluded_text=&area=113&salary=&currency_code=RUR&only_with_salary=true&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20'
    last_page = extract_max_page(url)

    return extract_jobs(last_page, url)
