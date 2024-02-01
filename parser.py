import datetime
import time

import bs4.element

from bs4 import BeautifulSoup

from request_maker import Requester


class Parser:
    """Responsible for parsing data

    Attributes:
        _requested_vacancy: Stores a string, representing requested vacancy ('GoLag developer')
        _items_on_page: How many vacancies to store on page (setting from HH)
        _base_url: Base URL to make initial search
        _db: DB emulation"""

    def __init__(self, requested_vacancy: str, db: dict, items_on_page: int = 20):
        self._requested_vacancy: str = requested_vacancy.replace(' ', '+').lower()
        self._items_on_page: int = items_on_page
        self._base_url = 'https://ekaterinburg.hh.ru/search/vacancy' \
                         '?L_save_area=true' \
                         '&text={requested_vacancy}' \
                         '&excluded_text=' \
                         '&area=113' \
                         '&salary=' \
                         '&currency_code=RUR' \
                         '&only_with_salary=true' \
                         '&experience=doesNotMatter&' \
                         'order_by=relevance' \
                         '&search_period=0' \
                         '&items_on_page={items_on_page}'
        self._db: dict = db
        self._requester: Requester = Requester(db)

    def parse_vacancies(self) -> list[dict]:
        """Parses HH and returns a list with dicts, where each dict is parse vacancy

        Returns:
            List of dictionaries with a job description based on a unique request"""

        url = self._base_url.format(
            requested_vacancy=self._requested_vacancy,
            items_on_page=self._items_on_page
        )

        last_page_number = self._find_last_available_page_number(url)
        parsed_vacancies = self._parse_vacancies(last_page_number, url)

        return parsed_vacancies

    def _find_last_available_page_number(self, url: str) -> int:
        """Finds out, how many pages available via pagination

        Returns:
            Last available page number"""

        hh_request = self._requester.make_request(url)
        hh_soup = BeautifulSoup(hh_request.text, 'html.parser')
        paginator = hh_soup.find_all('a', {'data-qa': 'pager-page'})  # Finding all link in paginator
        pages = []
        for i in paginator:
            pages.append(int(i.text))
        return pages[-1] if pages else 0

    def _extract_vacancy(self, vacancy: bs4.element.Tag) -> dict:
        """Extracts single vacancy from soup

        Args:
            vacancy: Tag (kinda like a piece of soup)
        Returns:
            dict with parsed vacancy"""

        vacancy_name = vacancy.find('span', {'class': 'serp-item__title'})
        title_vacancy = vacancy_name.text

        vacancy_link = vacancy.find('a', {'class': 'bloko-link'})
        vacancy_link = vacancy_link.get('href')

        company = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).text

        city = str(vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).text).split(',')[0]

        experience_div = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-work-experience'})

        # Check if the div is found before trying to access its text
        if experience_div:
            experience = experience_div.text
        else:
            experience = '---------'

        salary = vacancy.find('span', {'class': 'bloko-header-section-2'})
        salary = salary.text if salary else '---------'
        if salary != '---------':
            salary_from, salary_up_to, salary_currency = self._parse_salary(salary)
        else:
            salary_from = '---------'
            salary_up_to = '---------'
            salary_currency = '---------'

        return {'title': title_vacancy,
                'company': company.replace(u'\xa0', ' '),
                'city': city,
                'link': vacancy_link,
                'experience': experience,
                'salary_from': salary_from,
                'salary_up_to': salary_up_to,
                'salary_currency': salary_currency}

    def _parse_salary(self, input_string: str) -> tuple[str, str, str]:
        """Parses salary-string into 'from', 'up too', 'currency'

        Args:
            input_string: 'от 100 000 $'
        Returns:
            Tuple with ['от', '100000', '$']"""

        # Split the input string by space
        input_string = input_string.replace(' ', ' ')
        parts = input_string.split()

        parts = self._remove_spaces_in_salary(parts)

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

    def _remove_spaces_in_salary(self, string_parts: list[str]) -> list[str]:
        """Removes spaces from salary

        Args:
            string_parts: ['от', '1', '000', '$']
        Returns:
            ['от', '1000', '$']"""

        parts_formatted = []
        actual_salary = ''
        for part in string_parts:
            try:
                int(part)
                actual_salary += part
            except:
                if actual_salary:
                    parts_formatted.append(actual_salary)
                actual_salary = ''
                parts_formatted.append(part)

        return parts_formatted

    def _parse_vacancies(self, last_page: int, url: str) -> list[dict]:
        """Returns the search result for all vacancies on all pages

        Args:
            last_page: number of the last page from pagination
            url: url, used to make initial search
        Returns:
            list of dictionaries with job description"""

        self._add_record_to_progress(f'{last_page} pages to go...')

        parsed_vacancies = []
        for page_num in range(last_page):
            self._add_record_to_progress(f'Getting page {page_num}/{last_page}')

            single_pagination_page = f'{url}&page={page_num}'
            page = self._requester.make_request(single_pagination_page)
            page_soup = BeautifulSoup(page.text, 'html.parser')
            vacancies = page_soup.find_all('div', {'class': 'vacancy-serp-item__layout'})
            for vacancy in vacancies:
                parsed_vacancies.append(self._extract_vacancy(vacancy))

        return parsed_vacancies

    def _add_record_to_progress(self, record: str) -> None:
        """Saves some string into emulated DB

        Args:
            record: String to save"""

        current_dt = datetime.datetime.now().__str__()
        if current_dt in self._db['progress']:
            time.sleep(0.01)
            current_dt = datetime.datetime.now().__str__()
        self._db['progress'][current_dt] = record
