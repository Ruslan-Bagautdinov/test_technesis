import asyncio
import sqlite3

import pandas as pd
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from lxml import html

from config import BOT_TOKEN

# Токен вашего бота
TOKEN = BOT_TOKEN

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()


def parse_price(url, xpath):
    response = requests.get(url)
    tree = html.fromstring(response.content)
    price = tree.xpath(xpath)
    return price[0].text.strip() if price else None


def calculate_average_price(df):
    prices = []
    for index, row in df.iterrows():
        price = parse_price(row['url'], row['xpath'])
        if price:
            prices.append(float(price.replace(' ', '').replace('₽', '')))
    return sum(prices) / len(prices) if prices else None


async def save_file(file_id):
    file = await bot.get_file(file_id)
    file_path = f"downloads/{file_id}.xlsx"
    await file.download(destination_file=file_path)
    return file_path


def process_file(file_path):
    df = pd.read_excel(file_path)
    return df


def save_to_db(df):
    conn = sqlite3.connect('sites.db')
    df.to_sql('sites', conn, if_exists='replace', index=False)
    conn.close()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply('Привет! Отправьте мне файл Excel для обработки.')


@dp.message(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    file_id = message.document.file_id
    file_path = await save_file(file_id)
    df = process_file(file_path)
    average_price = calculate_average_price(df)
    await message.reply(f'Средняя цена: {average_price}')
    save_to_db(df)
    await message.reply(f'Файл обработан и сохранен. Содержимое:\n{df.to_string()}')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
