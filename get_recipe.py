import csv
import json
import os
import re

import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm


def get_recipe():
    """Формирует список рецептов с полным описанием. Создает изображения рецептов."""

    # Открываем файл с адресами страниц рецептов:
    with open("data/all_urls.json") as file:
        all_urls = json.load(file)

    # Создаем папки для изображений:
    if not os.path.exists('data/images_small'):
        os.mkdir('data/images_small')
    if not os.path.exists('data/images_big'):
        os.mkdir('data/images_big')

    # Создаем необходимые переменные:
    name = 'name'
    title = 'title'
    description = 'description'
    ingredients = 'ingredients'
    technology = 'technology'
    group = 'group'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/105.0.0.0 Safari/537.36'
               }

    # Создаем файл для записи рецептов. Прописываем заголовки:
    with open(f"data/all_recipe.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(
            (
                name,
                title,
                description,
                ingredients,
                technology,
                group
            )
        )

    # Ищем данные на страницах:
    for url in tqdm(all_urls, desc='Поиск рецептов', colour='#00ff00'):
        r = requests.get(url=url, headers=headers)
        src = r.text
        soup = BeautifulSoup(src, 'lxml')

        # Определяем name:
        name = '_'.join(url.split('-')[2:])

        # Находим title:
        title = soup.find('table').find('h1').text

        # Находим description:
        description = [soup.find('table').find('h2').text, soup.find(text=re.compile('Время'))[2:],
                       soup.find(text=re.compile('Количество'))[2:]]

        # Находим ingredients:
        ingredients_table = soup.find(
            'table').find_next_sibling().find_next_sibling().find_next_sibling().find_next_sibling()
        items = str(ingredients_table)
        items = items[items.find('<a'):items.find('<br/><br/><font')].split('<br/>')
        ingredients = {}
        for item in items:
            ingredient = item[item.find('>'):item.find('</a>')].replace('>', '')
            amount = item[item.find('</a>'):].replace('</a>', '').replace(': ', '')\
                .replace('<em>', '').replace('</em>', '')
            ingredients[ingredient] = amount

        # Находим technology:
        technology = []
        for i in soup.find_all(color='green'):
            technology.append(i.next_element.next_element)

        # Находим group:
        group = soup.find('body').find('a').find_next_sibling().text[:-2]

        # Записываем найденные данные в файл:
        with open(f"data/all_recipe.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerow(
                (
                    name,
                    title,
                    description,
                    ingredients,
                    technology,
                    group
                )
            )

        # Находим и сохраняем изображения рецепта. Присваиваем изображениям имя соответствующее name рецепта:
        image_small = 'data/images_small/' + name + '.jpg'
        image_small_url = soup.find('table').find('img').get('src')
        image_url = 'http://www.topglobus.ru/' + image_small_url
        image_data = requests.get(image_url, verify=False).content
        with open(image_small, "wb") as handler:
            handler.write(image_data)

        image_big = 'data/images_big/' + name + '.jpg'
        image_big_url = image_small_url.replace('/m/', '/h/')
        image_url = 'http://www.topglobus.ru/' + image_big_url
        image_data = requests.get(image_url, verify=False).content
        with open(image_big, "wb") as handler:
            handler.write(image_data)

    print('Поиск завершен успешно.')


if __name__ == '__main__':
    get_recipe()
