import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from info import BOT_TOKEN
from aiogram.dispatcher.filters.state import State, StatesGroup
from bs4 import BeautifulSoup
import requests

# Токен вашого бота
API_TOKEN = BOT_TOKEN

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Створення станів для введення даних
class Form(StatesGroup):
    city = State()
    street = State()

# Обробник команди /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await Form.city.set()
    await message.reply("Введіть населений пункт:")

# Обробник введення населеного пункту
@dp.message_handler(state=Form.city)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text

    await Form.next()
    await message.reply("Введіть вулицю (або '-' якщо не потрібна):")

# Обробник введення вулиці
@dp.message_handler(state=Form.street)
async def process_street(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['street'] = message.text if message.text != '-' else None

    city = data['city']
    street = data['street']

    # Виконання запиту до сайту та парсинг результатів
    url = 'https://energy.volyn.ua/spozhyvacham/perervy-u-elektropostachanni/hrafik-vidkliuchen/#gsc.tab=0'
    response = requests.post(url, data={'formCity': city, 'formStreet': street})
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.select_one('table.gsc-results-table')

    if table:
            rows = table.find_all("tr")[1:]  # Пропускаємо заголовок таблиці
            results = []
            for row in rows:
                columns = row.find_all("td")
                if len(columns) >= 7:  # Переконайтеся, що кількість колонок відповідає очікуванням
                    district = columns[0].text.strip()
                    locality = columns[1].text.strip()
                    street_name = columns[2].text.strip()
                    date = columns[5].text.strip()
                    outage_times = columns[6].decode_contents().replace("<br/>", ", ").strip()

                    result = (
                        f"Населений пункт: {locality}\n"
                        f"Вулиця: {street_name}\n"
                        f"Дата відключення: {date}\n"
                        f"Години відключення: {outage_times}\n"
                        "----------------------------------------"
                    )
                    results.append(result)

            # Збереження результатів в файл
            project_dir = os.path.abspath(os.path.dirname(__file__))
            results_file = os.path.join(project_dir, 'results.txt')
            with open(results_file, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write(result + "\n")
            self.log(f"Results saved to {results_file}")
        else:
            self.log("No table found on the page.")

        if results:
            await message.reply("\n".join(results))
        else:
            await message.reply(f"Не знайдено результатів для {city}, {street or '-'}")
    else:
        await message.reply("Помилка при отриманні даних з сайту.")

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
