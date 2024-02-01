import copy
import datetime
import random
import time
from typing import Optional

import requests


class Requester:
    def __init__(self, db: dict):
        self._db: dict = db
        self._session: Optional[requests.Session] = None
        self._user_agents = [
            'Mozilla/5.0 '
            '(Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/119.0.0.0 '
            'Safari/537.36',

            'Mozilla/5.0 '
            '(Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/121.0.0.0 '
            'Safari/537.36',

            'Mozilla/5.0 '
            '(Windows NT 10.0; Win64; x64; rv:100.0) '
            'Gecko/20100101 '
            'Firefox/100.0',

            'Mozilla/5.0 '
            '(Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) '
            'Version/15.0 '
            'Safari/605.1.15',

            'Mozilla/5.0 '
            '(Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 '
            'Safari/537.36',

            'Mozilla/5.0 '
            '(Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 '
            'Safari/537.36',

            'Mozilla/5.0 (Macintosh; '
            'Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/116.0.0.0 '
            'Safari/537.36',

            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/117.0.0.0 '
            'Safari/537.36',

            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/118.0.0.0 '
            'Safari/537.36',

            'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/108.0.0.0 '
            'Safari/537.36',

            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) '
            'Version/16.1 '
            'Safari/605.1.15',

            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) '
            'Version/16.1 '
            'Safari/605.1.15',

            'Googlebot/2.1 (+http://www.google.com/bot.html)'
        ]
        self._header_template: dict = {
            'connection': 'keep-alive',
            'accept-encoding': "gzip, deflate",
            'accept-language': 'ru-RU,ru;q=0.9,en-US,en;q=0.8',
        }
        self._current_headers: dict = {}
        self._sleep_timing = [0.1, 0.5, 1, 2, 3, 4, 5]

    def make_request(self, url: str) -> requests.Response:
        """"""

        if not self._session or not self._current_headers:
            self._session = requests.Session()
            self._make_headers()

        for i in range(10):
            time.sleep(random.choice(self._sleep_timing))
            try:
                response = self._session.get(url=url, headers=self._current_headers)
                return response
            except:
                error_msg = f'Seems like we have been blocked! Changing request-headers...'
                self._db['progress'][datetime.datetime.now().__str__()] = error_msg
                self._make_headers()
                self._session = requests.Session()

        error_msg = f'Can not make a request! Seems like HH does nt like us.'
        self._db['progress'][datetime.datetime.now().__str__()] = error_msg
        raise InterruptedError(error_msg)

    def _make_headers(self) -> None:
        """"""

        if not self._current_headers:
            self._current_headers = copy.deepcopy(self._header_template)
            self._current_headers['user-agent'] = random.choice(self._user_agents)
        else:
            self._select_new_user_agent()

    def _select_new_user_agent(self):
        """"""

        last_user_agent = self._current_headers['user-agent']
        new_user_agent = None

        new_user_agent_selected = False
        while not new_user_agent_selected:
            new_user_agent = random.choice(self._user_agents)
            if new_user_agent != last_user_agent:
                new_user_agent_selected = True

        self._current_headers['user-agent'] = new_user_agent
