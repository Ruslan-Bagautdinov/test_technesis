import asyncio
import re
import sqlite3

import pandas as pd
import requests
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters import Command
from loguru import logger
from lxml import html

from config import BOT_TOKEN

# Токен вашего бота
TOKEN = BOT_TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

logger.add("bot.log", rotation="500 MB", compression="zip")


def parse_price(url, xpath):
    logger.info(f"Parsing price from URL: {url} with XPath: {xpath}")
    response = requests.get(url)
    tree = html.fromstring(response.content)
    price_elements = tree.xpath(xpath)
    if not price_elements:
        logger.warning(f"No price elements found for URL: {url} with XPath: {xpath}")
        return None

    price_text = price_elements[0].text.strip()
    price_match = re.search(r'(\d+[\s\.,]*\d*)\s*(руб|\s*₽|$)', price_text)
    if price_match:
        price = price_match.group(1).replace(' ', '').replace(',', '.')
        logger.info(f"Parsed price: {price} from URL: {url}")
        return price
    logger.warning(f"No price match found for URL: {url} with XPath: {xpath}")
    return None


def calculate_average_price(df):
    logger.info("Calculating average price")
    prices = []
    for index, row in df.iterrows():
        price = parse_price(row['url'], row['xpath'])
        if price:
            prices.append(float(price))
    if prices:
        average_price = sum(prices) / len(prices)
        logger.info(f"Calculated average price: {average_price}")
        return average_price
    logger.warning("No prices found to calculate average")
    return None


async def save_file(file_id):
    logger.info(f"Saving file with ID: {file_id}")
    file = await bot.get_file(file_id)
    file_path = f"downloads/{file_id}.xlsx"
    await file.download(destination_file=file_path)
    logger.info(f"File saved to: {file_path}")
    return file_path


def process_file(file_path):
    logger.info(f"Processing file: {file_path}")
    df = pd.read_excel(file_path)
    logger.info(f"File processed, DataFrame shape: {df.shape}")
    return df


def create_database_and_table():
    logger.info("Creating database and table if they do not exist")
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
    logger.info("Database and table creation completed")


def save_to_db(df):
    logger.info("Saving DataFrame to database")
    try:
        with sqlite3.connect('sites.db') as conn:
            df.to_sql('sites', conn, if_exists='replace', index=False)
        logger.info("DataFrame saved to database successfully")
    except sqlite3.Error as e:
        logger.error(f'Database error: {e}')
        return str(e)
    return None


@dp.message(Command("start"))
async def start(message: types.Message):
    logger.info(f"Received /start command from user: {message.from_user.id}")
    await message.reply('Привет! Отправьте мне файл Excel для обработки.')


@dp.message(F.document.mime_type.in_(
    {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"}))
async def handle_document(message: types.Message):
    logger.info(f"Received document from user: {message.from_user.id}")
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
    logger.info("Starting bot")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
