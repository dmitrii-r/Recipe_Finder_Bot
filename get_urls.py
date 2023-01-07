import json
import os

import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm


def get_urls():
    """Формирует список с доступными адресами страниц рецептов."""

    # Определяем список листов с которых будем собирать ссылки:
    # 0  http://www.topglobus.ru/kulinarnaja-kniga-recepty-online-kuchnja-vse
    # 1   http://www.topglobus.ru/kulinarnaja-kniga-recepty-online-kuchnja-vse?p=12&l=
    # 2   http://www.topglobus.ru/kulinarnaja-kniga-recepty-online-kuchnja-vse?p=24&l=
    #   ...
    # 25   http://www.topglobus.ru/kulinarnaja-kniga-recepty-online-kuchnja-vse?p=300&l=

    # Создаем необходимые переменные:
    all_urls = []
    number_of_pages = 26
    current_page = 0
    recipe_on_page = 12
    next_page_link = ''
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/105.0.0.0 Safari/537.36'
               }

    # Ищем доступные ссылки:
    for _ in tqdm(range(number_of_pages), desc='Поиск доступных адресов страниц рецептов', colour='#00ff00'):
        url = 'http://www.topglobus.ru/kulinarnaja-kniga-recepty-online-kuchnja-vse' + next_page_link
        current_page += recipe_on_page
        next_page_link = f'?p={current_page}&l='
        r = requests.get(url=url, headers=headers)
        src = r.text
        soup = BeautifulSoup(src, 'lxml')
        urls = soup.find('table').find_all('tr')
        for item in urls:
            tds = item.find('td')
            title = tds.find('a')
            if title:
                url = 'http://www.topglobus.ru/' + title.get('href')
                r = requests.head(url, headers=headers)
                if r.status_code == 200:
                    all_urls.append(url)

    # Создаем папку data если ее еще не существует:
    if not os.path.exists('data'):
        os.mkdir('data')

    # Записываем полученные ссылки в файл data/all_urls.json:
    with open("data/all_urls.json", "w") as file:
        json.dump(all_urls, file, indent=4, ensure_ascii=False)

    print(f'Всего добавлено адресов страниц рецептов: {len(all_urls)}')


if __name__ == '__main__':
    get_urls()
