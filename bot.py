import asyncio
import re
import sqlite3

import pandas as pd
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from loguru import logger
from lxml import html

from config import BOT_TOKEN

# Токен вашего бота
TOKEN = BOT_TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()


def parse_price(url, xpath):
    response = requests.get(url)
    tree = html.fromstring(response.content)
    price_elements = tree.xpath(xpath)
    if not price_elements:
        return None

    price_text = price_elements[0].text.strip()
    price_match = re.search(r'(\d+[\s\.,]*\d*)\s*(руб|\s*₽|$)', price_text)
    if price_match:
        return price_match.group(1).replace(' ', '').replace(',', '.')
    return None


def calculate_average_price(df):
    prices = []
    for index, row in df.iterrows():
        price = parse_price(row['url'], row['xpath'])
        if price:
            prices.append(float(price))
    return sum(prices) / len(prices) if prices else None


async def save_file(file_id):
    file = await bot.get_file(file_id)
    file_path = f"downloads/{file_id}.xlsx"
    await file.download(destination_file=file_path)
    return file_path


def process_file(file_path):
    df = pd.read_excel(file_path)
    return df


def create_database_and_table():
    with sqlite3.connect('sites.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                xpath TEXT NOT NULL
            )
        ''')
        conn.commit()


def save_to_db(df):
    try:
        with sqlite3.connect('sites.db') as conn:
            df.to_sql('sites', conn, if_exists='replace', index=False)
    except sqlite3.Error as e:
        logger.error(f'Database error: {e}')
        return str(e)
    return None


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply('Привет! Отправьте мне файл Excel для обработки.')


@dp.message(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    try:
        file_id = message.document.file_id
        file_path = await save_file(file_id)
        df = process_file(file_path)
        average_price = calculate_average_price(df)
        await message.reply(f'Средняя цена: {average_price}')

        db_error = save_to_db(df)
        if db_error:
            await message.reply(f'Произошла ошибка при сохранении в базу данных: {db_error}')
        else:
            await message.reply(f'Файл обработан и сохранен. Содержимое:\n{df.to_string()}')
    except Exception as e:
        logger.error(f'Error: {e}')
        await message.reply(f'Произошла ошибка: {e}')


async def main():
    create_database_and_table()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
