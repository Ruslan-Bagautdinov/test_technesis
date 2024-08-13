# Бот для добавления сайтов для парсинга цен на зюзюблики

Этот бот предназначен для упрощения процесса добавления новых сайтов для парсинга цен на зюзюблики. Пользователь может загрузить файл Excel с информацией о сайтах, и бот обработает этот файл, сохранит данные в локальную базу данных SQLite и выведет содержимое файла пользователю.

## Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/Ruslan-Bagautdinov/test_technesis.git
   cd test_technesis
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте токен бота:**
   Создайте файл `.env` в корне проекта и добавьте в него ваш токен:
   ```
   BOT_TOKEN=your_bot_token_here
   ```

## Использование

1. **Запустите бота:**
   ```bash
   python bot.py
   ```

2. **Отправьте боту файл Excel:**
   - Бот ожидает файл в формате `.xlsx` или `.xls`.
   - Файл должен содержать столбцы `title`, `url` и `xpath`, где `title` — название товара или услуги, `url` — это URL веб-сайта, а `xpath` — XPath выражение для извлечения цены.

3. **Получите результат:**
   - Бот сохранит файл, обработает его, сохранит данные в базу данных и отправит вам содержимое файла.

## Структура файла Excel

- **title**: Название товара или услуги.
- **url**: URL веб-сайта, с которого нужно извлечь цену.
- **xpath**: XPath выражение для извлечения цены с веб-сайта.

## Пример файла Excel

| title            | url                                      | xpath                                              |
|------------------|------------------------------------------|----------------------------------------------------|
| Зюзюблик 1      | https://example.com/product1             | //span[@class='price']                             |
| Зюзюблик 2      | https://example.com/product2             | //div[@class='product-price']/span                 |

## Логирование

- Бот использует библиотеку `loguru` для логирования. Логи сохраняются в файл `bot.log` с ротацией при достижении размера 10 МБ и сжатием в формате ZIP.

## База данных

- Бот создает базу данных `sites.db` и таблицу `sites` для хранения информации о сайтах и XPath выражениях.

## Обработка ошибок

- Бот обрабатывает ошибки и отправляет сообщения об ошибках пользователю.

## Задача со звездочкой

- Бот также вычисляет среднюю цену зюзюблика по каждому сайту и отправляет результат пользователю.

## Тестирование

Для тестирования функционала бота вы можете использовать файл `test_prices.xlsx`, который находится в корневой папке проекта. Загрузите этот файл в бота, чтобы увидеть, как он обрабатывает данные и вычисляет среднюю цену.

## Автор

- [Руслан Багаутдинов](https://github.com/Ruslan-Bagautdinov)